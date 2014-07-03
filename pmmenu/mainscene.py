import pygame
from pmcontrols import *
from pmpopup import *
from pmwarning import *
from pmconfig import *
from pmheader import *
from pmselection import *
from pmlabel import *
from pmutil import *
from romlistscene import *

class MainScene(object):

	SCENE_NAME = 'main'
	
	selected_index = 0
	pre_rendered = False

	def __init__(self):
		super(MainScene, self).__init__()
		self.CONTROLS = PMControls()

	def get_selected_item(self):
		try:
			return self.grid.sprites()[self.selected_index]
		except:
			return False

	def set_selected_index(self, new_selected_index, play_sound = True):
		if play_sound: self.cfg.options.menu_move_sound.play()
		self.erase_selection()

		num_menu_items = len(self.grid.sprites())

		if new_selected_index < 0:
			new_selected_index = 0
		elif new_selected_index >= num_menu_items:
			new_selected_index = num_menu_items - 1

		self.selected_index = new_selected_index
		#self.selection.clear(self.screen)
		self.selection.update(self.get_selected_item(), self.cfg.options)
		#self.draw_items()
		self.draw_selection()
		

	def draw_bg(self):
		background_image = self.cfg.options.pre_loaded_background
		background_rect = background_image.get_rect()
		screen_width = pygame.display.Info().current_w
		screen_height = pygame.display.Info().current_h
		scale = min(float(background_rect.w) / float(screen_width), float(background_rect.h) / float(screen_height))
		background_rect = (int(background_rect.w / scale), int(background_rect.h / scale))
		
		self.cfg.options.pre_loaded_background =  pygame.transform.smoothscale(self.cfg.options.pre_loaded_background, background_rect)
		background_image = self.cfg.options.pre_loaded_background
		
		self.screen.fill(self.cfg.options.background_color)
		
		self.screen.blit(background_image, (0,0))


		
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
			
			self.screen.fill(self.cfg.options.background_color, selected_item.rect)
			self.screen.blit(self.cfg.options.pre_loaded_background, selected_item.rect, pygame.Rect(selected_item.rect[0], selected_item.rect[1], item_width, self.cfg.options.item_height))
			
			pygame.sprite.RenderPlain(selected_item).draw(self.screen)

	def draw_selection(self):
		padding = self.cfg.options.padding
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding
		
		self.screen.fill(self.cfg.options.background_color, self.selection.rect)
		self.screen.blit(self.cfg.options.pre_loaded_background, self.selection.rect, pygame.Rect(self.selection.rect[0], self.selection.rect[1], item_width, self.cfg.options.item_height))
			
		selection = pygame.sprite.RenderPlain((self.selection))
		selection.draw(self.screen)

	def calc_num_items_per_page(self):
		padding = self.cfg.options.padding
		avail_height = pygame.display.Info().current_h - self.cfg.options.header_height - padding * 2
		item_height = self.cfg.options.item_height + padding
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
		background = pygame.Surface([self.screen.get_width(), self.screen.get_height()], pygame.SRCALPHA, 32).convert_alpha()
		background_image = self.cfg.options.pre_loaded_background
		background.fill(self.cfg.options.background_color)
		background.blit(background_image, (0,0))
		
		self.grid.clear(self.screen, background)
		self.grid.draw(self.screen)


	def pre_render(self, screen):
		if not self.pre_rendered:
			self.header = PMHeader(self.cfg.options)
			self.selection = PMSelection(self.cfg.options)
			self.grid = PMGrid(self.cfg.options.options_menu_items, self.cfg.options)
			self.grid.set_num_items_per_page(self.calc_num_items_per_page())
			self.popup = PMPopup(self.manager.scene.SCENE_NAME, self.cfg.options)
			self.warning = None
			self.pre_rendered = True
		
		self.draw_bg()
		self.draw_header()
		self.draw_ip_addr()
		self.draw_update()
		self.draw_items()
		#self.draw_selection()
		self.set_selected_index(0, play_sound = False)

		if self.cfg.options.fade_image:
			if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_into(self, self.cfg.options.fade_image)
		else:
			if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_in(self)
			self.cfg.options.fade_image = pygame.Surface([self.screen.get_width(), self.screen.get_height()], pygame.SRCALPHA, 32).convert()
		self.cfg.options.fade_image.blit(self.screen,(0,0))



	def render(self, screen):
		pass

	def update(self):
		pass

	def handle_events(self, events):
		for event in events:
			
			
			#ctrl+q to force quit
			if event.type == pygame.KEYDOWN:
				if pygame.key.get_mods() & pygame.KMOD_LCTRL:
					if event.key == pygame.K_q:
						self.cfg.options.menu_back_sound.play()
						if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_out(self)
						pygame.quit()
						sys.exit()
						
			if event.type == pygame.QUIT:
				self.cfg.options.menu_back_sound.play()
				if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_out(self)
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()

				# get all rects under cursor
				clicked_sprites = [s for s in self.grid if s.rect.collidepoint(pos)]

				if len(clicked_sprites) > 0:
					sprite = clicked_sprites[0]
					self.do_menu_item_action(sprite)
					
			action = None		
			if event.type == pygame.KEYDOWN: action = self.CONTROLS.get_action('keyboard', event.key)
			if event.type == pygame.JOYAXISMOTION: action = self.CONTROLS.get_action('joystick', event.dict)
			if event.type == pygame.JOYBUTTONDOWN: action = self.CONTROLS.get_action('joystick', event.button)
			
			# self.warning = PMWarning(self.screen, self.cfg.options, "message goes here", "yes/no")
			#answer will return False until selection -> yes, no, ok, or cancel
			if self.warning and self.warning.menu_open:
				self.warning.handle_events(action)
				if self.warning.answer:
					self.warning.take_action({'YES': 'python /home/pi/pimame/pimame-menu/scraper/scrape_script.py --platform ' + self.get_selected_item().label})
					if self.warning.answer == "NO":
						self.warning = None
						self.do_menu_item_action(self.get_selected_item())
					
			elif self.popup.menu_open:
				self.popup.handle_events(action, self.screen, self.effect)
			else:
			
				if action == 'LEFT':
					self.set_selected_index(self.selected_index - 1)
					
				elif action == 'RIGHT':
					self.set_selected_index(self.selected_index + 1)
					
				elif action == 'UP':
					self.set_selected_index(self.selected_index - self.cfg.options.num_items_per_row)
					
				elif action == 'DOWN':
					self.set_selected_index(self.selected_index + self.cfg.options.num_items_per_row)
					
				elif action == 'SELECT':
					sprite = self.get_selected_item()
					if "!" in str(sprite.num_roms) and not self.warning: 
						self.warning = PMWarning(self.screen, self.cfg.options, "Some files have changed, would you like to scrape this folder for new roms?", "yes/no")
					elif not self.warning:
						self.do_menu_item_action(sprite)
						
				elif action == 'MENU':
					self.popup.menu_open = True
					self.cfg.options.fade_image.blit(self.screen,(0,0))
					if self.cfg.options.use_scene_transitions:
						self.effect = PMUtil.blurSurf(self.screen, 20)
						self.screen.blit(self.effect,(0,0))
					else:
						self.effect = self.screen.copy()
					self.screen.blit(self.popup.menu,((pygame.display.Info().current_w - self.popup.rect.w)/2, (pygame.display.Info().current_h - self.popup.rect.h)/2))
					
				elif action == 'BACK' and self.cfg.options.allow_quit_to_console:
					self.cfg.options.menu_back_sound.play()
					if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_out(self)
					pygame.quit()
					sys.exit()
				
					

	#@TODO - change name:
	def do_menu_item_action(self, sprite):
		if sprite.type == PMMenuItem.ROM_LIST:
				self.cfg.options.fade_image.blit(self.screen,(0,0))
				self.cfg.options.menu_select_sound.play()
				self.manager.go_to(RomListScene(sprite.get_rom_list()))
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
				if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_into(self, self.cfg.options.fade_image)
			else:
				self.grid.next_page()
				self.draw_items()
				self.set_selected_index(0, play_sound = False)
				if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_into(self, self.cfg.options.fade_image)
