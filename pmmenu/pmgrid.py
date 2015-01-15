from menuitem import *
from pmutil import *

class PMGrid(pygame.sprite.OrderedUpdates):
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
		self.num_items_per_page = self.calc_num_items_per_page()
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
		
		self.set_num_items_per_page(self.calc_num_items_per_page())
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
		item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding
		
		#self.screen.fill(self.cfg.options.background_color, self.style.selection.rect)
		self.screen.blit(self.cfg.options.pre_loaded_background, self.selection.rect, pygame.Rect(self.selection.rect[0], self.selection.rect[1], item_width, self.cfg.options.item_height))
			
		selection = pygame.sprite.RenderPlain((self.selection))
		selection.draw(self.screen)
		return self.selection.rect
	
	def draw_items(self):
		padding = self.cfg.options.padding
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding

		x = padding
		y = self.cfg.options.header_height + padding
		i = 1

		sprites = self.sprites()
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
		
		self.clear(self.screen, self.cfg.options.pre_loaded_background)
		self.draw(self.screen)
		
	def set_selected_index(self, new_selected_index, play_sound = True):
		if play_sound: self.cfg.options.menu_move_sound.play()
		
		self.update_display.append(self.erase_selection())
		num_menu_items = len(self.sprites())

		if new_selected_index < 0:
			new_selected_index = 0
		elif new_selected_index >= num_menu_items:
			new_selected_index = num_menu_items - 1

		self.selected_index = new_selected_index
		#self.selection.clear(self.screen)
		self.selection.update(self.get_selected_item())
		#self.draw_items()
		self.update_display.append(self.draw_selection())
	
	def calc_num_items_per_page(self):
		padding = self.cfg.options.padding
		avail_height = pygame.display.Info().current_h - self.cfg.options.header_height - padding * 2
		item_height = self.cfg.options.item_height + padding
		
		#trap the case where item_height in theme.yaml is larger than the available space 		
		if item_height > avail_height:
			item_height = avail_height
		
		num_rows = avail_height / item_height

		return num_rows * self.cfg.options.num_items_per_row

	def get_selected_item(self):
		try:
			return self.sprites()[self.selected_index]
		except:
			return 0
			
	def create_nav_menu_item(self, label, icon_file = False, icon_selected = False):
		item = {}
		item['id'] = -1
		item['label'] = '' if not self.cfg.options.display_navigation_labels else label
		item['type'] = PMMenuItem.NAVIGATION
		item['visible'] = True
		item['icon_file'] = self.cfg.options.theme_pack + icon_file
		item['icon_selected'] = self.cfg.options.theme_pack + icon_selected
		item['command'] = ''
		item['rom_path'] = ''
		item['include_full_path'] = False
		item['include_extension'] = False
		item['scraper_id'] = None
		item['icon_id'] = None
		item['override_menu'] = False
		item['display_label'] = self.cfg.options.display_navigation_labels
		item['banner'] = None

		menu_item = PMMenuItem(item, self.cfg)

		return menu_item

	def set_num_items_per_page(self, n):
		self.num_items_per_page = n

		# create pages
		self.pages = []

		num_menu_items = len(self.menu_items)
		#total_num_of_icons = num_menu_items/num_items_per_page - 1(page) * (2 navigation buttons per page) + num_menu_items + 2 navigation buttons for first and last pages
		total_num_of_icons = (int(num_menu_items/self.num_items_per_page) - 1) * 2 + num_menu_items + 2
		total_num_of_pages = int(total_num_of_icons/self.num_items_per_page) + 1 #+1 b/c int always rounds down
		
		if total_num_of_pages == 1:
			self.pages.append(self.menu_items[:])
		else:
			num_items_to_display = self.num_items_per_page - 1
			page = self.menu_items[:num_items_to_display]
			next = self.create_nav_menu_item('Next', self.next_icon, self.next_selected)
			next.command = PMMenuItem.NEXT_PAGE
			page.append(next)
			self.pages.append(page)
			r = xrange(1, total_num_of_pages)
			iteration = 0
			for i in r:
				iteration += num_items_to_display
				num_items_to_display = self.num_items_per_page - 2
					
				page = self.menu_items[iteration: iteration + num_items_to_display]
				back = self.create_nav_menu_item('Back', self.back_icon, self.back_selected)
				back.command = PMMenuItem.PREV_PAGE
				next = self.create_nav_menu_item('Next', self.next_icon, self.next_selected)
				next.command = PMMenuItem.NEXT_PAGE
				page.insert(0, back)
				if i != len(r): page.append(next)
				self.pages.append(page)
				
			last_page = self.menu_items[self.num_items_per_page - 1 + len(r) * (self.num_items_per_page - 2):]
			back = self.create_nav_menu_item('Back', self.back_icon, self.back_selected)
			back.command = PMMenuItem.PREV_PAGE
			last_page.insert(0, back)
			self.pages.append(last_page)

		self.set_page(0)

	def set_page(self, page_index):
		self.page_index = page_index

		self.empty()
		self.add(self.pages[page_index])

	def next_page(self):
		self.set_page(self.page_index + 1)

	def prev_page(self):
		self.set_page(self.page_index - 1)

	def get_adjacent_item(self, item, direction):
		index = self.menu_items.index(item)
		adj_index = None

		if(direction == PMDirection.LEFT):
			adj_index = index - 1
		elif(direction == PMDirection.RIGHT):
			adj_index = index + 1
		elif(direction == PMDirection.TOP):
			adj_index = index - options.num_items_per_row
		elif(direction == PMDirection.BOTTOM):
			adj_index = index + options.num_items_per_row

		if adj_index == None:
			return None

		return self.menu_items[adj_index]
	
	def handle_events(self, action):
		#NAVIGATE MAIN MENU
		if action == 'LEFT':
			if self.selected_index == 0: 
				sprite = self.get_selected_item()
				if sprite.type == PMMenuItem.NAVIGATION:
					self.do_menu_item_action(sprite)
			else:
				self.set_selected_index(self.selected_index - 1)
		elif action == 'RIGHT':
			if self.selected_index == self.num_items_per_page - 1:    #zero based
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
			if self.selected_index == self.num_items_per_page - 1:    #zero based
				sprite = self.get_selected_item()
				if sprite.type == PMMenuItem.NAVIGATION:
					self.do_menu_item_action(sprite)
			else: 
				self.set_selected_index(self.selected_index + self.cfg.options.num_items_per_row)

			
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

			screen_width = pygame.display.Info().current_w
			item_width = ((screen_width - self.cfg.options.padding) / self.cfg.options.num_items_per_row) - self.cfg.options.padding

			self.image = pygame.Surface([item_width, self.cfg.options.item_height], pygame.SRCALPHA, 32).convert_alpha()

			
			item_rect = menu_item.rect
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
				if self.cfg.options.display_labels:
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
			self.rect.x = item_rect.x;
			self.rect.y = item_rect.y;


