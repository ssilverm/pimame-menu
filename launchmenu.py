import argparse
import pygame
from pmmenu import pmmenu
from pmmenu.pmconfig import *
from pmmenu.scenemanager import *
from pmmenu.mainscene import *
from pmmenu.romlistscene import *


parser = argparse.ArgumentParser(description='PiPlay')
parser.add_argument("--quicklaunch", metavar="value", help="Which platform to skip to", type=str)
args = parser.parse_args()

def main():
	cfg = PMCfg()
	controls = PMControls()
	

	pygame.display.set_caption('PiMAME')
	#TODO: need to set_icon
	
	timer = pygame.time.Clock()
	running = True
	input_test = [pygame.KEYDOWN, pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]
	refresh = 0
	total_refresh = cfg.options.max_fps * 5
	

	
	
	if args.quicklaunch: 
		manager = SceneManager(cfg, MainScene(), False)
		print "Relaunch", args.quicklaunch

		for sprite in manager.scene.grid:
			if sprite.label == args.quicklaunch:
				manager.go_to(RomListScene(sprite.get_rom_list(), sprite.label))
	else:
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
		if refresh == total_refresh:
			pygame.display.flip()
		pygame.event.clear()
		
		

if __name__ == "__main__":
	main()
