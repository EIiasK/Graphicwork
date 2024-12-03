# renderer.py
from OpenGL.GL import *
import glm
from shader_compiler import init_shader_program
from utils import print_matrix

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

        # 将矩阵传递到着色器
        view_loc = glGetUniformLocation(self.shader_program, "view")
        projection_loc = glGetUniformLocation(self.shader_program, "projection")
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(projection))

        # 设置模型矩阵
        model = glm.mat4(1.0)  # 使用单位矩阵或根据需要进行变换
        model_loc = glGetUniformLocation(self.shader_program, "model")
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))

        # 检查并打印OpenGL错误
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL Error before rendering objects: {error}")

        # 渲染场景中的物体
        self.scene.render()

        # 检查并打印OpenGL错误
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL Error after rendering objects: {error}")
