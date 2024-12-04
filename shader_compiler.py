# shader_compiler.py
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

def load_shader_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def compile_shader(vertex_src, fragment_src):
    try:
        vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
    except RuntimeError as e:
        print("顶点着色器编译失败:")
        print(e)
        raise

    try:
        fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
    except RuntimeError as e:
        print("片段着色器编译失败:")
        print(e)
        raise

    try:
        shader_program = compileProgram(vertex_shader, fragment_shader)
    except RuntimeError as e:
        print("着色器程序链接失败:")
        print(e)
        raise

    return shader_program

def init_shader_program():
    # 读取简单的 GLSL 文件内容
    vertex_shader_code = load_shader_code("Shader/shader.vert")
    fragment_shader_code = load_shader_code("Shader/shader.frag")

    # 编译并链接着色器
    shader_program = compile_shader(vertex_shader_code, fragment_shader_code)

    return shader_program
