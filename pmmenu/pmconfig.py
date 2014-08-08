import yaml
from os.path import isfile
from os import system
import pygame
from menuitem import *
from pmgrid import *

class PMCfg:
	def __init__(self):
		
		#clear command line for incoming error messages
		system('clear')
		#initialize sound mixer
		pygame.mixer.pre_init(22050, -16, 1, 1024)
		
		#load config file, use open() rather than file(), file() is deprecated in python 3.
		stream = open('/home/pi/pimame/pimame-menu/config.yaml', 'r')
		config = yaml.safe_load(stream)
		stream.close()
		
		#load theme file - use safe_load to make sure malicious code is not executed if hiding in theme.yaml
		stream = open('/home/pi/pimame/pimame-menu/themes/' +config['options']['theme_pack'] + '/theme.yaml', 'r')
		theme = yaml.safe_load(stream)
		stream.close()
		
		#load theme file - use safe_load to make sure malicious code is not executed if hiding in theme.yaml
		stream = open('/home/pi/pimame/pimame-menu/ks.yaml', 'r')
		self.ks = yaml.safe_load(stream)
		self.ks = sorted(self.ks)
		stream.close()
		
		#roll config file + theme file into options class
		self.options = PMOptions(config['options'], config['scraper_options'], theme['options'],config['menu_items'],theme['menu_items'])
		config = None
		theme = None
		
		self.screen = self.init_screen(self.options.resolution, self.options.fullscreen)
		self.screen.set_alpha(None)
		pygame.mouse.set_visible(self.options.show_cursor) 
		
		#loading screen
		background_image = self.options.load_image(self.options.loading_image, "/home/pi/pimame/pimame-menu/assets/images/loading_screen.png")
		background_rect = background_image.get_rect()
		screen_width = pygame.display.Info().current_w
		screen_height = pygame.display.Info().current_h
		scale = min(float(background_rect.w) / float(screen_width), float(background_rect.h) / float(screen_height))
		background_rect = (int(background_rect.w / scale), int(background_rect.h / scale))
		
		background_image = pygame.transform.smoothscale(background_image, background_rect)
		self.screen.blit(background_image, (0,0))
		pygame.display.flip()
		
		#resize main menu background image
		background_rect =  self.options.pre_loaded_background.get_rect()
		scale = min(float(background_rect.w) / float(screen_width), float(background_rect.h) / float(screen_height))
		background_rect = (int(background_rect.w / scale), int(background_rect.h / scale))
		
		self.options.pre_loaded_background =  pygame.transform.smoothscale(self.options.pre_loaded_background, background_rect)
		
		#resize rom list background image
		background_rect =  self.options.pre_loaded_rom_list_background.get_rect()
		scale = min(float(background_rect.w) / float(screen_width), float(background_rect.h) / float(screen_height))
		background_rect = (int(background_rect.w / scale), int(background_rect.h / scale))
		
		self.options.pre_loaded_rom_list_background =  pygame.transform.smoothscale(self.options.pre_loaded_rom_list_background, background_rect)
		
		#load audio
		self.options.menu_move_sound = self.options.load_audio(self.options.menu_move_sound)
		self.options.menu_select_sound = self.options.load_audio(self.options.menu_select_sound)
		self.options.menu_back_sound = self.options.load_audio(self.options.menu_back_sound)
		self.options.menu_navigation_sound = self.options.load_audio(self.options.menu_navigation_sound)
		
		#pre-load surfaces
		self.options.blur_image = pygame.Surface([screen_width, screen_height]).convert_alpha()
		self.options.fade_image = pygame.Surface([screen_width, screen_height]).convert()
		
		
		self.options.draw_rect = pygame.Surface([screen_width, screen_height], pygame.SRCALPHA)
		self.options.draw_rect.fill((0,0,0,0))
		self.options.draw_rect.convert()
		
		try:
			if self.options.boxart_border_color[3] == 0:
				self.options.draw_rect = None
			else:
				self.options.draw_rect.set_alpha(self.options.boxart_border_color[3])
		except:
			pass
		
	def init_screen(self, size, fullscreen):
		
		pygame.init()
		pygame.display.init()
		dinfo = pygame.display.Info()

		#return pygame.display.set_mode(size,0,32)
		pygame.display.init()
		dinfo = pygame.display.Info()


		flag = 0
		if fullscreen:
			flag = pygame.FULLSCREEN
		#return pygame.display.set_mode(size, flag, 32)

		if (pygame.display.mode_ok((dinfo.current_w,dinfo.current_h),pygame.FULLSCREEN)):
			return pygame.display.set_mode((dinfo.current_w, dinfo.current_h), flag)
		else:
			pygame.quit()
			sys.exit()


class PMOptions:
	def __init__(self, opts, scraper, theme, opt_menu_item, theme_menu_item):
	
		#config.yaml
		for index, oItem in enumerate(opt_menu_item):
			match = next((tItem for tItem in theme_menu_item if tItem['label'].lower() == oItem['label'].lower()), None)
			if match is not None:
				opt_menu_item[index]['icon_file'] = match['icon_file'] if ('icon_file' in match and match['icon_file']) else theme['generic_menu_item']
				opt_menu_item[index]['icon_selected'] = match['icon_selected'] if ('icon_selected' in match and match['icon_selected']) else theme['generic_menu_item_selected']
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
		self.hide_system_tools = opts['hide_system_tools']
		self.show_cursor = opts['show_cursor']
		self.allow_quit_to_console = opts['allow_quit_to_console']
		self.use_scene_transitions = opts['use_scene_transitions']
		self.theme_name = opts['theme_pack']
		self.theme_pack = "themes/" + opts['theme_pack'] + "/"
		
		#scraper options
		self.show_clones = scraper['show_clones']
		self.overwrite_images = scraper['overwrite_images']
		
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
		self.display_navigation_labels = theme['display_navigation_labels']
		
		self.menu_move_sound = self.theme_pack + theme['menu_move_sound']
		self.menu_select_sound = self.theme_pack + theme['menu_select_sound']
		self.menu_back_sound = self.theme_pack + theme['menu_back_sound']
		self.menu_navigation_sound = self.theme_pack + theme['menu_navigation_sound']
		
		self.loading_image = self.theme_pack + theme['loading_image']
		self.font_file = theme['font_file']
		self.default_font_size = theme['default_font_size']
		self.default_font_color = self.get_color(theme['default_font_color'])
		self.default_font_background_color = self.get_color(theme['default_font_background_color'])
		self.popup_menu_font_size = theme['popup_menu_font_size']
		self.popup_menu_font_color = self.get_color(theme['popup_menu_font_color'])
		self.popup_menu_font_selected_color = self.get_color(theme['popup_menu_font_selected_color'])
		self.popup_menu_background_color = self.get_color(theme['popup_menu_background_color'])
		
		self.display_labels = theme['display_labels']
		self.label_text_align = theme['label_text_align'].lower()
		self.labels_offset = theme['labels_offset']
		self.label_font_size = theme['label_font_size']
		self.label_font_color = self.get_color(theme['label_font_color'])
		self.label_font_bold = theme['label_font_bold']
		self.label_background_color = self.get_color(theme['label_background_color'])
		self.label_font_selected_color = self.get_color(theme['label_font_selected_color'])
		self.label_font_selected_bold = theme['label_font_selected_bold']
		self.label_background_selected_color = self.get_color(theme['label_background_selected_color'])
		self.label_max_text_width = self.check_type(theme['label_max_text_width'])
		
		self.display_rom_count = theme['display_rom_count']
		self.rom_count_text_align = theme['rom_count_text_align'].lower()
		self.rom_count_offset = theme['rom_count_offset']
		self.rom_count_font_size = theme['rom_count_font_size']
		self.rom_count_font_color = self.get_color(theme['rom_count_font_color'])
		self.rom_count_font_bold = theme['rom_count_font_bold']
		self.rom_count_background_color = self.get_color(theme['rom_count_background_color'])
		self.rom_count_font_selected_color = self.get_color(theme['rom_count_font_selected_color'])
		self.rom_count_font_selected_bold = theme['rom_count_font_selected_bold']
		self.rom_count_background_selected_color = self.get_color(theme['rom_count_background_selected_color'])
		self.rom_count_max_text_width = self.check_type(theme['rom_count_max_text_width'])
		
		self.rom_list_font_size = theme['rom_list_font_size']
		self.rom_list_font_align = theme['rom_list_font_align'].lower()
		self.rom_list_font_color = self.get_color(theme['rom_list_font_color'])
		self.rom_list_background_color = self.get_color(theme['rom_list_background_color'])
		self.rom_list_font_bold = theme['rom_list_font_bold']
		self.rom_list_font_selected_color = self.get_color(theme['rom_list_font_selected_color'])
		self.rom_list_font_selected_bold = theme['rom_list_font_selected_bold']
		self.rom_list_background_selected_color = self.get_color(theme['rom_list_background_selected_color'])
		self.rom_list_background_image = theme['rom_list_background_image']
		self.rom_list_offset = {"left": theme['rom_list_offset'][0], "top": theme['rom_list_offset'][1], "right": theme['rom_list_offset'][2], "bottom": theme['rom_list_offset'][3]}
		self.rom_list_align = theme['rom_list_align'].lower()
		self.rom_list_alignment_padding = int(theme['rom_list_alignment_padding'])
		self.rom_list_orientation = theme['rom_list_orientation'].lower() if theme['rom_list_orientation'].lower() == 'horizontal' else 'vertical'
		self.rom_list_max_text_width = self.check_type(theme['rom_list_max_text_width'])
		
		self.boxart_offset = theme['boxart_offset']
		self.boxart_max_width = float(theme['boxart_max_width'].strip('%'))/100
		self.boxart_max_height = float(theme['boxart_max_height'].strip('%'))/100
		self.boxart_border_thickness = theme['boxart_border_thickness']
		self.boxart_border_padding = theme['boxart_border_padding']
		self.boxart_border_color = self.get_color(theme['boxart_border_color'])
		

		#items to be pre-loaded for efficiency
		pygame.font.init()
		self.fade_image = None
		self.draw_rect = None
		self.blank_image = pygame.image.load('/home/pi/pimame/pimame-menu/assets/images/blank.png')
		self.font = pygame.font.Font(self.theme_pack + self.font_file, self.default_font_size)
		self.popup_font = pygame.font.Font(self.theme_pack + self.font_file, self.popup_menu_font_size)
		self.popup_rom_letter_font = pygame.font.Font(self.theme_pack + self.font_file, 125)
		self.label_font = pygame.font.Font(self.theme_pack + self.font_file, self.label_font_size)
		self.rom_count_font = pygame.font.Font(self.theme_pack + self.font_file, self.rom_count_font_size)
		self.rom_list_font = pygame.font.Font(self.theme_pack + self.font_file, self.rom_list_font_size)
		self.pre_loaded_background = self.load_image(self.theme_pack + self.background_image)
		self.pre_loaded_romlist = self.load_image(self.theme_pack + theme['rom_list_item_image'])
		self.pre_loaded_romlist_selected = self.load_image(self.theme_pack + theme['rom_list_item_selected_image'])
		self.pre_loaded_rom_list_background = self.load_image(self.theme_pack + self.rom_list_background_image)
		
		#determine romlist item height
		self.romlist_item_height = max(self.pre_loaded_romlist.get_rect().h, self.rom_list_font.size('')[1])
		if self.check_type(theme['rom_list_min_background_height']): self.romlist_item_height = max(self.romlist_item_height, theme['rom_list_min_background_height'])
		
		#determine romlist item width
		if str(theme['rom_list_min_background_width']).lower() == 'auto' : self.romlist_item_width = max(self.pre_loaded_romlist.get_rect().w, 300)
		else: self.romlist_item_width = max(self.pre_loaded_romlist.get_rect().w, int(theme['rom_list_min_background_width']))
		
		self.missing_boxart_image = (self.theme_pack + theme['missing_boxart_image']) if isfile(self.theme_pack + theme['missing_boxart_image']) else ('/home/pi/pimame/pimame-menu/assets/images/missing_boxart.png')
		

	def get_color(self, color_str):
		return tuple([int(x) for x in color_str.split(",")])

	def get_screen_size(self, res_str):
		return tuple([int(x) for x in res_str.split(",")])
	
	#test if number value or string (ie - string = 'auto')
	def check_type(self, input):
		try:
			input += 1
			return (input - 1)
		except TypeError:
			return False
		
	def load_image(self, file_path, alternate_image = None):
		try:
			return pygame.image.load(file_path)
		except:
			if alternate_image: 
				try:
					return pygame.image.load(alternate_image)
				except:
					print 'cant load image: ', alternate_image
					return self.blank_image
			print 'cant load image: ', file_path
			return self.blank_image
			
	def load_audio(self, file_path):
		if isfile(file_path):
			sound_file = pygame.mixer.Sound(file_path)
			sound_file.set_volume(1.0)
			return sound_file
		else:
			print 'cant load audio: ', file_path
			return pygame.mixer.Sound('/home/pi/pimame/pimame-menu/assets/audio/blank.wav')
		


class PMDirection:
	LEFT = 0
	UP = 1
	RIGHT = 2
	DOWN = 3
