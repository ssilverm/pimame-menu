import os
import subprocess
import json
import pygame
from pygame.locals import *
from pmcontrols import *
from pmutil import *
from pmlabel import *
from pmcontrols import *
from pmwarning import *

class PMControllerConfig(pygame.sprite.Sprite):

	DIRECTORY = "/home/pi/pimame/controller-setup/"
	OUTPUT_DIRECTORY = DIRECTORY + "output/"
	

	def __init__(self, screen, cfg, title = "ControllerMain", controller = None):
		pygame.sprite.Sprite.__init__(self)
		
		self.CONTROLS = PMControls()
		self.input_test = [pygame.KEYDOWN, pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN]
		
		self.cfg = cfg
		self.screen = screen
		self.title = title
		
		self.hover = 0
		self.selected = False
		self.menu_open = True
		
		self.effect = None
		self.rect = None
		self.answer = None
		
		self.warning = None
		
		self.item_width = 0
		self.item_height = 0
		
		window_rect =  self.screen.get_rect()
		self.center_x = window_rect.centerx
		self.center_y = window_rect.centery
		
		self.original_screen = self.screen.copy()
		self.cfg.blur_image.blit(self.screen,(0,0))
		if self.cfg.use_scene_transitions:
			self.effect = PMUtil.blurSurf(self.cfg.blur_image, 20)
		else:
			self.effect = self.screen.copy()
			
		#  Try to initialize the first joystick
		try:
			stick = pygame.joystick.Joystick(0)
			stick.init()
			stick2 = pygame.joystick.Joystick(1)
			stick2.init()
		except:
			pass

		#  Formatters available 
		formatters_available = filter(lambda x: x[-3:]==".py", os.listdir(self.DIRECTORY + 'formatters'))

		#  What controller are we configuring?
		controllers_available = os.listdir(self.DIRECTORY +'controllers')

		if controller:
			self.controllers = [controller]
		else:
			self.controllers = controllers_available
		
		self.buttons = (["All"] + self.controllers) if len(self.controllers) > 1 else self.controllers

		events_to_capture = [KEYUP, JOYBUTTONUP, JOYHATMOTION, JOYAXISMOTION]

		self.list = BuildList(cfg, self.buttons)
		self.update_menu()
		self.rect = self.menu.get_rect()
		
		self.draw_menu()
	
	#MENU FUNCTIONS
	def hover_next(self):
		self.hover += 1
		if self.hover > (len(self.list.options)-1): self.hover = 0
		self.update_menu()
		
	def hover_prev(self):
		self.hover -= 1
		if self.hover < 0: self.hover = len(self.list.options)-1
		self.update_menu()
	
	def set_selected(self):
		self.selected = not self.selected
		self.update_menu()
		
	
	def update_menu(self):
			
		#not efficient way, should clear and redraw updated secion
		self.menu = pygame.Surface([self.list.item_width, self.list.item_height], pygame.SRCALPHA, 32).convert_alpha()
		self.rect = self.menu.get_rect()
		self.menu.fill(self.cfg.popup_menu_background_color, self.rect)
		
		y= 10
		for index, item in enumerate(self.list.options):
			y += item['title'].rect.h
			if index == self.hover:
				self.menu.blit(item['title_selected'].image, ((self.list.item_width - item['title_selected'].rect.w) / 2, y))
			else:
				self.menu.blit(item['title'].image, ((self.list.item_width - item['title'].rect.w) / 2, y))
					
	def render(self, message = None):  

		
		#  Display controller image
		#self.screen.blit(self.effect,(0,0))
		#self.screen.blit(self.fullscreen, (0,0))
		
		
		
		#  Display what button we're currently configuring
		if message: 
			key_text = PMLabel(message, self.cfg.popup_font, self.cfg.popup_menu_font_color)
		else:
			key_text = PMLabel("Currently configuring button: "+ self.buttons_to_update[self.current_button].replace("*",""), self.cfg.popup_font, self.cfg.popup_menu_font_color)
		key_text.rect.centerx = self.center_x
		key_text.rect.centery = self.controllerImageRect[1] + self.controllerImageRect[3] + self.cfg.popup_menu_font_size
		clear_rect =  key_text.rect.copy()
		clear_rect.w = self.background_rect.w
		clear_rect.centerx = self.center_x
		self.screen.blit(self.effect, clear_rect, clear_rect)
		self.screen.blit(self.fullscreen, clear_rect, clear_rect)
		self.screen.blit(key_text.image, key_text.rect) 
		
		pygame.display.update()
					

			
	def handle_events(self, action):
		
		if action == 'LEFT':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_prev()
			self.draw_menu()
		elif action == 'RIGHT':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_next()
			self.draw_menu()
		elif action == 'UP':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_prev()
			self.draw_menu()
		elif action == 'DOWN':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_next()
			self.draw_menu()
		elif action == 'BACK':
			self.cfg.menu_back_sound.play()
			self.menu_open = False
			self.screen.blit(self.original_screen,(0,0))
			pygame.display.update()
		
		if action == 'SELECT':
			self.cfg.menu_select_sound.play()
			self.answer = self.list.options[self.hover]['return']
			self.take_action()
		
		return None
		
	def draw_menu(self):
			self.screen.blit(self.effect,(0,0))
			self.screen.blit(self.menu, ((pygame.display.Info().current_w - self.rect.w)/2, (pygame.display.Info().current_h - self.rect.h)/2))
			pygame.display.update()
			
	def take_action(self, dict = []):
		
		avail_controller = self.controllers
		if self.answer == "CANCEL":
			self.menu_open = False
			self.screen.blit(self.original_screen,(0,0))
			pygame.display.update()
			
		#run the configurator!
		elif self.answer in self.buttons:
			if self.answer != 'All': avail_controller = [self.answer]
			for selected_controller in avail_controller:
				
				
				input_path = self.DIRECTORY + "controllers/" + selected_controller
				try:
					input_text = open(input_path + "/info.json").read()
				except:
					print "Invalid controller: %s. Skipping" % selected_controller
					continue
				self.controller = json.loads(input_text)
				
				if not 'max_players' in self.controller: self.controller['max_players'] = 1

				#  Load controller image
				self.controllerImage = pygame.image.load(input_path + '/' + self.controller['image']).convert_alpha()

				#  Setup where controller image will be drawn
				self.controllerImageRect = self.controllerImage.get_rect()
				self.background_rect = self.controllerImageRect.copy()
				self.background_rect.h = self.center_y * 1.5
				self.background_rect.w = self.center_x * 1.5
				self.background_rect.centerx = self.center_x
				self.background_rect.centery = self.center_y
				self.controllerImageRect.centerx = self.center_x
				self.controllerImageRect.centery = self.center_y
				self.fullscreen = self.effect.copy().convert_alpha()
				self.fullscreen.fill(self.cfg.popup_menu_background_color, self.background_rect)
				self.fullscreen.blit(self.controllerImage, self.controllerImageRect)
				
				# Display quit
				text = PMLabel("*Press Ctrl + Q to exit", self.cfg.popup_font, self.cfg.popup_menu_font_color)
				text.rect.centerx = self.center_x
				text.rect.centery = self.controllerImageRect[1] - self.cfg.popup_menu_font_size
				self.fullscreen.blit(text.image, self.background_rect)
				
				#  Display the controller label
				text = PMLabel("Controller: " + self.controller['name'], self.cfg.popup_font, self.cfg.popup_menu_font_color)
				text.rect.centerx = self.center_x
				text.rect.centery = self.controllerImageRect[1] - self.cfg.popup_menu_font_size
				self.fullscreen.blit(text.image, text.rect)
				
				self.screen.blit(self.effect, (0,0))
				self.screen.blit(self.fullscreen, (0,0))
				
				#  Which button are we adjusting?
				self.current_button = 0
				self.buttons_to_update = self.controller['controls']
				'''
					KEYUP = scancode, key, mod
					JOYBUTTONUP = joy, button
					JOYHATMOTION = joy, hat, value
				'''

				mapping = {}
				self.total_map = []
				running = True
				self.render()
				pygame.event.clear()
				
				events_to_capture = [KEYDOWN, JOYBUTTONDOWN, JOYHATMOTION, JOYAXISMOTION]
				action_list = [pygame.KEYDOWN, pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN]
				while running:
					events = pygame.event.get()
					
					for event in events:
						
						
						
						#ctrl+q to force quit
						if (pygame.key.get_mods() & pygame.KMOD_LCTRL) and event.type == pygame.KEYDOWN and event.key == pygame.K_q:
								self.cfg.menu_back_sound.play()
								if self.cfg.use_scene_transitions: effect = PMUtil.fade_out(self)
								running = False
								self.draw_menu()
								pygame.display.update()
								self.menu_open = False
								return
						
						elif self.warning and self.warning.menu_open:
							action = self.CONTROLS.get_action(action_list, events)
							self.warning.handle_events(action)
							if self.warning.answer:
								if self.warning.title == 'next_player':
									if self.warning.answer == "NO": 
										self.warning = None
										pygame.display.update()
										self.render("Building Config Files... Please Wait.")
										running = False
										break
									else:
										#calling render twice to make transition 'smoother'
										self.render()
										self.warning = None
										self.render()
						
						elif event.type in events_to_capture:
							if event.type == KEYDOWN:
								mapping[self.buttons_to_update[self.current_button]] = {"type":event.type, "key":event.key, "mod": event.mod, "keyname": pygame.key.name(event.key)}
							
							elif event.type == JOYBUTTONDOWN:
								mapping[self.buttons_to_update[self.current_button]] = {"type":event.type, "button":event.button, "joy": event.joy}
							
							elif event.type == JOYHATMOTION:
								#  Skip the event of the joystick reseting to 0, 0
								if event.value == (0,0):
									continue
								mapping[self.buttons_to_update[self.current_button]] = {"type": event.type, "value": event.value, "joy": event.joy}
							
							elif event.type == JOYAXISMOTION:
								#  Skip if the press wasn't 'hard' enough
								if event.value < 1.0 and event.value > -1.0:
									continue
								mapping[self.buttons_to_update[self.current_button]] = {"type": event.type, "value": event.value, "axis": event.axis, "joy": event.joy}
							
							#  Advance to next button
							self.current_button += 1
							while len(self.total_map) >= 1 and self.current_button < len(self.buttons_to_update) and self.buttons_to_update[self.current_button][0] == '*': self.current_button += 1
							if self.current_button >= len(self.buttons_to_update):
								self.current_button = 0
								self.total_map.append(mapping.copy())
								if len(self.total_map) == self.controller['max_players']:
									self.render("Building Config Files... Please Wait.")
									running = False
								else: 
									self.warning = PMWarning(self.screen, self.cfg, "Would you like to configure Player %d?" % (len(self.total_map) + 1), "yes/no", "next_player")
							else:
								self.render()

				#  Output our mapping
				with open(self.OUTPUT_DIRECTORY + self.controller['name'] + ".json", "w") as output_file:
					output_file.write(json.dumps(self.total_map, indent=4, separators=(',', ': ')))

				output_directory = []
				if "output_directory" in self.controller:
					for od in self.controller['output_directory']:
						output_directory.append(od)
				else:
					output_directory = self.OUTPUT_DIRECTORY + self.controller['name']  + "/" + formatter[:-3]

				#print output_directory
				count = 0
				#  Call Formatters
				if "formatters" in self.controller:
					for formatter in self.controller['formatters']:
						print formatter
						#print sys.executable, "formatters/"+formatter, controller['name'] + ".json ", output_directory[count]
						print output_directory[count]
						try:
							pid = os.system('python ' + self.DIRECTORY +  "formatters/" + formatter + " " + self.OUTPUT_DIRECTORY + self.controller['name'] + ".json " + output_directory[count] )
							#print pid
						except Exception as e:
							print e.message, e.args
							print formatter + " has failed."
						count += 1
					
				self.cfg.menu_back_sound.play()
				if self.cfg.use_scene_transitions: effect = PMUtil.fade_out(self)
				running = False
				self.draw_menu()
				pygame.display.update()
				return
			
		

		
class BuildList():
		def __init__(self, cfg, buttons, message = None):
			text_line = ''
			self.cfg = cfg
			self.lines = []
			
			if message:
				for words in message.split(' '):
					if len(text_line) + len(words) > 45 or words == '\n':
						self.lines.append(text_line)
						text_line = ''
					if words != '\n': text_line += words + ' '
				self.lines.append(text_line)
			
			
			self.options = [
				{
			"title": PMLabel(controller, self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMLabel(controller, self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"return": controller
			} for controller in buttons]
			
			
			self.options.append({
			"title": PMLabel("Cancel", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMLabel("Cancel", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"return": "CANCEL"
			})
			
			self.item_width = max(self.options, key=lambda x: x['title'].rect.w)['title'].rect.w + 40
			self.item_height = self.options[0]['title'].rect.h * (len(self.options) + 1) + 40
			
			
