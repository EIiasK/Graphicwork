from OpenGL.GL import *
import glm
import logging


class Renderer:
    def __init__(self, scene, shader_program):
        self.scene = scene
        self.shader_program = shader_program
        logging.info("Renderer 已初始化")

    def render(self):
        """渲染当前场景"""
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # 清理缓冲区
        glUseProgram(self.shader_program)

        # 获取视图矩阵和投影矩阵
        view_matrix = self.scene.camera.get_view_matrix()
        projection_matrix = glm.perspective(
            glm.radians(self.scene.camera.fov),
            1600 / 900,  # 假设窗口宽高比
            0.1, 100.0
        )

        view_loc = glGetUniformLocation(self.shader_program, "view")
        projection_loc = glGetUniformLocation(self.shader_program, "projection")

        if view_loc != -1:
            glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view_matrix))
        if projection_loc != -1:
            glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(projection_matrix))

        for vao, count, transform, texture_id in self.scene.meshes:
            # 设置模型矩阵
            model_loc = glGetUniformLocation(self.shader_program, "model")
            if model_loc != -1:
                glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(transform))

            # 绑定纹理（如果有）
            if texture_id is not None:
                texture_loc = glGetUniformLocation(self.shader_program, "texture1")
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                if texture_loc != -1:
                    glUniform1i(texture_loc, 0)

            # 绘制网格
            glBindVertexArray(vao)
            glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        glUseProgram(0)
        # logging.info("场景渲染完成")

