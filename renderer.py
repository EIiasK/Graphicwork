# renderer.py
from OpenGL.GL import *
import glm
from shader_compiler import init_simple_shader_program
from model import Model
import logging
import numpy as np


class Renderer:
    def __init__(self, scene):
        self.scene = scene
        self.shader_program = init_simple_shader_program()

        # 使用着色器程序
        glUseProgram(self.shader_program)

        # 设置光源参数
        glUniform3f(glGetUniformLocation(self.shader_program, "lightPos"), 1.2, 1.0, 2.0)
        glUniform3f(glGetUniformLocation(self.shader_program, "lightColor"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(self.shader_program, "objectColor"), 1.0, 1.0, 1.0)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        glUseProgram(self.shader_program)
        glEnable(GL_DEPTH_TEST)

        # 获取相机的视图矩阵
        view = self.scene.camera.get_view_matrix()

        # 设置投影矩阵
        projection = glm.perspective(glm.radians(self.scene.camera.fov), 1600 / 900, 0.1, 500.0)


        # 获取 uniform 位置
        view_loc = glGetUniformLocation(self.shader_program, "view")
        proj_loc = glGetUniformLocation(self.shader_program, "projection")
        view_pos_loc = glGetUniformLocation(self.shader_program, "viewPos")

        # 传递视图和投影矩阵到着色器
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))

        # 传递相机位置到着色器
        glUniform3f(view_pos_loc, self.scene.camera.position.x, self.scene.camera.position.y,
                    self.scene.camera.position.z)


        # 遍历所有 meshes 并渲染
        for mesh in self.scene.model.meshes:

            # 传递模型矩阵到着色器
            model_loc = glGetUniformLocation(self.shader_program, "model")
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(mesh.model_matrix))
            print("Model Matrix for mesh:", glm.value_ptr(mesh.model_matrix))
            print("Shader Uniform Locations - Model:", model_loc, "View:", view_loc, "Projection:", proj_loc)
            # 渲染网格
            mesh.render(self.shader_program)
