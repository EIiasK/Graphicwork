from OpenGL.GL import *
import glm
from shader_compiler import init_shader_program

class Renderer:
    def __init__(self, scene):
        self.scene = scene

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        shader_program = init_shader_program()

        # 设置视图矩阵
        model = glm.mat4(1.0)  # 物体的模型矩阵
        view = self.scene.camera.get_view_matrix()
        projection = glm.perspective(glm.radians(self.scene.camera.fov), 1600 / 900, 0.1, 100.0)

        # 使用shader并传递矩阵
        shader = self.get_shader()
        # 将矩阵传递给着色器
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

        # 渲染场景中的物体
        self.scene.render()

    def get_shader(self):
        # 返回一个已经加载的shader程序
        pass
