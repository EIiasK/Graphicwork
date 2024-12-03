# renderer.py
from OpenGL.GL import *
from shader_compiler import init_simple_shader_program
import glm

class Renderer:
    def __init__(self, scene):
        self.scene = scene  # 保存传递进来的场景对象
        self.shader_program = init_simple_shader_program()  # 初始化简单的 shader program

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.0, 0.0, 0.0, 1.0)  # 设置背景为黑色

        glUseProgram(self.shader_program)  # 使用简单的 shader program

        # 禁用深度测试和背面剔除（因为只有一个简单的三角形）
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        # 不需要设置矩阵，因为简单的着色器直接使用顶点位置

        # 渲染场景中的物体（简单的三角形）
        self.scene.render()
