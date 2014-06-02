import thread, time
import pygame
from pmlist import *
from pmutil import *

class RomListScene(object):

	SCENE_NAME = 'romlist'
	
	DIRECTION_UP = 'up'
	DIRECTION_DOWN = 'down'
	DIRECTION_LEFT = 'left'
	DIRECTION_RIGHT = 'right'

	ORIENTATION = {'vertical':[DIRECTION_UP,DIRECTION_DOWN,DIRECTION_LEFT,DIRECTION_RIGHT],
						'horizontal': [DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_DOWN]}
						
	selected_item = None
	sprites = []
	
	boxart_thread = None

	def __init__(self, rom_list):
		super(RomListScene, self).__init__()
		self.rom_list = rom_list

	def resize_bg(self):

		background_rect = self.cfg.options.pre_loaded_rom_list_background.get_rect()
		screen_width = pygame.display.Info().current_w
		screen_height = pygame.display.Info().current_h
		scale = min(float(background_rect.w) / float(screen_width), float(background_rect.h) / float(screen_height))
		background_rect = (int(background_rect.w / scale), int(background_rect.h / scale))
		
		self.cfg.options.pre_loaded_rom_list_background =  pygame.transform.smoothscale(self.cfg.options.pre_loaded_rom_list_background, background_rect)

		self.screen.fill(self.cfg.options.background_color)
		self.screen.blit(self.cfg.options.pre_loaded_rom_list_background, (0,0))
	
	def draw_bg(self):
		self.screen.fill(self.cfg.options.background_color)
		self.screen.blit(self.cfg.options.pre_loaded_rom_list_background, (0,0))

	def pre_render(self, screen):
		
		self.resize_bg()
		self.list = PMList(self.rom_list, self.cfg.options)

		self.items_per_screen = int(self.measure_items_per_screen())
		self.list.set_visible_items(0, self.items_per_screen)

		self.selected_item = self.list.labels[0]

		self.draw()

	def measure_items_per_screen(self):
	
		item_size = self.cfg.options.romlist_item_height if not self.cfg.options.rom_list_orientation == 'horizontal' else self.cfg.options.romlist_item_width
		screen_size = pygame.display.Info().current_h  if not self.cfg.options.rom_list_orientation == 'horizontal' else pygame.display.Info().current_w
		
		alignment = {	'left': self.cfg.options.rom_list_alignment_padding, 
							'right': (pygame.display.Info().current_w - self.cfg.options.romlist_item_width - self.cfg.options.rom_list_alignment_padding), 
							'top': self.cfg.options.rom_list_alignment_padding,
							'bottom': (pygame.display.Info().current_h - self.cfg.options.romlist_item_height - self.cfg.options.rom_list_alignment_padding)
							}
							
		self.rom_list_align = alignment[self.cfg.options.rom_list_align]

		return screen_size / item_size

	def render(self, screen):
		pass

	def update(self):
		pass

	def handle_events(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()

				# get all rects under cursor
				clicked_sprites = [s for s in self.list if s.rect.collidepoint(pos)]
				
				if len(clicked_sprites) > 0:
					sprite = clicked_sprites[0]
					self.run_sprite_command(sprite)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP or event.key == pygame.K_KP8:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][0])
				elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][1])
				elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][2])
				elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][3])
				elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_KP_ENTER:
					self.run_sprite_command(self.selected_item)
				elif event.key == pygame.K_ESCAPE:
					self.manager.back()
			elif event.type == pygame.JOYAXISMOTION:
				if event.dict['axis'] == 1 and event.dict['value'] < 0:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][0])
				elif event.dict['axis'] == 1 and event.dict['value'] > 0:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][1])
				elif event.dict['axis'] == 0 and event.dict['value'] < 0:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][2])
				elif event.dict['axis'] == 0 and event.dict['value'] > 0:
					self.set_selected_index(self.ORIENTATION[self.cfg.options.rom_list_orientation][3])
			elif event.type == pygame.JOYBUTTONDOWN:
				if event.button == 0:
					self.run_sprite_command(self.selected_item)

	def set_selected_index(self, direction):
		#move selection up by 1
		if direction == self.DIRECTION_UP:
			selected_index = self.sprites.index(self.selected_item)
			#check if selected item is highest item on screen
			if selected_index == 0:
				#check to see if this is the very first rom. if not, then advance list upwards, otherwise do nothing
				if self.list.first_index > 0:
					#get the smaller number to determine how far to advance the list
					difference = min(self.list.first_index, len(self.list.labels))
					self.list.set_visible_items(self.list.first_index - difference, self.list.last_index - difference)
					self.selected_item = self.list.labels[len(self.list.labels)-1]
			else:
				#if not highest item on screen, just advance selection
				self.selected_item = self.sprites[selected_index - 1]
	
		#move selection down by 1
		elif direction == self.DIRECTION_DOWN:
			selected_index = self.sprites.index(self.selected_item)
			if selected_index == (len(self.list.labels)-1):
				if self.list.last_index < len(self.rom_list):
					difference = min(len(self.rom_list) - self.list.last_index + 1, len(self.list.labels))
					self.list.set_visible_items(self.list.first_index + difference, self.list.last_index + difference)
					self.selected_item = self.list.labels[0]
			else:
				self.selected_item = self.sprites[selected_index + 1]
				
		#move selection down by number of items on screen	
		elif direction == self.DIRECTION_RIGHT:
			selected_index = self.sprites.index(self.selected_item)
			if selected_index < int(self.items_per_screen/2):
				selected_index = min((self.items_per_screen/2),(len(self.list.labels)-1))
				self.selected_item = self.list.labels[selected_index]
			else:
				difference = min(len(self.rom_list) - self.list.last_index + 1, len(self.list.labels))
				self.list.set_visible_items(self.list.first_index + difference, self.list.last_index + difference)
				selected_index = min((self.items_per_screen/2),(len(self.list.labels)-1))
				self.selected_item = self.list.labels[selected_index]
				
		#move selection up by number of items on screen
		if direction == self.DIRECTION_LEFT:
			selected_index = self.sprites.index(self.selected_item)
			if selected_index > int(self.items_per_screen/2):
				selected_index = min((self.items_per_screen/2),(self.list.last_index - len(self.list.labels)))
				self.selected_item = self.list.labels[selected_index]
			else:
				difference = min(self.list.first_index, len(self.list.labels))
				self.list.set_visible_items(self.list.first_index - difference, self.list.last_index - difference)
				selected_index = min((self.items_per_screen/2),(self.list.last_index - len(self.list.labels)))
				self.selected_item = self.list.labels[selected_index]

		self.draw()

	def draw_list(self, orientation):
		if not orientation == 'horizontal':
			
			y = 0

			self.sprites = []
			
			for sprite in self.list.sprites():
				self.sprites.append(sprite)
				sprite.rect.x = self.rom_list_align
				sprite.rect.y = y

				y += sprite.rect.height

			self.list.draw(self.screen)
		else:
			available_width = pygame.display.Info().current_w - (self.items_per_screen * self.cfg.options.romlist_item_width)
			padding = available_width / (self.items_per_screen + 1)
			x = padding

			self.sprites = []
			
			for sprite in self.list.sprites():
				self.sprites.append(sprite)
				sprite.rect.y = self.rom_list_align
				sprite.rect.x = x

				x += sprite.rect.width + padding

			self.list.draw(self.screen)

	def draw_boxart(self, delay):
		for i in range(0, delay):
			time.sleep(.01)
			if thread.get_ident() != self.boxart_thread: thread.exit()
			
		
		boxart = self.cfg.options.load_image(self.selected_item.boxart, self.cfg.options.missing_boxart_image)
		boxart_rect = boxart.get_rect()
		avail_width = self.screen.get_width()
		avail_height = self.screen.get_height()
		
		if not self.cfg.options.rom_list_orientation == 'horizontal':
			avail_width = pygame.display.Info().current_w - self.cfg.options.romlist_item_width - self.cfg.options.rom_list_alignment_padding
		else:
			avail_height = pygame.display.Info().current_h - self.cfg.options.romlist_item_height - self.cfg.options.rom_list_alignment_padding
		
		scale = min(float((avail_width * self.cfg.options.boxart_max_width) / boxart_rect.w), float((avail_height * self.cfg.options.boxart_max_height) / boxart_rect.h))
		scale_size = (int(boxart_rect.w * scale), int(boxart_rect.h * scale))
		
		if thread.get_ident() != self.boxart_thread: thread.exit()
		
		#depending on type of file, either scale or smoothscale needs to be used
		try:
			boxart = pygame.transform.smoothscale(boxart, scale_size) 
		except:
			boxart = pygame.transform.scale(boxart, scale_size)
			
		boxart_location_x = 	((avail_width - scale_size[0])/2) + self.cfg.options.boxart_offset[0]
		boxart_location_y = ((avail_height - scale_size[1])/2) +  self.cfg.options.boxart_offset[1]
		if self.cfg.options.rom_list_align == 'left': boxart_location_x += self.cfg.options.romlist_item_width + self.cfg.options.rom_list_alignment_padding
		if self.cfg.options.rom_list_align == 'top': boxart_location_y += self.cfg.options.romlist_item_height + self.cfg.options.rom_list_alignment_padding
		boxart_location = (boxart_location_x, boxart_location_y)
		
		if self.manager.scene.SCENE_NAME == 'romlist': 
			self.screen.blit(boxart, boxart_location)
			if self.cfg.options.boxart_underlay: self.draw(False)
		else: thread.exit()
	
	def draw(self, draw_boxart = True):
		if draw_boxart:
			self.boxart_thread = thread.start_new_thread(self.draw_boxart, (20,))
			self.draw_bg()
		self.draw_list(self.cfg.options.rom_list_orientation)

		text = self.selected_item.text
		rect = self.selected_item.rect

		#rect.width = pygame.display.Info().current_w
		
		#build and draw selected item on the fly
		selected_romlist_image = self.cfg.options.pre_loaded_romlist_selected.convert_alpha()
		
		self.screen.fill(self.cfg.options.background_color, rect)
		self.screen.blit(self.cfg.options.pre_loaded_rom_list_background, rect, rect)

		selected_label = PMLabel(text, self.cfg.options.rom_list_font, self.cfg.options.rom_list_font_selected_color, self.cfg.options.rom_list_background_selected_color, self.cfg.options.rom_list_font_selected_bold, self.cfg.options.rom_list_offset, False, self.list.selected_rom_template, [], self.cfg.options.rom_list_font_align)

		self.screen.blit(selected_label.image, rect)
		
		

	def run_sprite_command(self, sprite):
		if(sprite.type == 'back'):
			self.manager.back()
		else:
			PMUtil.run_command_and_continue(sprite.command)
