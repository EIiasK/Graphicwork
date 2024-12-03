# scene.py
from simple_triangle import SimpleTriangle

class Scene:
    def __init__(self, camera):
        self.objects = []
        self.camera = camera
        # 初始化简单的三角形对象
        self.simple_triangle = SimpleTriangle()

    def load_objects(self):
        # 此处可以保留原有的加载对象代码，但为了简化，我们只渲染简单的三角形
        pass

    def update(self):
        # 更新物体状态（如动画等）
        pass

    def render(self):
        # 渲染简单的三角形
        self.simple_triangle.render()
