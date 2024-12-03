# scene.py
import pyassimp
from OpenGL.GL import *
import numpy as np
from shader_compiler import init_shader_program
import glm

class Mesh:
    def __init__(self, vertices, normals, texcoords, indices):
        self.vertices = vertices
        self.normals = normals
        self.texcoords = texcoords
        self.indices = indices

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        self.setup_mesh()

    def setup_mesh(self):
        glBindVertexArray(self.vao)

        # 顶点缓冲区包含位置、法线和纹理坐标，交错存储
        interleaved_data = []
        for i in range(len(self.vertices) // 3):
            interleaved_data.extend(self.vertices[3*i:3*i+3])
            if len(self.normals) > 0:
                interleaved_data.extend(self.normals[3*i:3*i+3])
            if len(self.texcoords) > 0:
                interleaved_data.extend(self.texcoords[2*i:2*i+2])

        interleaved_data = np.array(interleaved_data, dtype=np.float32)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, interleaved_data.nbytes, interleaved_data, GL_STATIC_DRAW)

        # 索引缓冲区
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # 计算步幅
        stride = (3 + 3 + 2) * 4  # 位置 + 法线 + 纹理坐标，每个浮点数4字节

        # 位置属性
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # 法线属性
        if len(self.normals) > 0:
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
            glEnableVertexAttribArray(1)

        # 纹理坐标属性
        if len(self.texcoords) > 0:
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
            glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    def render(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)


class Scene:
    def __init__(self, camera):
        self.objects = []
        self.camera = camera
        self.shader_program = init_shader_program()  # 初始化 shader program

    def load_fbx_model(self, path):
        scene = pyassimp.load(path)
        if not scene.meshes:
            raise Exception(f"No meshes found in file: {path}")

        for mesh in scene.meshes:
            vertices = np.array(mesh.vertices, dtype=np.float32)
            normals = np.array(mesh.normals, dtype=np.float32)
            if len(mesh.texturecoords) > 0:
                texcoords = np.array(mesh.texturecoords[0], dtype=np.float32).flatten()
            else:
                texcoords = np.zeros(len(vertices) // 3 * 2, dtype=np.float32)  # 无纹理时默认值

            indices = np.array(mesh.faces, dtype=np.uint32).flatten()

            self.objects.append(Mesh(vertices, normals, texcoords, indices))

        pyassimp.release(scene)

    def load_objects(self):
        vertices = np.array([
            -0.5, -0.5, 0.0,
             0.5, -0.5, 0.0,
             0.0, 0.5, 0.0
        ], dtype=np.float32)

        indices = np.array([0, 1, 2], dtype=np.uint32)

        self.objects.append(Mesh(vertices, [], [], indices))

    def update(self):
        # 更新物体状态（如动画等）
        pass

    def render(self):
        # 渲染所有物体
        for obj in self.objects:
            obj.render()

