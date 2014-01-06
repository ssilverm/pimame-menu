import yaml
import pygame
from menuitem import *
from pmgrid import *

class PMCfg:
	def __init__(self, config_path):
		stream = file('config.yaml', 'r')
		self.config = yaml.load(stream)

		self.options = PMOptions(self.config['options'])

		self.screen = self.init_screen(self.options.resolution, self.options.fullscreen)

	def init_screen(self, size, fullscreen):
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
		self.text_color = self.get_color(opts['text_color'])
		self.text_highlight_color = self.get_color(opts['text_highlight_color'])
		self.selection_color = self.get_color(opts['selection_color'])
		self.item_color = self.get_color(opts['item_color'])
		self.header_color = self.get_color(opts['header_color'])
		self.rom_dot_color = self.get_color(opts['rom_dot_color'])
		self.icon_pack_path = opts['icon_pack_path']
		self.font_size = opts['font_size']
		self.font_file = opts['font_file']
		self.sort_items_alphanum = opts['sort_items_alphanum']
		self.sort_items_with_roms_first = opts['sort_items_with_roms_first']
		self.hide_items_without_roms = opts['hide_items_without_roms']

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