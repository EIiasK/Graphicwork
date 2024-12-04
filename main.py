# main.py
import glfw
from OpenGL.GL import *
from camera import Camera
from scene import Scene  # 修改为新实现的 Scene
from controls import Controls
from renderer import Renderer  # 修改为新实现的 Renderer
import time
import logging
from shader_compiler import init_shader_program

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # 初始化 GLFW 窗口
    if not glfw.init():
        logging.error("GLFW 初始化失败")
        return

    # 创建窗口
    window = glfw.create_window(1600, 900, "3D Model Loader", None, None)
    if not window:
        glfw.terminate()
        logging.error("窗口创建失败")
        return

    glfw.make_context_current(window)

    # 打印 OpenGL 信息
    logging.info(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
    logging.info(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
    logging.info(f"Renderer: {glGetString(GL_RENDERER).decode()}")

    # 初始化相机
    camera = Camera()

    # 初始化场景（新实现）
    scene = Scene(camera, gltf_path="D:/Programming/Project/Graphics/model/scene.gltf")

    # 初始化着色器
    shader_program = init_shader_program()  # 着色器的编译和链接保持不变

    # 使用着色器程序
    glUseProgram(shader_program)

    # 初始化 Renderer
    renderer = Renderer(scene, shader_program)

    # 初始化 Controls
    controls = Controls(window, camera)

    # 设置初始时间
    last_frame = glfw.get_time()

    # 启用深度测试
    glEnable(GL_DEPTH_TEST)

    # 主循环
    while not glfw.window_should_close(window):
        # 计算时间间隔
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        # 处理输入
        controls.handle_input(delta_time)

        # 更新场景
        scene.update()

        # 使用 Renderer 进行渲染
        renderer.render()

        # 检查并打印 OpenGL 错误wwdwd
        error = glGetError()
        if error != GL_NO_ERROR:
            logging.error(f"OpenGL Error: {error}")

        glfw.swap_buffers(window)
        glfw.poll_events()
        glClearColor(0.1, 0.1, 0.1, 1.0)  # 设置背景颜色（暗灰色）

    glfw.terminate()

if __name__ == "__main__":
    main()
