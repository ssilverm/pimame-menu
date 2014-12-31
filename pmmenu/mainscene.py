import pygame
from pmcontrols import *
from pmpopup import *
from pmwarning import *
from pmcontrollerconfig import *
from pmconfig import *
from pmheader import *
from pmselection import *
from pmlabel import *
from pmutil import *
from romlistscene import *
import os

class MainScene(object):

	SCENE_NAME = 'main'
	update_display = []
	
	selected_index = 0
	pre_rendered = False

	def __init__(self):
		super(MainScene, self).__init__()


	def get_selected_item(self):
		try:
			return self.grid.sprites()[self.selected_index]
		except:
			return False

	def set_selected_index(self, new_selected_index, play_sound = True):
		if play_sound: self.cfg.options.menu_move_sound.play()
		self.update_display.append(self.erase_selection())

		num_menu_items = len(self.grid.sprites())

		if new_selected_index < 0:
			new_selected_index = 0
		elif new_selected_index >= num_menu_items:
			new_selected_index = num_menu_items - 1

		self.selected_index = new_selected_index
		#self.selection.clear(self.screen)
		self.selection.update(self.get_selected_item(), self.cfg.options)
		#self.draw_items()
		self.update_display.append(self.draw_selection())
		

	def draw_bg(self):
		#self.screen.fill(self.cfg.options.background_color)
		self.screen.blit(self.cfg.options.pre_loaded_background, (0,0))
		
	def draw_header(self):
		# @TODO - how to prepare ahead of time:
		header = pygame.sprite.RenderPlain((self.header))
		header.draw(self.screen)

	def draw_ip_addr(self):
		displayString = ''

		if self.cfg.options.show_ip:
			try:
				displayString = PMUtil.get_ip_addr()
			except:
				displayString = "No Network Connection"

			self.ip_addr = PMLabel(displayString, self.cfg.options.font, self.cfg.options.default_font_color, self.cfg.options.default_font_background_color)
			label = pygame.sprite.RenderPlain((self.ip_addr))
			textpos = self.ip_addr.rect
			textpos.x = pygame.display.Info().current_w - textpos.width - self.cfg.options.padding
			textpos.y = self.cfg.options.padding
			label.draw(self.screen)

	def draw_update(self):
		displayString = ''

		if self.cfg.options.show_update:
			user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0"}
			try:
				import requests
				version_web = float( requests.get('http://www.pimame.org/version', headers = user_agent).text)
				version_current = float(open("../version", 'r').read())
				if version_current < version_web:
					displayString = "New Version Available"
			except:
				displayString = "Could not check for updates"

			self.update_label = PMLabel(displayString, self.cfg.options.font, self.cfg.options.default_font_color, self.cfg.options.default_font_background_color)
			label = pygame.sprite.RenderPlain((self.update_label))
			textpos = self.update_label.rect
			textpos.x = self.cfg.options.padding
			textpos.y = self.cfg.options.padding
			label.draw(self.screen)

	def erase_selection(self):
		selected_item = self.get_selected_item()

		if selected_item:
			
			padding = self.cfg.options.padding
			screen_width = pygame.display.Info().current_w
			item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding
			
			#self.screen.fill(self.cfg.options.background_color, selected_item.rect)
			self.screen.blit(self.cfg.options.pre_loaded_background, selected_item.rect, pygame.Rect(selected_item.rect[0], selected_item.rect[1], item_width, self.cfg.options.item_height))
			
			pygame.sprite.RenderPlain(selected_item).draw(self.screen)
			return selected_item.rect

	def draw_selection(self):
		padding = self.cfg.options.padding
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding
		
		#self.screen.fill(self.cfg.options.background_color, self.selection.rect)
		self.screen.blit(self.cfg.options.pre_loaded_background, self.selection.rect, pygame.Rect(self.selection.rect[0], self.selection.rect[1], item_width, self.cfg.options.item_height))
			
		selection = pygame.sprite.RenderPlain((self.selection))
		selection.draw(self.screen)
		return self.selection.rect

	def calc_num_items_per_page(self):
		padding = self.cfg.options.padding
		avail_height = pygame.display.Info().current_h - self.cfg.options.header_height - padding * 2
		item_height = self.cfg.options.item_height + padding
		
		#trap the case where item_height in theme.yaml is larger than the available space 		
		if item_height > avail_height:
			item_height = avail_height
		
		num_rows = avail_height / item_height

		return num_rows * self.cfg.options.num_items_per_row

	def draw_items(self):
		padding = self.cfg.options.padding
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding

		x = padding
		y = self.header.rect.h + padding
		i = 1

		sprites = self.grid.sprites()
		for menu_item in sprites:
			menu_item.rect.x = x
			menu_item.rect.y = y

			if i % self.cfg.options.num_items_per_row == 0:
				x = padding
				y += self.cfg.options.item_height + padding
			else:
				x += item_width + padding

			i += 1


		# @TODO: use this get_width() method everywhere instead of get_info()!
		#background = pygame.Surface([self.screen.get_width(), self.screen.get_height()]).convert()
		#background_image = self.cfg.options.pre_loaded_background
		#background.fill(self.cfg.options.background_color)
		#background.blit(background_image, (0,0))
		#background.set_alpha(None)
		
		self.grid.clear(self.screen, self.cfg.options.pre_loaded_background)
		self.grid.draw(self.screen)


	def pre_render(self, screen, call_render):
		if not self.pre_rendered:
			self.grid = PMGrid(self.cfg.options.options_menu_items, self.cfg)
			self.grid.set_num_items_per_page(self.calc_num_items_per_page())
			self.popup = None
			self.warning = None
			self.pre_rendered = True
		
		if call_render: self.render(self.screen)
		
	def render(self, screen):
		self.header = PMHeader(self.cfg.options)
		self.selection = PMSelection(self.cfg.options)
		self.draw_bg()
		self.draw_header()
		self.draw_ip_addr()
		self.draw_update()
		self.draw_items()
		#self.draw_selection()
		self.set_selected_index(0, play_sound = False)

		if self.cfg.options.fade_image:
			effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
		else:
			effect = PMUtil.fade_in(self, self.cfg.options.use_scene_transitions)
		self.cfg.options.fade_image.blit(self.screen,(0,0))
		
		
		if not os.path.isfile('/home/pi/pimame/changelogs/firstrun_passed'):
			open('/home/pi/pimame/changelogs/firstrun_passed', 'a').close()
			self.warning = PMWarning(self.screen, self.cfg.options, 
				[["center","Welcome to PiPlay!"], 
				["center", ""],
				["left", "Here's the default control scheme:"],
				["left", "-Press 'Enter' or 'joystick button 1' to make selections"],
				["left", "-Press 'Esc' or 'joystick button 2' to go back"],
				["left", "-Press 'Tab' or 'joystick button 3' to open your popup menu"],
				["center", ""],
				["left", "*Hint: try the popup menu when selecting a game"]], "ok", "FIRST_RUN")
		else:
			self.changelog_check()

	def update(self):
		pass
		
	def warning_check(self):
		if self.warning.answer:
				if self.warning.title == 'ROMS':
					if self.warning.answer == "YES": 
						PMUtil.run_command_and_continue('python /home/pi/pimame/pimame-menu/scraper/scrape_script.py --platform ' + str(self.get_selected_item().id))
					else:
						#PMUtil.run_command_and_continue('python /home/pi/pimame/pimame-menu/scraper/scrape_script.py --dont_match True --platform ' + str(self.get_selected_item().id))
						self.warning = None
						self.do_menu_item_action(self.get_selected_item())
					return
				
				try:
					if self.warning.title == 'KICKSTARTER':
						if self.warning.answer == "OK":
							self.warning = None
							self.ks_line = ''
							self.ks_range += 20
							if self.ks_range < len(self.cfg.options.ks):
								for person in self.cfg.options.ks[self.ks_range:self.ks_range+19]:
									self.ks_line += person + ' \n '
								self.warning = PMWarning(self.screen, self.cfg.options, self.ks_line, "ok/cancel", 'KICKSTARTER')
						else:
							self.warning = None
						return
				except:
					pass
				
				if self.warning.title == 'FIRST_RUN':
					if not self.warning.menu_open: 
						self.warning = None
						self.changelog_check()
					return
						
				if self.warning.title == 'CHANGELOG':
					self.warning = None
					return
					
	def changelog_check(self):
		#check if flag file exists
		if os.path.isfile('/home/pi/pimame/changelogs/show_changelog'):
			try:
				#get current version
				with open('/home/pi/pimame/version') as file:
					version = file.readline().strip()
				
				#load current version changelog into array, Delete flag file
				changelog = [line for line in open('/home/pi/pimame/changelogs/' + version)]
				os.remove('/home/pi/pimame/changelogs/show_changelog')
				
				#build message
				message = [["center", "Version " + changelog[0].strip() + " Changelog"]]
				for line in changelog[1:]:
						message.append(["left", line.strip()])
				self.warning = PMWarning(self.screen, self.cfg.options, message, "ok", "CHANGELOG")
			except:
				pass

	def handle_events(self, action):
		
		if self.warning and not self.warning.menu_open: self.warning = None
		
		# self.warning = PMWarning(self.screen, self.cfg.options, "message goes here", "yes/no")
		#answer will return False until selection -> yes, no, ok, or cancel
		if self.warning and self.warning.menu_open:
			self.warning.handle_events(action)
			self.warning_check()
				
		elif self.popup and self.popup.menu_open:
			status = self.popup.handle_events(action)
			if status == "CONTROLLER": self.popup = PMControllerConfig(self.screen, self.cfg.options)
			
		else:
			
			#NAVIGATE MAIN MENU
			if action == 'LEFT':
				if self.selected_index == 0: 
					sprite = self.get_selected_item()
					if sprite.type == PMMenuItem.NAVIGATION:
						self.do_menu_item_action(sprite)
				else:
					self.set_selected_index(self.selected_index - 1)
			elif action == 'RIGHT':
				if self.selected_index == self.grid.num_items_per_page - 1:    #zero based
					sprite = self.get_selected_item()
					if sprite.type == PMMenuItem.NAVIGATION:
						self.do_menu_item_action(sprite)
				else:
					self.set_selected_index(self.selected_index + 1)
			elif action == 'UP':
				if self.selected_index == 0:
					sprite = self.get_selected_item()
					if sprite.type == PMMenuItem.NAVIGATION:
						self.do_menu_item_action(sprite)
				else:
					self.set_selected_index(self.selected_index - self.cfg.options.num_items_per_row)
			elif action == 'DOWN':
				if self.selected_index == self.grid.num_items_per_page - 1:    #zero based
					sprite = self.get_selected_item()
					if sprite.type == PMMenuItem.NAVIGATION:
						self.do_menu_item_action(sprite)
				else: 
					self.set_selected_index(self.selected_index + self.cfg.options.num_items_per_row)
			elif action == 'SELECT':
				sprite = self.get_selected_item()
				#DISPLAY WARNING IF FILES HAVE CHANGED
				if sprite.warning == "!" and not self.warning: 
					self.warning = PMWarning(self.screen, self.cfg.options, "Some files have changed, would you like to scrape this folder for new roms?", "yes/no", "ROMS")
				elif not self.warning:
					self.do_menu_item_action(sprite)
			elif action == 'BACK' and self.cfg.options.allow_quit_to_console:
				self.cfg.options.menu_back_sound.play()
				effect = PMUtil.fade_out(self, self.cfg.options.use_scene_transitions)
				pygame.quit()
				sys.exit()
			
			#POPUP OPTIONS MENU
			elif action == 'MENU':
				self.popup = PMPopup(self.screen, self.manager.scene.SCENE_NAME, self.cfg, True)
			
			#SHOW KICKSTARTER SUPPORTERS
			elif action == 'KICKSTARTER':
				if not self.warning:
					self.ks_range = 0
					self.ks_line = ''
					self.cfg.options.load_ks()
					for person in self.cfg.options.ks[0:19]:
						self.ks_line += person + ' \n '
					self.warning = PMWarning(self.screen, self.cfg.options, self.ks_line, "ok/cancel", 'KICKSTARTER')
			
			#MOUSE CLICK
			elif action == "MOUSEBUTTON":
				pos = pygame.mouse.get_pos()
				# get all rects under cursor
				clicked_sprites = [s for s in self.grid if s.rect.collidepoint(pos)]
				
				if len(clicked_sprites) > 0:
					sprite = clicked_sprites[0]
					self.do_menu_item_action(sprite)
			
			#MOUSE MOVE
			elif action == "MOUSEMOVE":
				pos = pygame.mouse.get_pos()
				# get all rects under cursor
				if not self.grid.menu_items[self.selected_index].rect.collidepoint(pos):
					clicked_sprites = [index for index, s in enumerate(self.grid) if s.rect.collidepoint(pos)]
				
					if len(clicked_sprites) > 0:
						sprite = clicked_sprites[0]
						self.set_selected_index(sprite)
					
				
		return self.update_display

	#@TODO - change name:
	def do_menu_item_action(self, sprite):
		if sprite.type == PMMenuItem.EMULATOR:
				self.cfg.options.fade_image.blit(self.screen,(0,0))
				self.cfg.options.menu_select_sound.play()
				self.manager.go_to(RomListScene(sprite.get_rom_list(), sprite.label))
		elif sprite.command == 'exit_piplay':
				pygame.quit()
				sys.exit()
		elif sprite.type == PMMenuItem.COMMAND:
				self.cfg.options.menu_select_sound.play()
				PMUtil.run_command_and_continue(sprite.command)
		elif sprite.type == PMMenuItem.NAVIGATION:
				self.cfg.options.menu_navigation_sound.play()
				self.cfg.options.fade_image.blit(self.screen,(0,0))
				if sprite.command == PMMenuItem.PREV_PAGE:
					self.grid.prev_page()
					self.draw_items()
					self.set_selected_index(len(self.grid.sprites()) - 1, play_sound = False)
					effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
				else:
					self.grid.next_page()
					self.draw_items()
					self.set_selected_index(0, play_sound = False)
					effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
		else:
				self.cfg.options.menu_select_sound.play()
				PMUtil.run_command_and_continue(sprite.command)
