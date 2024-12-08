# model.py
from pygltflib import GLTF2
from OpenGL.GL import *
import numpy as np
from PIL import Image
import os
import logging
import ctypes
import glm
import base64


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Mesh:
    DEFAULT_TEXTURE_FILENAME = 'default_texture.png'

    def __init__(self, vertices, normals, texcoords, indices, texture_path=None, directory='', model_matrix=glm.mat4(1.0)):
        self.model_matrix = model_matrix  # glm.mat4 对象
        self.vertex_count = len(indices)
        self.directory = directory
        self.vao = self.create_vao(vertices, normals, texcoords, indices)
        self.texture = self.load_texture(texture_path or self.default_texture_path())

    def create_vao(self, vertices, normals, texcoords, indices):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        vertex_data = np.hstack((vertices, normals, texcoords)).astype(np.float32)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        stride = 8 * ctypes.sizeof(ctypes.c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)
        return vao

    def load_texture(self, path):
        if not os.path.isfile(path):
            logging.warning(f"纹理文件缺失: {path}")
            return None
        image = Image.open(path)
        img_data = image.convert("RGBA").tobytes()
        width, height = image.size
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        return texture

    def default_texture_path(self):
        return os.path.join(self.directory, 'textures', self.DEFAULT_TEXTURE_FILENAME)

    def render(self, shader_program):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.vertex_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)


class Model:
    def __init__(self, file_path):
        self.meshes = []
        self.directory = os.path.dirname(file_path)
        self.gltf = GLTF2().load(file_path)
        self.textures = self.extract_textures()
        self.process_scenes()

    def extract_textures(self):
        textures = {}
        for idx, texture in enumerate(self.gltf.textures):
            image = self.gltf.images[texture.source]
            if image.uri:
                textures[idx] = os.path.join(self.directory, image.uri)
            else:
                logging.warning(f"嵌入式纹理尚未处理: {texture}")
        return textures

    def process_scenes(self):
        for scene in self.gltf.scenes:
            for node_index in scene.nodes:
                self.process_node(node_index, glm.mat4(1.0))

    def process_node(self, node_index, parent_transform):
        node = self.gltf.nodes[node_index]
        local_transform = glm.mat4(1.0)
        if node.matrix:
            local_transform = glm.mat4(*node.matrix)
        else:
            translation = node.translation or [0.0, 0.0, 0.0]
            rotation = node.rotation or [0.0, 0.0, 0.0, 1.0]
            scale = node.scale or [1.0, 1.0, 1.0]
            local_transform = (
                glm.translate(glm.mat4(1.0), glm.vec3(*translation)) *
                glm.mat4_cast(glm.quat(*rotation)) *
                glm.scale(glm.mat4(1.0), glm.vec3(*scale))
            )
        global_transform = parent_transform * local_transform

        if node.mesh is not None:
            self.process_mesh(self.gltf.meshes[node.mesh], global_transform)

        for child_index in node.children or []:
            self.process_node(child_index, global_transform)

    def process_mesh(self, mesh, transform):
        for primitive in mesh.primitives:
            positions = self.get_accessor_data(primitive.attributes.POSITION)
            normals = self.get_accessor_data(primitive.attributes.NORMAL)
            if normals is None or normals.size == 0:  # 检查是否为空或未定义
                normals = np.zeros_like(positions)
            texcoords = self.get_accessor_data(primitive.attributes.TEXCOORD_0)
            if texcoords is None or texcoords.size == 0:  # 检查是否为空或未定义
                texcoords = np.zeros((len(positions), 2))
            indices = self.get_accessor_data(primitive.indices)
            if indices is None or indices.size == 0:  # 检查是否为空或未定义
                indices = np.arange(len(positions))
            texture_path = self.get_material_texture_path(primitive.material)
            self.meshes.append(Mesh(positions, normals, texcoords, indices, texture_path, self.directory, transform))
            logging.info(f"Mesh Loaded: {len(positions)} vertices, {len(indices)} indices")
            logging.info(f"Normals: {normals.shape}, TexCoords: {texcoords.shape}")

    def get_accessor_data(self, accessor_idx):
        accessor = self.gltf.accessors[accessor_idx]
        buffer_view = self.gltf.bufferViews[accessor.bufferView]
        buffer = self.gltf.buffers[buffer_view.buffer]

        # 加载 Buffer 数据
        if buffer.uri.startswith("data:"):
            # 处理嵌入式 base64 数据
            header, base64_data = buffer.uri.split(",", 1)
            buffer_data = base64.b64decode(base64_data)
        else:
            # 加载外部文件
            buffer_path = os.path.join(self.directory, buffer.uri)
            with open(buffer_path, 'rb') as f:
                buffer_data = f.read()

        byte_offset = (buffer_view.byteOffset or 0) + (accessor.byteOffset or 0)

        # 更新 dtype 映射，支持更多类型
        component_type_map = {
            5120: np.int8,  # BYTE
            5121: np.uint8,  # UNSIGNED_BYTE
            5122: np.int16,  # SHORT
            5123: np.uint16,  # UNSIGNED_SHORT
            5125: np.uint32,  # UNSIGNED_INT
            5126: np.float32  # FLOAT
        }

        dtype = component_type_map.get(accessor.componentType)
        if dtype is None:
            raise ValueError(f"Unsupported accessor componentType: {accessor.componentType}")

        count = accessor.count * {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[accessor.type]

        # 从 Buffer 数据中提取内容
        return np.frombuffer(buffer_data, dtype=dtype, count=count, offset=byte_offset).reshape((accessor.count, -1))

    def get_material_texture_path(self, material_index):
        if material_index is None:
            return None
        material = self.gltf.materials[material_index]
        texture_index = material.pbrMetallicRoughness.baseColorTexture.index
        return self.textures.get(texture_index)
