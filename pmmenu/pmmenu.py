# def main():
# 	pygame.init()
# 	screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
# 	pygame.display.set_caption('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
# 	timer = pygame.time.Clock()
# 	running = True

# 	manager = SceneManager()

# 	while running:
# 		timer.tick(60)

# 		if pygame.event.get(QUIT):
# 			running = False
# 			return
# 		manager.scene.handle_events(pygame.event.get())
# 		manager.scene.update()
# 		manager.scene.render(screen)
# 		pygame.display.flip()