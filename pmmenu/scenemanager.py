class SceneManager(object):
	history = []

	def __init__(self, cfg, initial_scene, call_render = True):
		self.cfg = cfg
		self.go_to(initial_scene, call_render)

	def go_to(self, scene, call_render = True):
		self.history.append(scene)

		self.scene = scene
		self.scene.manager = self
		self.scene.cfg = self.cfg
		self.scene.screen = self.cfg.screen
		self.scene.pre_render(self.cfg.screen, call_render)

	def back(self):
		self.history.pop()
		self.go_to(self.history.pop())
	