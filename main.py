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

    window = glfw.create_window(1600, 900, "airbase 3D", None, None)
    if not window:
        glfw.terminate()
        raise Exception("窗口创建失败")

    glfw.make_context_current(window)

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

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
