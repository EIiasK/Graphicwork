# model.py
import pyassimp
from OpenGL.GL import *
import numpy as np
import glm
import ctypes
from PIL import Image


class Mesh:
    def __init__(self, vertices, normals, texcoords, indices, texture_path=None):
        self.vertex_count = len(indices)

        # 创建并绑定 VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # 创建 VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # Interleave vertices, normals, texcoords
        vertex_data = np.hstack((vertices, normals, texcoords)).astype(np.float32)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        # 创建 EBO
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        stride = 8 * ctypes.sizeof(ctypes.c_float)  # 3 (position) + 3 (normal) + 2 (texcoord) = 8 floats

        # 位置属性
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # 法线属性
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        # 纹理坐标属性
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        # 解绑 VBO 和 VAO
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # 加载纹理
        if texture_path:
            self.texture = self.load_texture(texture_path)
        else:
            self.texture = None

    def load_texture(self, path):
        image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        # 设置纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glBindTexture(GL_TEXTURE_2D, 0)
        return texture

    def render(self, shader_program):
        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            # 假设着色器中的 sampler2D uniform 名为 "texture_diffuse1"
            glUniform1i(glGetUniformLocation(shader_program, "texture_diffuse1"), 0)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.vertex_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        if self.texture:
            glBindTexture(GL_TEXTURE_2D, 0)


class Model:
    def __init__(self, file_path):
        self.meshes = []
        self.load_model(file_path)

    def load_model(self, file_path):
        with pyassimp.load(file_path) as scene:
            if not scene:
                raise Exception(f"无法加载模型文件: {file_path}")

            for mesh in scene.meshes:
                vertices = mesh.vertices
                normals = mesh.normals if mesh.normals is not None else np.zeros_like(vertices)
                texcoords = mesh.texturecoords[0][:, :2] if mesh.texturecoords and len(
                    mesh.texturecoords) > 0 else np.zeros((len(vertices), 2))
                indices = mesh.faces.flatten()

                # 转换为 NumPy 数组
                vertices = np.array(vertices, dtype=np.float32)
                normals = np.array(normals, dtype=np.float32)
                texcoords = np.array(texcoords, dtype=np.float32)
                indices = np.array(indices, dtype=np.uint32)

                # 获取纹理路径（假设纹理在 mesh.material 中）
                texture_path = None
                if mesh.material and mesh.material.properties:
                    for prop in mesh.material.properties:
                        if prop.key == "!$tex.file" and prop.semantic == 1:
                            texture_path = prop.data
                            break

                self.meshes.append(Mesh(vertices, normals, texcoords, indices, texture_path))

    def render(self, shader_program):
        for mesh in self.meshes:
            mesh.render(shader_program)
