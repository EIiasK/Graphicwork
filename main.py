import glfw
from OpenGL.GL import *
from camera import Camera
from scene import Scene
from controls import Controls
from renderer import Renderer

def main():
    # 初始化GLFW窗口
    if not glfw.init():
        raise Exception("GLFW初始化失败")

    # 请求调试上下文（可选）
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # glfw.window_hint(glfw.OPENGL_DEBUG_CONTEXT, GL_TRUE)  # 可选，移除调试上下文请求

    window = glfw.create_window(1600, 900, "airbase 3D", None, None)
    if not window:
        glfw.terminate()
        raise Exception("窗口创建失败")

    glfw.make_context_current(window)

    # 打印 OpenGL 信息以验证上下文
    print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
    print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
    print(f"Renderer: {glGetString(GL_RENDERER).decode()}")

    # 初始化渲染器、相机、场景和控制
    camera = Camera()
    scene = Scene(camera)
    renderer = Renderer(scene)
    controls = Controls(window, camera)
    glEnable(GL_DEPTH_TEST)  # 启用深度测试
    glEnable(GL_CULL_FACE)  # 启用背面剔除
    glCullFace(GL_BACK)  # 剔除背面
    glFrontFace(GL_CCW)  # 设置逆时针为正面

    # 加载模型
    scene.load_objects()

    # 渲染主循环
    while not glfw.window_should_close(window):
        # 处理用户输入
        controls.handle_input()

        # 更新场景和渲染
        scene.update()
        renderer.render()

        # 检查并打印OpenGL错误
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL Error: {error}")

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()

