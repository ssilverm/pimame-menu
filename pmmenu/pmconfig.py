import yaml
import sys
import os.path
from os import system
import pygame
from menuitem import *
import sqlite3

class PMCfg:
	def __init__(self):
		
		#clear command line for incoming error messages
		system('clear')
		
		#initialize sound mixer
		system("alsactl --file ~/pimame/config/piplay-sound.state restore")
		pygame.mixer.pre_init(44100, -16, 1, 2048)
		
		path = os.path.realpath('/home/pi/pimame/pimame-menu/database/config.db')
		self.config_db = sqlite3.connect(path)
		self.config_cursor = self.config_db.cursor()
		
		path = os.path.realpath('/home/pi/pimame/pimame-menu/database/local.db')
		self.local_db = sqlite3.connect(path)
		self.local_cursor = self.local_db.cursor()
		
		self.local_cursor.execute('CREATE TABLE IF NOT EXISTS local_roms'  + 
		' (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, system INTEGER, title TEXT, search_terms TEXT, parent TEXT, cloneof TEXT, release_date TEXT, overview TEXT, esrb TEXT, genres TEXT,' +
		' players TEXT, coop TEXT, publisher TEXT, developer TEXT, rating REAL, command TEXT, rom_file TEXT, rom_path TEXT, image_file TEXT, number_of_runs INTEGER, flags TEXT)')
		self.local_db.commit()
		
		path = os.path.realpath('/home/pi/pimame/pimame-menu/database/games_master.db')
		self.platform_db = sqlite3.connect(path)
		self.platform_cursor = self.platform_db.cursor()
		
		config = {'options':None, 'menu_items':None}
		keys = [item[1] for item in self.config_cursor.execute('PRAGMA table_info(options)').fetchall()]
		values = self.config_cursor.execute('SELECT * FROM options').fetchone()
		config['options'] = dict(zip(keys,values))
		
		keys = [item[1] for item in self.config_cursor.execute('PRAGMA table_info(menu_items)').fetchall()]
		values = self.config_cursor.execute('SELECT * FROM menu_items').fetchall()
		config['menu_items'] = [dict(zip(keys,value)) for value in values]
		
		#DEPRECATED
		#stream = open('/home/pi/pimame/pimame-menu/config.yaml', 'r')
		#config = yaml.safe_load(stream)
		#stream.close()
		
		#load theme file - use safe_load to make sure malicious code is not executed if hiding in theme.yaml
		stream = open('/home/pi/pimame/pimame-menu/themes/' +config['options']['theme_pack'] + '/theme.yaml', 'r')
		theme = yaml.safe_load(stream)
		stream.close()
		
		#roll config file + theme file into options class
		self.options = PMOptions(config['options'], theme['options'],config['menu_items'],theme['menu_items'])
		self.screen = self.init_screen(config['options']['resolution'], config['options']['fullscreen'])
		self.screen.set_alpha(None)
		pygame.mouse.set_visible(self.options.show_cursor) 
		config = None
		theme = None
		
		
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
		
		#resize favorite icon
		scale_size = self.options.rom_list_favorite_icon.get_rect()
		scale_size = (self.options.romlist_item_height, self.options.romlist_item_height)
		try: self.options.rom_list_favorite_icon = pygame.transform.smoothscale(self.options.rom_list_favorite_icon, scale_size).convert_alpha()
		except: self.options.rom_list_favorite_icon = pygame.transform.scale(self.options.rom_list_favorite_icon, scale_size).convert_alpha()
		self.options.rom_list_favorite_icon_rect = self.options.rom_list_favorite_icon.get_rect()
		
		#resize main menu background image
		background_rect =  self.options.pre_loaded_background.get_rect()
		scale = min(float(background_rect.w) / float(screen_width), float(background_rect.h) / float(screen_height))
		background_rect = (int(background_rect.w / scale), int(background_rect.h / scale))

		self.options.pre_loaded_background =  pygame.transform.smoothscale(self.options.pre_loaded_background, background_rect).convert()
		
		#resize rom list background image
		background_rect =  self.options.pre_loaded_rom_list_background.get_rect()
		scale = min(float(background_rect.w) / float(screen_width), float(background_rect.h) / float(screen_height))
		background_rect = (int(background_rect.w / scale), int(background_rect.h / scale))
		
		self.options.pre_loaded_rom_list_background =  pygame.transform.smoothscale(self.options.pre_loaded_rom_list_background, background_rect).convert()
		
		#load audio
		self.options.menu_move_sound = self.options.load_audio(self.options.menu_move_sound)
		self.options.menu_select_sound = self.options.load_audio(self.options.menu_select_sound)
		self.options.menu_back_sound = self.options.load_audio(self.options.menu_back_sound)
		self.options.menu_navigation_sound = self.options.load_audio(self.options.menu_navigation_sound)
		
		#load music, only stream if music volume > 0
		pygame.mixer.music.set_volume(self.options.default_music_volume)
		if self.options.menu_music: 
			pygame.mixer.music.load(self.options.menu_music)
			if self.options.default_music_volume: pygame.mixer.music.play(-1)
		
		#pre-load surfaces
		self.options.blur_image = pygame.Surface([screen_width, screen_height]).convert_alpha()
		self.options.fade_image = pygame.Surface([screen_width, screen_height]).convert()
		
	def load_ks(self):
		#load kickstarter names when called
		self.ks = [item[0] for item in self.config_cursor.execute('SELECT name FROM kickstarter_backers ORDER BY name ASC').fetchall()]
		self.ks.insert(0,"Thanks to all of our generous Kickstarter Backers!")
		
	def init_screen(self, size, fullscreen):

		pygame.init()
		pygame.display.init()
		dinfo = pygame.display.Info()
		size = tuple( int(x) for x in size.split(',') )
		#return pygame.display.set_mode(size,0,32)
		pygame.display.init()
		dinfo = pygame.display.Info()


		flag = 0
		if fullscreen:
			flag = pygame.FULLSCREEN
		#return pygame.display.set_mode(size, flag, 32)

		if (pygame.display.mode_ok((dinfo.current_w, dinfo.current_h),pygame.FULLSCREEN)):
			return pygame.display.set_mode(size, flag)
		else:
			pygame.quit()
			sys.exit()


class PMOptions:
	def __init__(self, opts, theme, opt_menu_items, theme_menu_items):
	
	
		self.theme_name = opts['theme_pack']
		self.theme_style = theme['theme_style'] if 'theme_style' in theme else 'grid'
		
		self.theme_pack = "themes/" + opts['theme_pack'] + "/"
		
		

		#Assign icons from theme if not assigned in config
		for index, item in enumerate(opt_menu_items):
			#assign theme icons
			opt_menu_items[index]['display_label'] = theme['display_labels']
			
			if item['icon_id'] in theme_menu_items:
				#let theme set label to blank on case by case basis
				if not theme_menu_items[item['icon_id']]['label']:
					opt_menu_items[index]['display_label'] = False
				else:
					opt_menu_items[index]['label'] = theme_menu_items[item['icon_id']]['label']
				if theme_menu_items[item['icon_id']]['icon_file']:
					opt_menu_items[index]['icon_file'] = self.theme_pack + theme_menu_items[item['icon_id']]['icon_file']
				if theme_menu_items[item['icon_id']]['icon_selected']:
					opt_menu_items[index]['icon_selected'] = self.theme_pack + theme_menu_items[item['icon_id']]['icon_selected']
				
				try: opt_menu_items[index]['banner'] = (self.theme_pack + theme_menu_items[item['icon_id']]['banner'])
				except TypeError: opt_menu_items[index]['banner'] = None
				
			#if icons not specified by theme or menu_items table, then use theme generic icon
			if not opt_menu_items[index]['icon_file']: 
				opt_menu_items[index]['icon_file'] =  self.theme_pack + theme['generic_menu_item']
			if not opt_menu_items[index]['icon_selected']: 
				opt_menu_items[index]['icon_selected'] =  self.theme_pack + theme['generic_menu_item_selected']


		self.options_menu_items = opt_menu_items
		
		self.max_fps = opts['max_fps']
		self.show_ip = opts['show_ip']
		self.show_update = opts['show_update']
		self.sort_items_alphanum = opts['sort_items_alphanum']
		self.sort_items_with_roms_first = opts['sort_items_with_roms_first']
		self.hide_emulators = opts['hide_emulators_with_no_roms']
		self.hide_system_tools = opts['hide_system_tools']
		self.show_cursor = opts['show_cursor']
		self.allow_quit_to_console = opts['allow_quit_to_console']
		self.use_scene_transitions = opts['use_scene_transitions']
		self.default_music_volume = max(float(opts['default_music_volume']) , 0.0)
		self.first_run = opts['first_run']
		
		#romlist options
		self.show_clones = opts['show_rom_clones']
		self.show_unmatched_roms = opts['show_unmatched_roms']
		self.rom_sort_category = opts['sort_roms_by'].lower()
		self.rom_sort_order = 'des' if 'des' in opts['rom_sort_order'].lower() else 'asc'
		self.rom_filter = opts['filter_roms_by'].lower() if opts['filter_roms_by'] else 'all'
		
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
		try: self.menu_music = self.theme_pack + theme['menu_music']
		except: self.menu_music = None
		
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
		self.rom_list_favorite_icon = self.load_image(self.theme_pack + theme['rom_list_favorite_icon'], 'assets/images/star.png')
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
		self.rom_list_padding = int(theme['rom_list_padding'])
		self.rom_list_max_text_width = self.check_type(theme['rom_list_max_text_width'])
		
		self.boxart_offset = theme['boxart_offset']
		self.boxart_max_width = float(theme['boxart_max_width'].strip('%'))/100
		self.boxart_max_height = float(theme['boxart_max_height'].strip('%'))/100
		self.boxart_background_color = self.get_color(theme['boxart_background_color'])
		self.boxart_border_thickness = theme['boxart_border_thickness']
		self.boxart_border_color = self.get_color(theme['boxart_border_color'])
		  
		self.info_font_file = theme['info_font_file']
		self.info_font_size = theme['info_font_size']
		self.info_font_color = self.get_color(theme['info_font_color'])
		self.info_bg1 = self.get_color(theme['info_extras_background_color'])
		self.info_bg2 = self.get_color(theme['info_overview_background_color'])
		self.info_border_color = self.get_color(theme['info_border_color'])
		self.info_border_thickness = theme['info_border_thickness']
		

		#items to be pre-loaded for efficiency
		pygame.font.init()
		self.fade_image = None
		self.draw_rect = None
		self.blank_image = pygame.Surface((1,1), pygame.SRCALPHA, 32)#pygame.image.load(os.path.realpath('/home/pi/pimame/pimame-menu/assets/images/blank.png'))
		
		self.font = pygame.font.Font(self.theme_pack + self.font_file, self.default_font_size)
		self.popup_font = pygame.font.Font(self.theme_pack + self.font_file, self.popup_menu_font_size)
		self.popup_rom_letter_font = pygame.font.Font(self.theme_pack + self.font_file, 25)
		self.label_font = pygame.font.Font(self.theme_pack + self.font_file, self.label_font_size)
		self.rom_count_font = pygame.font.Font(self.theme_pack + self.font_file, self.rom_count_font_size)
		self.rom_list_font = pygame.font.Font(self.theme_pack + self.font_file, self.rom_list_font_size)
		self.info_font = pygame.font.Font(self.theme_pack + self.info_font_file, self.info_font_size)
		
		self.pre_loaded_background = self.load_image(self.theme_pack + self.background_image)
		self.pre_loaded_romlist = self.load_image(self.theme_pack + theme['rom_list_item_image'])
		self.pre_loaded_romlist_selected = self.load_image(self.theme_pack + theme['rom_list_item_selected_image'])
		self.pre_loaded_rom_list_background = self.load_image(self.theme_pack + self.rom_list_background_image)
		
	
		if not self.background_image:
			self.pre_loaded_background = pygame.Surface([100,100], pygame.SRCALPHA, 32)
			self.pre_loaded_background.fill(self.background_color)
		
		if not self.rom_list_background_image:
			self.pre_loaded_rom_list_background = pygame.Surface([100,100], pygame.SRCALPHA, 32)
			self.pre_loaded_rom_list_background.fill(self.background_color)
		
		#determine romlist item height
		self.romlist_item_height = max(self.pre_loaded_romlist.get_rect().h, self.rom_list_font.size('')[1])
		if self.check_type(theme['rom_list_min_background_height']): self.romlist_item_height = max(self.romlist_item_height, theme['rom_list_min_background_height'])
		
		#determine romlist item width
		if str(theme['rom_list_min_background_width']).lower() == 'auto' : self.romlist_item_width = max(self.pre_loaded_romlist.get_rect().w, 300)
		else: self.romlist_item_width = max(self.pre_loaded_romlist.get_rect().w, int(theme['rom_list_min_background_width']))
		
		self.missing_boxart_image = (self.theme_pack + theme['missing_boxart_image']) if os.path.isfile(self.theme_pack + theme['missing_boxart_image']) else (os.path.realpath('/home/pi/pimame/pimame-menu/assets/images/missing_boxart.png'))
		

	def get_color(self, color_str):
		return tuple([int(x) for x in color_str.split(",")])
	
	#test if number value or string (ie - string = 'auto')
	def check_type(self, input):
		try:
			input += 1
			return (input - 1)
		except TypeError:
			return False
		
	def load_image(self, file_path, alternate_image = None, verbose = False):
		try:
			if os.path.splitext(file_path)[1] != "":
				return pygame.image.load(file_path)
			else:
				try:
					return pygame.image.load(os.path.join(file_path, '.jpg'))
				except:
					return pygame.image.load(os.path.join(file_path, '.png'))
		except:
			if alternate_image: 
				try:
					return pygame.image.load(alternate_image)
				except:
					if alternate_image and os.path.splitext(alternate_image)[1] != "":
						print 'cant load image: ', alternate_image
						
					if verbose: return None
					return self.blank_image.copy()
					
		if verbose: return None
		return self.blank_image.copy()
			
	def load_audio(self, file_path):
		if os.path.isfile(file_path):
			sound_file = pygame.mixer.Sound(file_path)
			sound_file.set_volume(1.0)
			return sound_file
		else:
			print 'cant load audio: ', file_path
			return pygame.mixer.Sound(os.path.realpath('/home/pi/pimame/pimame-menu/assets/audio/blank.wav'))
		


class PMDirection:
	LEFT = 0
	UP = 1
	RIGHT = 2
	DOWN = 3
