# main.py
import glfw
from OpenGL.GL import *
from camera import Camera
from scene import Scene
from controls import Controls
from renderer import Renderer

def main():
    # 初始化 GLFW 窗口
    if not glfw.init():
        raise Exception("GLFW 初始化失败")

    # 创建窗口
    window = glfw.create_window(800, 600, "Simple Triangle", None, None)
    if not window:
        glfw.terminate()
        raise Exception("窗口创建失败")

    glfw.make_context_current(window)

    # 打印 OpenGL 信息
    print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
    print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
    print(f"Renderer: {glGetString(GL_RENDERER).decode()}")

    # 初始化渲染器、相机、场景和控制
    camera = Camera()
    scene = Scene(camera)
    renderer = Renderer(scene)
    controls = Controls(window, camera)

    # 主循环
    while not glfw.window_should_close(window):
        # 处理用户输入（此处可以简化或注释掉 controls.handle_input()）
        # controls.handle_input()

        # 更新场景和渲染
        scene.update()
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
