import glfw

class Controls:
    def __init__(self, window, camera):
        self.window = window
        self.camera = camera

    def handle_input(self):
        # 键盘控制相机
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.process_keyboard('FORWARD', 0.1)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.process_keyboard('BACKWARD', 0.1)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.process_keyboard('LEFT', 0.1)
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.process_keyboard('RIGHT', 0.1)
