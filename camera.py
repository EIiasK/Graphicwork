import glm
from utils import *
class Camera:
    def __init__(self, position=None, front=None, up=None):
        self.position = position if position else glm.vec3(0.0, 0.0, 10.0)  # 将初始位置拉远
        self.front = front if front else glm.vec3(0.0, 0.0, -1.0)
        self.up = up if up else glm.vec3(0.0, 1.0, 0.0)
        self.right = glm.normalize(glm.cross(self.front, self.up))
        self.world_up = self.up
        self.fov = 45.0

    def get_view_matrix(self):
        view_matrix = glm.lookAt(self.position, self.position + self.front, self.up)
        # print_matrix(view_matrix, "View Matrix")  # 调用打印函数
        return view_matrix

    def process_keyboard(self, direction, delta_time):
        speed = 2.5 * delta_time
        if direction == 'FORWARD':
            self.position += self.front * speed
        elif direction == 'BACKWARD':
            self.position -= self.front * speed
        elif direction == 'LEFT':
            self.position -= self.right * speed
        elif direction == 'RIGHT':
            self.position += self.right * speed

    def process_mouse(self, xoffset, yoffset):
        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity

        self.front.x += xoffset
        self.front.y += yoffset

        # 更新前向、右向和上向的向量
        self.front = glm.normalize(self.front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))
