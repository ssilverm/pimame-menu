import pygame
from pmmenu import pmmenu
from pmmenu.pmconfig import *
from pmmenu.scenemanager import *
from pmmenu.mainscene import *

#menu = pmmenu.PMMenu('config.yaml')
#menu.draw()



def main():
	cfg = PMCfg()
	controls = PMControls()
	
	#pygame.init()
	#screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
	pygame.display.set_caption('PiMAME')
	#TODO: need to set_icon
	
	timer = pygame.time.Clock()
	running = True
	input_test = [pygame.KEYDOWN, pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]
	refresh = 0
	
	manager = SceneManager(cfg, MainScene())
	
	while running:
		timer.tick(cfg.options.max_fps)
		action = None
		
		if pygame.event.peek(input_test):
			action = controls.get_action()
		
		if action == 'QUIT':
			pygame.quit()
			sys.exit()
		
		update_display = []
		if action: update_display = manager.scene.handle_events(action)
		#manager.scene.update()
		#manager.scene.render(cfg.screen)
		if update_display: 
			pygame.display.update(update_display)
			manager.scene.update_display = []
			refresh += 1
			if refresh == 20:
				pygame.display.flip()
		pygame.event.clear()
		
		

if __name__ == "__main__":
	main()
