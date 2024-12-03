# renderer.py
from OpenGL.GL import *
import glm
from shader_compiler import init_simple_shader_program

class Renderer:
    def __init__(self, scene):
        self.scene = scene
        self.shader_program = init_simple_shader_program()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        glUseProgram(self.shader_program)
        glEnable(GL_DEPTH_TEST)

        # 设置模型矩阵
        model = glm.mat4(1.0)  # 单位矩阵

        # 使用相机的视图矩阵
        view = self.scene.camera.get_view_matrix()

        # 设置投影矩阵
        projection = glm.perspective(glm.radians(self.scene.camera.fov), 1600 / 900, 0.1, 100.0)

        # 获取 uniform 位置
        model_loc = glGetUniformLocation(self.shader_program, "model")
        view_loc = glGetUniformLocation(self.shader_program, "view")
        proj_loc = glGetUniformLocation(self.shader_program, "projection")

        # 传递矩阵到着色器
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))

        # 打印相机位置（调试）
        print(f"Camera Position: {self.scene.camera.position}")

        # 渲染场景中的物体
        self.scene.render()
