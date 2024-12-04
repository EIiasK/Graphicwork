from camera import Camera
from model import Model  # 引入 Model 类

class Scene:
    def __init__(self, camera, gltf_path):
        self.camera = camera
        # 加载模型数据
        self.model = Model(gltf_path)

    def update(self):
        """更新场景逻辑"""
        pass

    @property
    def meshes(self):
        """提供模型网格数据供 Renderer 使用"""
        return [
            (mesh.vao, mesh.vertex_count, mesh.model_matrix, mesh.texture)
            for mesh in self.model.meshes
        ]
