class SceneManager(object):
	history = []

	def __init__(self, cfg, initial_scene):
		self.cfg = cfg
		self.go_to(initial_scene)

	def go_to(self, scene):
		self.history.append(scene)

		self.scene = scene
		self.scene.manager = self
		self.scene.cfg = self.cfg
		self.scene.screen = self.cfg.screen
		self.scene.pre_render(self.cfg.screen)

	def back(self):
		self.history.pop()
		self.go_to(self.history.pop())
