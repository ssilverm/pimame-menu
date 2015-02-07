from menuitem import *
from pmutil import *

class PMFlow(pygame.sprite.OrderedUpdates):
	#menu_items = []
	# menu_items_by_sprite = None
	options = None
	next_icon = 'nav_next.png'
	back_icon = 'nav_back.png'
	next_selected = 'nav_next-selected.png'
	back_selected = 'nav_back-selected.png'
	selected_index = 0
	update_display = []

	def __init__(self, menu_item_cfgs, cfg):

		pygame.sprite.OrderedUpdates.__init__(self)

		self.menu_items = []
		self.cfg = cfg
		self.first_index = self.last_index = 0
		self.selection = self.Selection(self.cfg)
		self.screen = pygame.display.get_surface()

		if self.cfg.options.sort_items_alphanum:
			menu_item_cfgs.sort(key=lambda x: x['label'])

		for menu_item in menu_item_cfgs:
			#print menu_item
			if menu_item['visible']:
				pm_menu_item = PMMenuItem(menu_item, self.cfg)
				if (
				
					(self.cfg.options.hide_emulators and pm_menu_item.num_roms == 0 and pm_menu_item.rom_path) or
					(self.cfg.options.hide_system_tools and pm_menu_item.type.upper() == "UTILITY")
					
					): pm_menu_item = None
					
				if pm_menu_item: self.menu_items.append(pm_menu_item)

		if self.cfg.options.sort_items_with_roms_first:
			self.menu_items.sort(key=self.roms_sort, reverse=True)	
			
		
		#pull all utilities to end of list
		self.menu_items.sort(key=self.utility_sort)
		self.empty()
		self.add(self.menu_items)
		self.set_selected_index(0, play_sound = False)
		

	def roms_sort (self, custom):
		if custom.num_roms > 0: return 1
		return 0
			
	def utility_sort(self, custom):
		if custom.type == "UTILITY": return 1
		return 0
	
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
		item_width = (screen_width - padding) - padding
		
		#self.screen.fill(self.cfg.options.background_color, self.style.selection.rect)
		self.screen.blit(self.cfg.options.pre_loaded_background, self.selection.rect, pygame.Rect(self.selection.rect[0], self.selection.rect[1], item_width, self.cfg.options.item_height))
			
		selection = pygame.sprite.RenderPlain((self.selection))
		selection.draw(self.screen)
		return self.selection.rect
	
	def draw_items(self, position = 0):
		padding = self.cfg.options.padding
		screen_width = pygame.display.Info().current_w
		item_width = screen_width * 2

		x = (screen_width/2) - (item_width * position)
		y = self.cfg.options.header_height + padding 

		sprites = self.sprites()
		for menu_item in sprites:
			menu_item.rect.centerx = x
			menu_item.rect.y = y
			x += item_width



		# @TODO: use this get_width() method everywhere instead of get_info()!
		#background = pygame.Surface([self.screen.get_width(), self.screen.get_height()]).convert()
		#background_image = self.cfg.options.pre_loaded_background
		#background.fill(self.cfg.options.background_color)
		#background.blit(background_image, (0,0))
		#background.set_alpha(None)
		
		self.clear(self.screen, self.cfg.options.pre_loaded_background)
		self.draw(self.screen)
		pygame.display.flip()
		
	def set_selected_index(self, new_selected_index, play_sound = True):
		if play_sound: self.cfg.options.menu_move_sound.play()

		self.update_display.append(self.erase_selection())
		num_menu_items = len(self.sprites())

		if new_selected_index < 0:
			new_selected_index = 0
		elif new_selected_index >= num_menu_items:
			new_selected_index = num_menu_items - 1
		
		self.draw_items(new_selected_index)
		self.selected_index = new_selected_index
		#self.selection.clear(self.screen)
		self.selection.update(self.get_selected_item())
		#self.draw_items()
		self.update_display.append(self.draw_selection())

	def get_selected_item(self):
		try:
			return self.sprites()[self.selected_index]
		except:
			return 0
			

	def handle_events(self, action):
		#NAVIGATE MAIN MENU
		if action == 'LEFT':
				self.set_selected_index(self.selected_index - 1)
		elif action == 'RIGHT':
				self.set_selected_index(self.selected_index + 1)
		elif action == 'UP':
				self.set_selected_index(self.selected_index - 1)
		elif action == 'DOWN':
				self.set_selected_index(self.selected_index + 1)

			
		return self.update_display
			
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
					self.prev_page()
					self.draw_items()
					self.set_selected_index(len(self.sprites()) - 1, play_sound = False)
					effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
				else:
					self.next_page()
					self.draw_items()
					self.set_selected_index(0, play_sound = False)
					effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
		else:
				self.cfg.options.menu_select_sound.play()
				PMUtil.run_command_and_continue(sprite.command)
		
	class Selection(pygame.sprite.Sprite):
		def __init__(self, cfg):
			pygame.sprite.Sprite.__init__(self)
			self.cfg = cfg

		def update(self, menu_item):
			#pygame.sprite.Sprite.__init__(self)
			
			self.image = menu_item.image.copy()
	
			self.rect = menu_item.rect



