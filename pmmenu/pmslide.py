from menuitem import *
from pmutil import *

class PMSlide(pygame.sprite.OrderedUpdates):
	
	update_display = []

	def __init__(self, menu_item_cfgs, cfg):

		pygame.sprite.OrderedUpdates.__init__(self)
		
		self.selected_index = None
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
		self.set_position(0)
		#self.set_selected_index(0, play_sound = False)
		

	def roms_sort (self, custom):
		if custom.num_roms > 0: return 1
		return 0
			
	def utility_sort(self, custom):
		if custom.type == "UTILITY": return 1
		return 0
	
	def erase_selection(self):
		try: selected_item = self.sprites()[self.selected_index]
		except: selected_item = None
		
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
	
	def set_position(self, position = 0):
		
		spacing = pygame.display.Info().current_w * 1.2
		screen_center = (pygame.display.Info().current_w / 2, 
								((pygame.display.Info().current_h - self.cfg.options.header_height) / 2) + self.cfg.options.header_height)
								

		self.current_position = position
		x = screen_center[0] - (spacing * position)
		y = screen_center[1]
		for menu_item in self.sprites():
			menu_item.rect.centerx = x
			menu_item.rect.centery = y
			x += spacing
			
	def ease(self, current_time, start_value, change_in_value, duration):
		#current_time = time or current frame
		#start_value = value to start at
		#change_in_value = end value - start_value
		#duration = total time or frames that you will run
		current_time /= duration / 2
		if (current_time < 1): 
			#in
			return change_in_value / 2 * current_time * current_time + start_value
		#out
		current_time -= 1
		return -change_in_value / 2 * (current_time * (current_time - 2) - 1) + start_value

	
	def draw_items(self, new_position = 0):
		#REQUIRED BY MAINSCENE
		self.new_position = new_position
		
		if self.selected_index != None:
			render_now = True
		else:
			render_now = False
		
		
		if render_now: self.cfg.options.menu_move_sound.play()
		
		if self.new_position < 0:
			self.new_position = 0
		elif self.new_position >= len(self.sprites()):
			self.new_position = len(self.sprites()) - 1
		
		spacing = pygame.display.Info().current_w * 1.2
		screen_center = (pygame.display.Info().current_w / 2, 
								((pygame.display.Info().current_h - self.cfg.options.header_height) / 2) + self.cfg.options.header_height)
								

		distance = self.current_position - self.new_position

		if distance < 0:
			direction = -1
		elif distance > 0:
			direction = 1
		else:
			direction = 0
			
		slideto = abs(distance) * spacing

		
		duration = 50
		speed = self.ease(1.0, 0, slideto, duration)
		pos = 0
		amt = -2
		if direction == 1:
			amt = 1
		for x in xrange(2,duration + amt):
			for sprite in self.sprites():
				sprite.rect.centerx += (speed * direction)
				if render_now: self.update_display.append(sprite.rect)
			pos = self.ease(float(x - 1), 0, slideto, duration)
			speed = self.ease(float(x), 0, slideto, duration) - pos
			
			self.clear(self.screen, self.cfg.options.pre_loaded_background)
			self.draw(self.screen)
			if render_now: pygame.display.update(self.update_display)
			self.update_display = []
		
		self.current_position = self.new_position
		sprite = self.sprites()[self.current_position]
		
		if render_now:
			self.set_position(self.current_position)
			self.clear(self.screen, self.cfg.options.pre_loaded_background)
			self.draw(self.screen)
			self.update_display.append(sprite.rect)
		
		

		if sprite.banner:
			self.cfg.options.fade_image.blit(self.screen,(0,0))
			banner_rect = sprite.banner.get_rect().fit(sprite.rect)
			try: banner = pygame.transform.smoothscale(sprite.banner, (banner_rect.w, banner_rect.h)) 
			except: banner = pygame.transform.scale(sprite.banner, (banner_rect.w, banner_rect.h))
			self.clear(self.screen, self.cfg.options.pre_loaded_background)
			self.screen.blit(banner, banner_rect)
			self.selection.update(self.sprites()[self.new_position])
			self.screen.blit(self.selection.image, self.selection.rect)
			#self.draw(self.screen)
			if render_now: effect = PMUtil.offset_fade_into(self, self.cfg.options.fade_image, banner_rect, self.cfg.options.use_scene_transitions, duration=30)
			#if render_now: effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
		else:
			self.clear(self.screen, self.cfg.options.pre_loaded_background)
			self.selection.update(self.sprites()[self.new_position])
			self.screen.blit(self.selection.image, self.selection.rect)
			self.update_display.append(self.selection.rect)
		
		self.selected_index = self.new_position

		
	def set_selected_index(self, new_selected_index, play_sound = True):
		#REQUIRED BY MAINSCENE
		pass

	def get_selected_item(self):
		#REQUIRED BY MAINSCENE
		try: return self.sprites()[self.selected_index]
		except: return None
			

	def handle_events(self, action):
		#REQUIRED BY MAINSCENE
		
		#NAVIGATE MAIN MENU
		if action == 'LEFT':
				self.draw_items(self.selected_index - 1)
		elif action == 'RIGHT':
				self.draw_items(self.selected_index + 1)
		elif action == 'UP':
				self.draw_items(0)
		elif action == 'DOWN':
				self.draw_items(len(self.sprites()) - 1)

			
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
		else:
				self.cfg.options.menu_select_sound.play()
				PMUtil.run_command_and_continue(sprite.command)
		
	class Selection(pygame.sprite.Sprite):
		def __init__(self, cfg):
			pygame.sprite.Sprite.__init__(self)
			self.cfg = cfg

		def update(self, menu_item):
			#pygame.sprite.Sprite.__init__(self)
			
			screen_width = pygame.display.Info().current_w
			item_width = ((screen_width - self.cfg.options.padding) / self.cfg.options.num_items_per_row) - self.cfg.options.padding

			self.image = pygame.Surface([item_width, self.cfg.options.item_height], pygame.SRCALPHA, 32).convert_alpha()

			if menu_item.icon_selected:
				icon = menu_item.pre_loaded_selected_icon.copy()
				
				# resize and center icon:
				icon_size = icon.get_size()
				text_align = icon_size[0]
				avail_icon_width = item_width - self.cfg.options.padding * 2
				avail_icon_height = self.cfg.options.item_height - self.cfg.options.padding * 2
				while True:
					icon_width = icon_size[0]
					icon_height = icon_size[1]
					icon_ratio = float(icon_height) / float(icon_width)
					icon_width_diff = avail_icon_width - icon_width
					icon_height_diff = avail_icon_height - icon_height
					if icon_width_diff < icon_height_diff:
						diff = icon_width_diff
						icon_size = (icon_width + diff, icon_height + diff * icon_ratio)
					else:
						diff = icon_height_diff
						icon_size = (icon_width + diff / icon_ratio, icon_height + diff)

					icon_size = (int(icon_size[0]), int(icon_size[1]))

					if icon_size[0] <= avail_icon_width and icon_size[1] <= avail_icon_height:
						break
				
				#ReDraw label ontop of menu_item 
				if menu_item.display_label:
					label = PMLabel(menu_item.label, self.cfg.options.label_font, self.cfg.options.label_font_selected_color, self.cfg.options.label_background_selected_color, self.cfg.options.label_font_selected_bold, self.cfg.options.label_max_text_width)
					textpos = label.rect
					if self.cfg.options.label_text_align == 'right': textpos.x = text_align - label.rect.w + self.cfg.options.labels_offset[0]
					elif  self.cfg.options.label_text_align == 'center': textpos.x = ((text_align - label.rect.w)/2) + self.cfg.options.labels_offset[0]
					else: textpos.x = self.cfg.options.labels_offset[0]
					textpos.y = self.cfg.options.labels_offset[1]

					icon.blit(label.image, textpos)
				
				#ReDraw rom-count ontop of menu_item
				if self.cfg.options.display_rom_count:
					if menu_item.rom_path and menu_item.num_roms != 0:

						label = PMLabel(str(menu_item.num_roms) + menu_item.warning, self.cfg.options.rom_count_font, self.cfg.options.rom_count_font_selected_color, self.cfg.options.rom_count_background_selected_color, self.cfg.options.rom_count_font_selected_bold, self.cfg.options.rom_count_max_text_width)
						textpos = label.rect
						
						if self.cfg.options.rom_count_text_align == 'right': textpos.x = text_align - label.rect.w + self.cfg.options.rom_count_offset[0]
						elif  self.cfg.options.rom_count_text_align == 'center': textpos.x = ((text_align - label.rect.w)/2) + self.cfg.options.rom_count_offset[0]
						else: textpos.x = self.cfg.options.rom_count_offset[0]
						textpos.y = self.cfg.options.rom_count_offset[1]

						icon.blit(label.image, textpos)
							
				icon = pygame.transform.smoothscale(icon, icon_size)
				self.image.blit(icon, ((avail_icon_width - icon_size[0]) / 2 + self.cfg.options.padding, (avail_icon_height - icon_size[1]) / 2 + self.cfg.options.padding))
				
				self.rect = self.image.get_rect()
			else:
				self.image = menu_item.image.copy()
				self.rect = menu_item.rect.copy()
				
			self.rect.center = menu_item.rect.center




