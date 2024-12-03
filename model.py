# model.py
from pygltflib import GLTF2
from OpenGL.GL import *
import numpy as np
from PIL import Image
import os
import logging
import ctypes

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Mesh:
    DEFAULT_TEXTURE_FILENAME = 'default_texture.png'

    def __init__(self, vertices, normals, texcoords, indices, texture_path=None, directory=''):
        self.vertex_count = len(indices)
        self.directory = directory  # 用于加载默认纹理

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
        if texture_path and os.path.isfile(texture_path):
            self.texture = self.load_texture(texture_path)
        else:
            default_texture_path = os.path.join(self.directory, 'textures', self.DEFAULT_TEXTURE_FILENAME)
            logging.info(f"未指定纹理或纹理文件不存在。使用默认纹理: {default_texture_path}")
            self.texture = self.load_texture(default_texture_path)

    def load_texture(self, path):
        try:
            image = Image.open(path)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.convert("RGBA").tobytes()
            width, height = image.size
        except Exception as e:
            logging.error(f"无法加载纹理图片 {path}: {e}")
            return None

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
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
        self.directory = os.path.dirname(file_path)
        self.processed_nodes = set()  # 用于跟踪已处理的节点，防止重复处理
        self.load_model(file_path)

    def load_model(self, file_path):
        gltf = GLTF2().load(file_path)

        # 提取纹理路径
        textures = {}
        for i, texture in enumerate(gltf.textures):
            image = gltf.images[texture.source]
            if image.uri:
                texture_path = os.path.join(self.directory, image.uri.replace('\\', os.sep).replace('/', os.sep))
                textures[i] = texture_path
                logging.info(f"  Extracted texture {i}: {texture_path}")
            else:
                # 处理嵌入式纹理（如果使用 .glb）
                buffer_view = gltf.bufferViews[image.bufferView]
                buffer = gltf.buffers[buffer_view.buffer]
                buffer_path = os.path.join(self.directory, buffer.uri.replace('\\', os.sep).replace('/', os.sep))
                if not os.path.isfile(buffer_path):
                    logging.error(f"  嵌入式纹理的缓冲区文件不存在: {buffer_path}")
                    continue
                with open(buffer_path, 'rb') as f:
                    f.seek(buffer_view.byteOffset)
                    data = f.read(buffer_view.byteLength)
                # 假设嵌入式纹理为PNG
                texture_filename = f"embedded_texture_{i}.png"
                texture_path = os.path.join(self.directory, 'textures', texture_filename)
                with open(texture_path, 'wb') as tex_file:
                    tex_file.write(data)
                textures[i] = texture_path
                logging.info(f"  Extracted embedded texture {i}: {texture_path}")

        # 遍历场景中的所有节点
        for scene in gltf.scenes:
            for node in scene.nodes:
                self.process_node(node, gltf, textures)

    def process_node(self, node_index, gltf, textures):
        if node_index in self.processed_nodes:
            return  # 已处理过此节点，跳过
        self.processed_nodes.add(node_index)

        node = gltf.nodes[node_index]
        if node.mesh is not None:
            mesh = gltf.meshes[node.mesh]
            for primitive in mesh.primitives:
                self.process_primitive(primitive, gltf, textures)
        if node.children:
            for child in node.children:
                self.process_node(child, gltf, textures)

    def process_primitive(self, primitive, gltf, textures):
        # 提取顶点位置
        positions = self.get_accessor_data(primitive.attributes.POSITION, gltf)
        logging.info(f"  Positions count: {len(positions)}")
        if positions.size == 0:
            logging.warning("  Primitive 缺少 POSITION 数据。跳过此 primitive。")
            return

        # 提取法线
        normals = self.get_accessor_data(primitive.attributes.NORMAL,
                                         gltf) if primitive.attributes.NORMAL is not None else np.zeros_like(positions)
        logging.info(f"  Normals count: {len(normals)}")

        # 提取纹理坐标
        texcoords = self.get_accessor_data(primitive.attributes.TEXCOORD_0,
                                           gltf) if primitive.attributes.TEXCOORD_0 is not None else np.zeros(
            (len(positions), 2), dtype=np.float32)
        logging.info(f"  Texcoords count: {len(texcoords)}")

        # 提取索引
        indices = self.get_accessor_data(primitive.indices, gltf)
        logging.info(f"  Indices count: {len(indices)}")
        if indices.size == 0:
            logging.warning("  Primitive 缺少索引数据。跳过此 primitive。")
            return

        # 确保顶点、法线和纹理坐标的长度一致
        num_vertices = len(positions)

        if len(normals) != num_vertices:
            logging.warning(f"  法线数量 ({len(normals)}) 与顶点数量 ({num_vertices}) 不匹配。使用默认法线。")
            normals = np.zeros_like(positions)

        if len(texcoords) != num_vertices:
            logging.warning(f"  纹理坐标数量 ({len(texcoords)}) 与顶点数量 ({num_vertices}) 不匹配。使用默认纹理坐标。")
            texcoords = np.zeros((num_vertices, 2), dtype=np.float32)

        # 提取纹理路径
        texture_path = None
        if primitive.material is not None:
            material = gltf.materials[primitive.material]
            if material.pbrMetallicRoughness and material.pbrMetallicRoughness.baseColorTexture:
                texture_index = material.pbrMetallicRoughness.baseColorTexture.index
                texture_path = textures.get(texture_index, None)
                if texture_path and not os.path.isfile(texture_path):
                    logging.warning(f"  纹理文件不存在: {texture_path}. 使用默认纹理。")
                    texture_path = os.path.join(self.directory, 'textures', Mesh.DEFAULT_TEXTURE_FILENAME)
        else:
            logging.info("  Primitive 无材质。使用默认纹理。")
            texture_path = os.path.join(self.directory, 'textures', Mesh.DEFAULT_TEXTURE_FILENAME)

        # 创建 Mesh 实例
        self.meshes.append(Mesh(positions, normals, texcoords, indices, texture_path, self.directory))

    def get_accessor_data(self, accessor_index, gltf):
        accessor = gltf.accessors[accessor_index]
        buffer_view = gltf.bufferViews[accessor.bufferView]
        buffer = gltf.buffers[buffer_view.buffer]

        # 读取二进制数据
        buffer_path = os.path.join(self.directory, buffer.uri.replace('\\', os.sep).replace('/', os.sep))
        if not os.path.isfile(buffer_path):
            logging.error(f"  缓冲区文件不存在: {buffer_path}")
            return np.array([])

        with open(buffer_path, 'rb') as f:
            f.seek(buffer_view.byteOffset)
            data = f.read(buffer_view.byteLength)

        # 根据 accessor.componentType 和 accessor.type 解析数据，并考虑 byteStride
        component_type = accessor.componentType
        accessor_type = accessor.type
        count = accessor.count

        type_count = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4, 'MAT3': 9, 'MAT4': 16}
        component_type_dtype = {
            5120: np.int8,  # BYTE
            5121: np.uint8,  # UNSIGNED_BYTE
            5122: np.int16,  # SHORT
            5123: np.uint16,  # UNSIGNED_SHORT
            5125: np.uint32,  # UNSIGNED_INT
            5126: np.float32,  # FLOAT
        }

        if accessor_type not in type_count or component_type not in component_type_dtype:
            logging.warning(f"Unsupported accessor type: {accessor_type} or componentType: {component_type}")
            return np.array([])

        dtype = component_type_dtype[component_type]
        num_components = type_count[accessor_type]

        # Calculate expected element size
        element_size = num_components * dtype().nbytes

        # Handle byteStride
        byte_stride = buffer_view.byteStride
        logging.info(
            f"  Accessor {accessor_index}: type={accessor_type}, componentType={component_type}, count={count}, byteStride={byte_stride}")

        if accessor_type == 'SCALAR':
            # 对于 SCALAR 类型，忽略 byteStride，假定数据是紧凑排列的
            array = np.frombuffer(data, dtype=dtype, count=count)
            logging.info(f"  Accessor {accessor_index}: SCALAR data read with shape ({count},)")
        elif byte_stride is None:
            # 紧凑排列
            array = np.frombuffer(data, dtype=dtype)
            try:
                array = array.reshape((count, num_components))
                logging.info(f"  Accessor {accessor_index}: Data reshaped to {array.shape}")
            except ValueError as e:
                logging.error(f"Reshape error for accessor {accessor_index}: {e}")
                return np.array([])
        else:
            # Strided 数据
            stride = byte_stride
            array = np.empty((count, num_components), dtype=dtype)
            for i in range(count):
                start = i * stride
                end = start + element_size
                if end > len(data):
                    logging.warning(f"Data overflow while reading accessor {accessor_index} at element {i}")
                    break
                element = np.frombuffer(data[start:end], dtype=dtype, count=num_components)
                if len(element) != num_components:
                    logging.warning(f"Incomplete data for accessor {accessor_index} at element {i}")
                    break
                array[i] = element
            logging.info(f"  Accessor {accessor_index}: Strided data reshaped to {array.shape}")

        return array

    def render(self, shader_program):
        for mesh in self.meshes:
            mesh.render(shader_program)
