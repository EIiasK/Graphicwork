# scene.py
from model import Model

class Scene:
    def __init__(self, camera):
        self.camera = camera
        # 加载 FBX 模型
        self.model = Model("D:/Programming/Project/Graphics/source/airport.fbx")  # 替换为你的模型路径

    def update(self):
        # 更新物体状态（如动画等）
        pass

    def render(self, shader_program):
        self.model.render(shader_program)

