import yaml
import pygame
from menuitem import *
from pmgrid import *

class PMCfg:
	def __init__(self):
	
		#load config file, use open() rather than file(), file() is deprecated in python 3.
		stream = open('/home/pi/pimame/pimame-menu/config.yaml', 'r')
		config = yaml.safe_load(stream)
		stream.close()
		
		#load theme file - use safe_load to make sure malicious code is not executed if hiding in theme.yaml
		stream = open('/home/pi/pimame/pimame-menu/themes/' +config['options']['theme_pack'] + "/theme.yaml", 'r')
		theme = yaml.safe_load(stream)
		stream.close()
		
		#roll config file + theme file into options class
		self.options = PMOptions(config['options'], theme['options'],config['menu_items'],theme['menu_items'])
		config = None
		theme = None
		
		self.screen = self.init_screen(self.options.resolution, self.options.fullscreen)
		
	def init_screen(self, size, fullscreen):
		pygame.init()
		#return pygame.display.set_mode(size,0,32)

		flag = 0
		if fullscreen:
			flag = pygame.FULLSCREEN

		return pygame.display.set_mode(size, flag)


class PMOptions:
	def __init__(self, opts, theme, opt_menu_item, theme_menu_item):
	
		#config.yaml
		for index, oItem in enumerate(opt_menu_item):
			match = next((tItem for tItem in theme_menu_item if tItem['label'].lower() == oItem['label'].lower()), None)
			if match is not None:
				opt_menu_item[index]['icon_file'] = match['icon_file']
				opt_menu_item[index]['icon_selected'] = match['icon_selected']
			else:
				opt_menu_item[index]['icon_file'] = theme['generic_menu_item']
				opt_menu_item[index]['icon_selected'] = theme['generic_menu_item_selected']
			
			
		self.options_menu_items = opt_menu_item
		
		self.max_fps = opts['max_fps']
		self.show_ip = opts['show_ip']
		self.show_update = opts['show_update']
		self.fullscreen = opts['fullscreen']
		self.resolution = self.get_screen_size(opts['resolution'])
		self.sort_items_alphanum = opts['sort_items_alphanum']
		self.sort_items_with_roms_first = opts['sort_items_with_roms_first']
		self.hide_items_without_roms = opts['hide_items_without_roms']
		self.theme_pack = "themes/" + opts['theme_pack'] + "/"
		
		#theme.yaml
		self.header_height = theme['header_height']
		self.header_color = self.get_color(theme['header_color'])
		self.logo_image = theme['logo_image']
		self.background_image = theme['background_image']
		self.background_color = self.get_color(theme['background_color'])
		self.generic_menu_item = self.theme_pack + theme['generic_menu_item']
		self.generic_menu_item_selected = self.theme_pack + theme['generic_menu_item_selected']
		self.item_color = self.get_color(theme['item_color'])
		self.disabled_alpha = theme['disabled_alpha']
		self.item_height = theme['item_height']
		self.num_items_per_row = theme['num_items_per_row']
		self.padding = theme['menu_item_padding']
		
		self.font_file = theme['font_file']
		self.default_font_size = theme['default_font_size']
		self.default_font_color = self.get_color(theme['default_font_color'])
		self.default_font_background_color = self.get_color(theme['default_font_background_color'])
		
		self.display_labels = theme['display_labels']
		self.labels_offset = theme['labels_offset']
		self.label_font_size = theme['label_font_size']
		self.label_font_color = self.get_color(theme['label_font_color'])
		self.label_background_color = self.get_color(theme['label_background_color'])
		self.label_font_selected_color = self.get_color(theme['label_font_selected_color'])
		self.label_background_selected_color = self.get_color(theme['label_background_selected_color'])
		
		self.display_rom_count = theme['display_rom_count']
		self.rom_count_offset = theme['rom_count_offset']
		self.rom_count_font_size = theme['rom_count_font_size']
		self.rom_count_font_color = self.get_color(theme['rom_count_font_color'])
		self.rom_count_background_color = self.get_color(theme['rom_count_background_color'])
		self.rom_count_font_selected_color = self.get_color(theme['rom_count_font_selected_color'])
		self.rom_count_background_selected_color = self.get_color(theme['rom_count_background_selected_color'])
		
		self.rom_list_font_size = theme['rom_list_font_size']
		self.rom_list_font_color = self.get_color(theme['rom_list_font_color'])
		self.rom_list_background_color = self.get_color(theme['rom_list_background_color'])
		self.rom_list_font_selected_color = self.get_color(theme['rom_list_font_selected_color'])
		self.rom_list_background_selected_color = self.get_color(theme['rom_list_background_selected_color'])
		self.rom_list_offset = {"left": theme['rom_list_offset'][0], "top": theme['rom_list_offset'][1], "right": theme['rom_list_offset'][2], "bottom": theme['rom_list_offset'][3]}
		

		#items to be pre-loaded for efficiency
		pygame.font.init()
		self.font = pygame.font.Font(self.theme_pack + self.font_file, self.default_font_size)
		self.label_font = pygame.font.Font(self.theme_pack + self.font_file, self.label_font_size)
		self.rom_count_font = pygame.font.Font(self.theme_pack + self.font_file, self.rom_count_font_size)
		self.rom_list_font = pygame.font.Font(self.theme_pack + self.font_file, self.rom_list_font_size)
		self.pre_loaded_background = self.load_image(self.theme_pack + self.background_image)
		self.pre_loaded_romlist = self.load_image(self.theme_pack + theme['rom_list_image'])
		self.pre_loaded_romlist_selected = self.load_image(self.theme_pack + theme['rom_list_selected_image'])
		self.romlist_item_height = max(self.pre_loaded_romlist.get_rect().h,self.rom_list_font.size('Ip')[1])


	def get_color(self, color_str):
		return tuple([int(x) for x in color_str.split(",")])

	def get_screen_size(self, res_str):
		return tuple([int(x) for x in res_str.split(",")])
		
	def load_image(self, file_path, alternate_image = None):
		try:
			return pygame.image.load(file_path)
		except:
			if alternate_image: 
				try:
					return pygame.image.load(alternate_image)
				except:
					print 'cant load: ', alternate_image
					return pygame.image.load('/home/pi/pimame/pimame-menu/assets/images/blank.png')
			print 'cant load: ', file_path
			return pygame.image.load('/home/pi/pimame/pimame-menu/assets/images/blank.png')
		


class PMDirection:
	LEFT = 0
	UP = 1
	RIGHT = 2
	DOWN = 3
