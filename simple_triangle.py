# simple_triangle.py
import numpy as np
from OpenGL.GL import *

class SimpleTriangle:
    def __init__(self):
        # 定义简单的三角形顶点数据
        self.vertices = np.array([
            -0.5, -0.5, 0.0,  # 左下角
             0.5, -0.5, 0.0,  # 右下角
             0.0,  0.5, 0.0   # 顶部
        ], dtype=np.float32)

        # 生成 VAO 和 VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # 设置顶点属性指针
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def render(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)
