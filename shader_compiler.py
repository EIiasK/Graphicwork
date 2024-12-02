from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

def load_shader_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def compile_shader(vertex_src, fragment_src):
    # 编译顶点着色器
    vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)

    # 编译片段着色器
    fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)

    # 链接着色器程序
    shader_program = compileProgram(vertex_shader, fragment_shader)

    return shader_program

def init_shader_program():
    # 读取 GLSL 文件内容
    vertex_shader_code = load_shader_code("Shader/shader.vert")
    fragment_shader_code = load_shader_code("Shader/shader.frag")

    # 编译并链接着色器
    shader_program = compile_shader(vertex_shader_code, fragment_shader_code)

    # 使用编译后的着色器程序
    glUseProgram(shader_program)

    # 获取 uniform 变量的位置并传递参数
    glUniform3f(glGetUniformLocation(shader_program, "lightPos"), 1.2, 1.0, 2.0)
    glUniform3f(glGetUniformLocation(shader_program, "viewPos"), 0.0, 0.0, 3.0)
    glUniform3f(glGetUniformLocation(shader_program, "lightColor"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(shader_program, "objectColor"), 1.0, 0.5, 0.31)

    return shader_program