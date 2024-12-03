# model.py
import pyassimp
from OpenGL.GL import *
import numpy as np
import ctypes
from PIL import Image
import os
import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Mesh:
    DEFAULT_TEXTURE_FILENAME = 'default_texture.png'

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
            # 如果指定的纹理文件不存在，使用默认纹理
            if not os.path.isfile(texture_path):
                logging.warning(f"纹理文件不存在: {texture_path}. 使用默认纹理。")
                texture_path = os.path.abspath(
                    os.path.join(os.path.dirname(texture_path), self.DEFAULT_TEXTURE_FILENAME))

            self.texture = self.load_texture(texture_path)
        else:
            # 使用默认纹理
            texture_path = os.path.abspath(
                os.path.join(self.directory, '..', 'textures', self.DEFAULT_TEXTURE_FILENAME))
            logging.info(f"未指定纹理。使用默认纹理: {texture_path}")
            self.texture = self.load_texture(texture_path)

    def load_texture(self, path):
        try:
            if not os.path.isfile(path):
                logging.error(f"纹理文件不存在: {path}")
                return None
            image = Image.open(path)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.convert("RGBA").tobytes()
        except Exception as e:
            logging.error(f"无法加载纹理图片 {path}: {e}")
            return None

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
        self.directory = os.path.dirname(file_path)  # 获取模型文件的目录
        self.load_model(file_path)

    def load_model(self, file_path):
        with pyassimp.load(file_path) as scene:
            if not scene:
                raise Exception(f"无法加载模型文件: {file_path}")

            # 打印场景中的纹理数量
            logging.info(f"Scene has {len(scene.textures)} embedded textures.")

            # 提取嵌入式纹理并保存为文件
            for i, texture in enumerate(scene.textures):
                # 将 numpy.ndarray 转换为字节串
                texture_bytes = texture.data.tobytes()

                # 判断纹理格式
                if texture_bytes.startswith(b'\211PNG\r\n\032\n'):
                    ext = 'png'
                elif texture_bytes.startswith(b'\xff\xd8'):
                    ext = 'jpg'
                else:
                    ext = 'bin'  # 未知格式

                texture_filename = f"embedded_texture_{i}.{ext}"
                texture_path = os.path.abspath(os.path.join(self.directory, '..', 'textures', texture_filename))
                with open(texture_path, 'wb') as f:
                    f.write(texture_bytes)
                logging.info(f"  Extracted embedded texture {i}: {texture_path}")

            for i, mesh in enumerate(scene.meshes):
                vertices = mesh.vertices
                normals = mesh.normals if mesh.normals is not None else np.zeros_like(vertices)

                # 调试输出：打印材质属性
                logging.info(f"\nProcessing mesh {i + 1} with {len(vertices)} vertices.")
                if mesh.material:
                    logging.info("Mesh has material. Properties:")
                    properties = mesh.material.properties
                    if len(properties) % 2 != 0:
                        logging.warning("  警告: 材质属性列表的长度不是偶数，可能存在不匹配的键值对。")

                    # 构建属性字典
                    prop_dict = {}
                    for j in range(0, len(properties) - 1, 2):
                        key = properties[j].lower()
                        value = properties[j + 1]
                        prop_dict[key] = value
                        logging.info(f"  Property: {properties[j]}, Value: {properties[j + 1]}")

                    # 处理最后一个属性（如果长度为奇数）
                    if len(properties) % 2 != 0:
                        key = properties[-1].lower()
                        value = None
                        prop_dict[key] = value
                        logging.info(f"  Property: {properties[-1]}, Value: {value}")
                else:
                    logging.info("Mesh has no material.")

                # 使用 mesh.texturecoords 获取纹理坐标
                texcoords = mesh.texturecoords[0][:, :2] if mesh.texturecoords is not None and len(
                    mesh.texturecoords) > 0 else np.zeros((len(vertices), 2))
                indices = mesh.faces.flatten()

                # 转换为 NumPy 数组
                vertices = np.array(vertices, dtype=np.float32)
                normals = np.array(normals, dtype=np.float32)
                texcoords = np.array(texcoords, dtype=np.float32)
                indices = np.array(indices, dtype=np.uint32)

                # 获取纹理路径
                texture_path = None
                if mesh.material and mesh.material.properties:
                    # 通过属性字典查找 'diffusecolor|file' 或 'file'
                    if 'diffusecolor|file' in prop_dict:
                        texture_file = prop_dict['diffusecolor|file']
                        # 查找提取的嵌入式纹理文件
                        texture_path_candidate = os.path.abspath(
                            os.path.join(self.directory, '..', 'textures', texture_file))
                        if os.path.isfile(texture_path_candidate):
                            texture_path = texture_path_candidate
                            logging.info(f"  Assigned embedded texture to mesh: {texture_path}")
                        else:
                            logging.error(f"  纹理文件不存在: {texture_path_candidate}")
                    elif 'file' in prop_dict:
                        texture_file = prop_dict['file']
                        texture_path_candidate = os.path.abspath(
                            os.path.join(self.directory, '..', 'textures', texture_file))
                        if os.path.isfile(texture_path_candidate):
                            texture_path = texture_path_candidate
                            logging.info(f"  Found diffuse texture (from 'file'): {texture_path}")
                        else:
                            logging.error(f"  纹理文件不存在: {texture_path_candidate}")
                    else:
                        logging.info("  没有找到 'DiffuseColor|file' 或 'file' 属性。")
                else:
                    logging.info("  No material properties found for this mesh.")

                if texture_path:
                    # 纹理文件存在，使用它
                    pass
                else:
                    logging.info("  No diffuse texture found for this mesh.")

                self.meshes.append(Mesh(vertices, normals, texcoords, indices, texture_path))

    def render(self, shader_program):
        for mesh in self.meshes:
            mesh.render(shader_program)

