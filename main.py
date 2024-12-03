# main.py
import glfw
from OpenGL.GL import *
from camera import Camera
from scene import Scene
from controls import Controls
from renderer import Renderer
import time

def main():
    # 初始化 GLFW 窗口
    if not glfw.init():
        raise Exception("GLFW 初始化失败")

    # 创建窗口
    window = glfw.create_window(1600, 900, "Simple Triangle", None, None)
    if not window:
        glfw.terminate()
        raise Exception("窗口创建失败")

    glfw.make_context_current(window)

    # 打印 OpenGL 信息
    print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
    print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
    print(f"Renderer: {glGetString(GL_RENDERER).decode()}")

    # 初始化相机
    camera = Camera()

    # 初始化场景
    scene = Scene(camera)

    # 初始化渲染器
    renderer = Renderer(scene)

    # 初始化控制
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

        # 渲染
        renderer.render()

        # 检查并打印 OpenGL 错误
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL Error: {error}")

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
