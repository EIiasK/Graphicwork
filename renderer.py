from OpenGL.GL import *
import glm
from shader_compiler import init_shader_program
from utils import *

class Renderer:
    def __init__(self, scene):
        self.scene = scene  # 保存传递进来的场景对象
        self.shader_program = init_shader_program()  # 初始化 shader program

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.0, 0.0, 0.0, 1.0)  # 设置背景为黑色
        glUseProgram(self.shader_program)  # 使用 shader program

        # 设置视图和投影矩阵
        view = self.scene.camera.get_view_matrix()
        projection = glm.perspective(glm.radians(self.scene.camera.fov), 1600 / 900, 0.1, 100.0)

        # 打印矩阵以调试
        # print_matrix(view, "View Matrix:")
        # print_matrix(projection, "Projection Matrix:")

        # 将矩阵传递到着色器
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"), 1, GL_FALSE,
                           glm.value_ptr(projection))

        # 设置模型矩阵（如果有多个物体，可能需要在这里设置不同的模型矩阵）
        model = glm.mat4(1.0)  # 例如，单位矩阵
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))

        # 渲染场景中的物体
        self.scene.render()
