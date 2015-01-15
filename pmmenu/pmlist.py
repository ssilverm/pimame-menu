import os
import pygame
from romitem import *


class PMList(pygame.sprite.OrderedUpdates):
	labels = []

	def __init__(self, rom_data, cfg, get_labels = False):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.cfg = cfg
		self.first_index = self.last_index = 0
		self.labels = []
		self.icon_id = rom_data['icon_id']
		
		#rom_list contains -> id (of menu item that called it), scraper_id, list
		self.rom_data = rom_data
		self.rom_list = self.rom_data['list']
		
		platform = self.cfg.platform_cursor.execute('SELECT id, title, overview, release_date FROM system_id where id=?', (self.rom_data['scraper_id'],)).fetchone()
		
		try: self.back_item = {'type': 'back', 'id': platform[0], 'title': str(platform[1]), 'image_file': '/home/pi/pimame/pimame-menu/assets/images/' + str(platform[0]) + '.png', 'command': None,
							'release_date': platform[3], 'overview': platform[2], 'esrb': '', 'genres': '', 'players':'', 'coop':'', 'publisher': '', 'developer': '', 'rating': '', 'rom_file': '', 'number_of_runs': 0, 'flags':'display_platform'}
		
		except: self.back_item = {'type': 'back', 'id': '', 'title': str(''), 'image_file': '/home/pi/pimame/pimame-menu/assets/images/' + str('') + '.png', 'command': None,
							'release_date': '', 'overview': '', 'esrb': '', 'genres': '', 'players':'', 'coop':'', 'publisher': '', 'developer': '', 'rating': '', 'rom_file': '', 'number_of_runs': 0, 'flags':'display_platform'}
		
		self.rom_list.insert(0, self.back_item)
		
		#get pre-loaded (unselected) rom list image
		create_romlist_image = self.cfg.options.pre_loaded_romlist
		create_romlist_selected = self.cfg.options.pre_loaded_romlist_selected
		
		#make sure each romlist item reaches minimum sizes
		min_scale_size = [self.cfg.options.romlist_item_width, self.cfg.options.romlist_item_height]
		
		#Create rom list surface/image with no text
		self.rom_template = PMRomItem('', self.cfg, create_romlist_image, min_scale_size = min_scale_size)
		self.selected_rom_template = PMRomItem('', self.cfg, create_romlist_selected, min_scale_size = min_scale_size)
		self.selected_rom_template.toggle_selection()
		
		if get_labels: self.build_labels(self.rom_list)
	
	def requery_database(self):
		keys = [item[1] for item in  self.cfg.local_cursor.execute('PRAGMA table_info(local_roms)').fetchall()]
		#basic query
		query = 'SELECT * FROM local_roms where system = {pid}'.format(pid = self.rom_data['id'] if self.rom_data['id'] else -999)
		
		#filter genres
		if self.cfg.options.rom_filter.lower() != 'all' : query += ' AND genres LIKE "%{genre_filter}%"'.format(genre_filter = self.cfg.options.rom_filter)
		
		#exclude clones
		if not self.cfg.options.show_clones: query += ' AND cloneof is NULL'
		
		#hide unmatched roms
		if not self.cfg.options.show_unmatched_roms: query += ' AND (flags is null or flags not like "%no_match%")'
		
		#order by category
		query += ' ORDER BY {sort_category} {sort_order}, title ASC'.format(sort_category = self.cfg.options.rom_sort_category.lower(), sort_order = 'DESC' if 'des' in self.cfg.options.rom_sort_order.lower() else 'ASC')
		
		#if favorites category, change query
		if self.icon_id == 'FAVORITE': 
			query = "SELECT * FROM local_roms WHERE flags like '%favorite%' ORDER BY {sort_category} {sort_order}, title ASC".format(
							sort_category = self.cfg.options.rom_sort_category.lower(), sort_order = 'DESC' if 'des' in self.cfg.options.rom_sort_order.lower() else 'ASC')

		values = self.cfg.local_cursor.execute(query).fetchall()

		return [dict(zip(keys,value)) for value in values]
	
	def sort_list(self):
		
		self.rom_list = self.requery_database()
		self.rom_list.insert(0, self.back_item)
	
	def build_labels(self, rom_list):
		#Get rom title and blit to already created rom_template
		self.labels = []
		self.labels = map(lambda x: PMRomItem(x, self.cfg, new_rom = True), rom_list)
		#append = self.labels.append
		#for list_item in rom_list:
		#	label = PMRomItem(list_item, self.cfg, self.cfg.options.rom_list_font, self.cfg.options.rom_list_font_color, self.cfg.options.rom_list_background_color, self.cfg.options.rom_list_font_bold, self.cfg.options.rom_list_offset, False, True, [], self.cfg.options.rom_list_font_align, self.cfg.options.rom_list_max_text_width)
		#	append(label)

	def set_visible_items(self, first_index, last_index):
		self.first_index = first_index
		self.last_index = last_index
	
		self.empty()
		self.build_labels(self.rom_list[first_index:last_index])
		self.add(self.labels)