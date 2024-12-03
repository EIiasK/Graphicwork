# controls.py
import glfw

class Controls:
    def __init__(self, window, camera):
        self.window = window
        self.camera = camera

        # 存储按键状态的字典
        self.keys = {}

        # 设置键盘回调
        glfw.set_key_callback(window, self.key_callback)

        # 设置鼠标输入模式（捕获鼠标）
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        # 记录鼠标位置
        self.last_x, self.last_y = glfw.get_cursor_pos(window)
        self.first_mouse = True

    def key_callback(self, window, key, scancode, action, mods):
        # 当按键被按下或释放时，更新按键状态
        if action == glfw.PRESS:
            self.keys[key] = True
        elif action == glfw.RELEASE:
            self.keys[key] = False

    def handle_input(self, delta_time):
        # 根据按键状态移动相机
        if self.keys.get(glfw.KEY_W, False):
            print("W pressed")
            self.camera.process_keyboard('FORWARD', delta_time)
        if self.keys.get(glfw.KEY_S, False):
            print("S pressed")
            self.camera.process_keyboard('BACKWARD', delta_time)
        if self.keys.get(glfw.KEY_A, False):
            print("A pressed")
            self.camera.process_keyboard('LEFT', delta_time)
        if self.keys.get(glfw.KEY_D, False):
            print("D pressed")
            self.camera.process_keyboard('RIGHT', delta_time)

        # 获取鼠标移动
        x_pos, y_pos = glfw.get_cursor_pos(self.window)
        if self.first_mouse:
            self.last_x, self.last_y = x_pos, y_pos
            self.first_mouse = False

        x_offset = x_pos - self.last_x
        y_offset = self.last_y - y_pos  # 注意这里是反过来的

        self.last_x, self.last_y = x_pos, y_pos

        self.camera.process_mouse_movement(x_offset, y_offset)

