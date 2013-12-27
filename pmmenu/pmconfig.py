import yaml
import pygame
from menuitem import *

class PMCfg:
	def __init__(self, config_path):
		stream = file('config.yaml', 'r')
		self.config = yaml.load(stream)

		self.options = PMOptions(self.config['options'])

		self.screen = self.init_screen(self.options.resolution, self.options.fullscreen)

		self.menu_items = PMMenuItems(self.config['menu_items'], self.options)

	def init_screen(self, size, fullscreen):
		print size
		pygame.init()
		#return pygame.display.set_mode(size,0,32)

		flag = 0
		if fullscreen:
			flag = pygame.FULLSCREEN

		return pygame.display.set_mode(size, flag)


class PMOptions:
	def __init__(self, opts):
		self.max_fps = opts['max_fps']
		self.show_ip = opts['show_ip']
		self.fullscreen = opts['fullscreen']
		self.num_items_per_row = opts['num_items_per_row']
		self.resolution = self.get_screen_size(opts['resolution'])
		self.item_height = opts['item_height']
		self.padding = opts['padding']
		self.selection_size = opts['selection_size']
		self.header_height = opts['header_height']
		self.background_color = self.get_color(opts['background_color'])
		self.selection_color = self.get_color(opts['selection_color'])
		self.item_color = self.get_color(opts['item_color'])
		self.header_color = self.get_color(opts['header_color'])
		self.rom_dot_color = self.get_color(opts['rom_dot_color'])
		self.icon_pack_path = opts['icon_pack_path']
		self.font_size = opts['font_size']
		self.font_file = opts['font_file']

		pygame.font.init()
		self.font = pygame.font.Font(self.font_file, self.font_size)

		#self.item_width = ((self.resolution[0] - self.padding) / self.num_items_per_row) - self.padding

	def get_color(self, color_str):
		return tuple([int(x) for x in color_str.split(",")])

	def get_screen_size(self, res_str):
		return tuple([int(x) for x in res_str.split(",")])


class PMDirection:
	LEFT = 0
	UP = 1
	RIGHT = 2
	DOWN = 3


# class PMMenuItem(pygame.sprite.Sprite):
# 	def __init__(self, opts):
# 		pygame.sprite.Sprite.__init__(self)


#@TODO - change to menu item collection
class PMMenuItems(pygame.sprite.OrderedUpdates):
	#menu_items = []
	# menu_items_by_sprite = None
	options = None

	def __init__(self, menu_item_cfgs, opts):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.options = opts

		for menu_item in menu_item_cfgs:
			pm_menu_item = PMMenuItem(menu_item, opts)
			self.add(pm_menu_item)

	# def get_item_having_sprite(self, sprite):
	# 	#return self.menu_items_by_sprite[self.get_sprite_pos(sprite)]
	# 	if self.menu_items_by_sprite == None:
	# 		self.menu_items_by_sprite = {}

	# 		for menu_item in self.menu_items:
	# 			self.menu_items_by_sprite[self.get_sprite_pos(menu_item.sprite)] = menu_item

	# 	return self.menu_items_by_sprite[self.get_sprite_pos(sprite)]

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

