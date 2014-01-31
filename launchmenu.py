import pygame
from pmmenu import pmmenu
from pmmenu.pmconfig import *
from pmmenu.scenemanager import *
from pmmenu.mainscene import *

#menu = pmmenu.PMMenu('config.yaml')
#menu.draw()



def main():
	cfg = PMCfg('/home/pi/pimame/pimame-menu/config.yaml')
	
	#pygame.init()
	#screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
	pygame.display.set_caption('PiMAME')
	timer = pygame.time.Clock()
	running = True

	manager = SceneManager(cfg, MainScene())

	while running:
		timer.tick(cfg.options.max_fps)

		if pygame.event.get(pygame.QUIT):
			running = False
			return
		manager.scene.handle_events(pygame.event.get())
		manager.scene.update()
		manager.scene.render(cfg.screen)
		pygame.display.flip()

if __name__ == "__main__":
	main()
