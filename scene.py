# scene.py
from model import Model
from OpenGL.GL import *
import logging
import os


class Scene:
    def __init__(self, camera):
        self.camera = camera
        # 加载glTF模型，假设glTF文件位于根目录下的model文件夹
        gltf_path = os.path.join('model', 'scene.gltf')
        if not os.path.isfile(gltf_path):
            logging.error(f"glTF模型文件不存在: {gltf_path}")
            raise FileNotFoundError(f"glTF模型文件不存在: {gltf_path}")
        self.model = Model(gltf_path)

    def update(self):
        # 更新物体状态（如动画等）
        pass

    def render(self, shader_program):
        self.model.render(shader_program)
