from mainscene import *

class SceneManager(object):
	def __init__(self, cfg):
		self.cfg = cfg
		self.go_to(MainScene())

	def go_to(self, scene):
		self.scene = scene
		self.scene.manager = self
		self.scene.cfg = self.cfg
		self.scene.screen = self.cfg.screen
		self.scene.pre_render(self.cfg.screen)