# camera.py
import glm

class Camera:
    def __init__(self, position=glm.vec3(0.0, 0.0, 3.0), up=glm.vec3(0.0, 1.0, 0.0), yaw=-90.0, pitch=0.0):
        self.position = position
        self.world_up = up
        self.up = up
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 2.5
        self.sensitivity = 0.1
        self.fov = 45.0
        self.update_camera_vectors()

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def process_keyboard(self, direction, delta_time):
        velocity = self.speed * delta_time
        if direction == "FORWARD":
            self.position += self.front * velocity
        if direction == "BACKWARD":
            self.position -= self.front * velocity
        if direction == "LEFT":
            self.position -= self.right * velocity
        if direction == "RIGHT":
            self.position += self.right * velocity

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_camera_vectors()

    def process_mouse_scroll(self, yoffset):
        if self.fov >= 1.0 and self.fov <= 45.0:
            self.fov -= yoffset
        if self.fov <= 1.0:
            self.fov = 1.0
        if self.fov >= 45.0:
            self.fov = 45.0

    def update_camera_vectors(self):
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))
