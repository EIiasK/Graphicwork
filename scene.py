from renderer import Renderer

class Scene:
    def __init__(self, camera):
        self.objects = []
        self.camera = camera

    def load_objects(self):
        # 加载模型、纹理等
        pass

    def update(self):
        # 更新物体状态、相机等
        pass

    def render(self):
        # 渲染所有物体
        for obj in self.objects:
            obj.render(self.camera)
