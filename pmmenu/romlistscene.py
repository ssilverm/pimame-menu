import pygame
from pmlist import *
from pmutil import *

class RomListScene(object):

	DIRECTION_UP = 'up'
	DIRECTION_DOWN = 'down'
	DIRECTION_LEFT = 'left'
	DIRECTION_RIGHT = 'right'

	selected_item = None
	sprites = []

	def __init__(self, rom_list):
		super(RomListScene, self).__init__()
		#self.font = pygame.font.SysFont('Arial', 52)
		#self.sfont = pygame.font.SysFont('Arial', 32)
		self.rom_list = rom_list

	def draw_bg(self):
		self.screen.fill(self.cfg.options.background_color)
		background_image = self.cfg.options.pre_loaded_background
		self.screen.blit(background_image, (0,0))

	def pre_render(self, screen):

		self.list = PMList(self.rom_list, self.cfg.options)
		

		self.items_per_screen = self.measure_items_per_screen()
		self.list.set_visible_items(0, self.items_per_screen)

		self.selected_item = self.list.labels[0]

		self.draw()

	def measure_items_per_screen(self):
		item_height = self.cfg.options.romlist_item_height
		#item_height = self.list.labels[0].rect.height
		screen_height = pygame.display.Info().current_h

		return screen_height / item_height

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
					self.set_selected_index(self.DIRECTION_UP)
				elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
					self.set_selected_index(self.DIRECTION_DOWN)
				elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
					self.set_selected_index(self.DIRECTION_RIGHT)
				elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
					self.set_selected_index(self.DIRECTION_LEFT)
				elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_KP_ENTER:
					self.run_sprite_command(self.selected_item)
				elif event.key == pygame.K_ESCAPE:
					self.manager.back()
			elif event.type == pygame.JOYAXISMOTION:
				if event.dict['axis'] == 1 and event.dict['value'] < 0:
					self.set_selected_index(self.DIRECTION_UP)
				elif event.dict['axis'] == 1 and event.dict['value'] > 0:
					self.set_selected_index(self.DIRECTION_DOWN)
				elif event.dict['axis'] == 0 and event.dict['value'] < 0:
					self.set_selected_index(self.DIRECTION_LEFT)
				elif event.dict['axis'] == 0 and event.dict['value'] > 0:
					self.set_selected_index(self.DIRECTION_RIGHT)
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

	def draw_list(self):
		y = 0

		self.sprites = []

		for sprite in self.list.sprites():
			self.sprites.append(sprite)
			sprite.rect.x = 0
			sprite.rect.y = y

			y += sprite.rect.height

		self.list.draw(self.screen)

	def draw(self):
		self.draw_bg()
		self.draw_list()

		text = self.selected_item.text
		rect = self.selected_item.rect

		rect.width = pygame.display.Info().current_w

		#pygame.draw.rect(self.screen, self.cfg.options.rom_dot_color, rect)
		
		#build and draw selected item on the fly
		selected_romlist_image = self.cfg.options.pre_loaded_romlist_selected.convert_alpha()
		#rom_template = PMLabel('', self.cfg.options.rom_list_font, self.cfg.options.rom_list_font_selected_color, self.cfg.options.rom_list_background_selected_color, self.cfg.options.rom_list_offset, selected_romlist_image)
		selected_label = PMLabel(text, self.cfg.options.rom_list_font, self.cfg.options.rom_list_font_selected_color, self.cfg.options.rom_list_background_selected_color, self.cfg.options.rom_list_offset, False, self.list.selected_rom_template)

		self.screen.blit(selected_label.image, rect)

	def run_sprite_command(self, sprite):
		if(sprite.type == 'back'):
			self.manager.back()
		else:
			PMUtil.run_command_and_continue(sprite.command)
