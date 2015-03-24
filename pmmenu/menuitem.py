
#TODO: fix alpha for unused emulators
import os
from os import listdir, system
from os.path import isfile, isdir, join, splitext, basename
import pygame
from pmlabel import *
import json

			
class PMMenuItem(pygame.sprite.Sprite):
	EMULATOR = 'EMULATOR'
	COMMAND = 'COMMAND'
	NAVIGATION = 'NAV'
	NEXT_PAGE = 'NEXT'
	PREV_PAGE = 'PREV'

	num_roms = 0
	has_rom_folder = False

	def __init__(self, menu_item, cfg, type = None):
		pygame.sprite.Sprite.__init__(self)
		
		self.cfg = cfg
		self.menu_item = menu_item
		self.id = self.menu_item['id']
		self.icon_id = self.menu_item['icon_id']
		self.display_label = self.menu_item['display_label']
		self.label = self.menu_item['label']
		self.command = self.menu_item['command']
		self.full_path = self.menu_item['include_full_path']
		self.scraper_id = self.menu_item['scraper_id'] if self.menu_item['scraper_id'] else ''
		self.banner = self.cfg.options.load_image(self.menu_item['banner'], verbose = True) #verbose=True, will return None, rather than blank image
		self.warning = ''
		self.visible = bool(self.menu_item['visible'])
		
		
		
		self.icon_selected = self.menu_item['icon_selected']
		self.pre_loaded_selected_icon = self.cfg.options.load_image(self.icon_selected, self.cfg.options.generic_menu_item_selected)

		self.rom_path = self.menu_item['rom_path']
		self.override_menu = bool(self.menu_item['override_menu'])
		self.extension = bool(self.menu_item['include_extension'])
		
		
		if not self.menu_item['type']:
			if self.rom_path:
				self.type = self.ROM_LIST
			else:
				self.type = self.COMMAND
		else:
			self.type = self.menu_item['type'].upper()

		self.update_image(init = True)
		
	def update_image(self, init = False):
	
		#@TODO this code is duplicated
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - self.cfg.options.padding) / self.cfg.options.num_items_per_row) - self.cfg.options.padding

		self.image = pygame.Surface([item_width, self.cfg.options.item_height], pygame.SRCALPHA, 32).convert_alpha()
		
		if not self.visible:
			self.image = self.image.convert()
			self.image.set_alpha(50)
			
		if self.menu_item['icon_file']:
			icon_file_path = self.menu_item['icon_file']
			#load generic icon if icon_file_path doesn't exist
			icon = self.cfg.options.load_image(icon_file_path, self.cfg.options.generic_menu_item)

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

			

		if self.display_label:
			label = PMLabel(self.label, self.cfg.options.label_font, self.cfg.options.label_font_color, self.cfg.options.label_background_color, self.cfg.options.label_font_bold, self.cfg.options.label_max_text_width)
			textpos = label.rect
			if self.cfg.options.label_text_align == 'right': textpos.x = text_align - label.rect.w + self.cfg.options.labels_offset[0]
			elif  self.cfg.options.label_text_align == 'center': textpos.x = ((text_align - label.rect.w)/2) + self.cfg.options.labels_offset[0]
			else: textpos.x = self.cfg.options.labels_offset[0]
			textpos.y = self.cfg.options.labels_offset[1]
			
			
			icon.blit(label.image, textpos)

		if self.cfg.options.display_rom_count:
			if self.rom_path:
				self.update_num_roms()
				if self.num_roms != 0:
					label = PMLabel(str(self.num_roms) + self.warning, self.cfg.options.rom_count_font, self.cfg.options.rom_count_font_color, self.cfg.options.rom_count_background_color, self.cfg.options.rom_count_font_bold, self.cfg.options.rom_count_max_text_width)
					textpos = label.rect
					
					if self.cfg.options.rom_count_text_align == 'right': textpos.x = text_align - label.rect.w + self.cfg.options.rom_count_offset[0]
					elif  self.cfg.options.rom_count_text_align == 'center': textpos.x = ((text_align - label.rect.w)/2) + self.cfg.options.rom_count_offset[0]
					else: textpos.x = self.cfg.options.rom_count_offset[0]
					textpos.y = self.cfg.options.rom_count_offset[1]
					
					icon.blit(label.image, textpos)

		icon = pygame.transform.smoothscale(icon, icon_size)
		self.image.blit(icon, ((avail_icon_width - icon_size[0]) / 2 + self.cfg.options.padding, (avail_icon_height - icon_size[1]) / 2 + self.cfg.options.padding))
		
		if init: self.rect = self.image.get_rect()
	
	def check_changes(self):
		
		if self.cfg.options.display_rom_count:
			if self.rom_path:
			
				query = 'SELECT COUNT(id) FROM local_roms where system = {pid}'.format(pid = self.id if self.id else -999)
				if self.icon_id == 'FAVORITE': query = "SELECT COUNT(id) FROM local_roms WHERE flags like '%favorite%'"
				if self.num_roms != int(self.cfg.local_cursor.execute(query).fetchone()[0]):
					self.update_image(init = False)
					return [self.rect]
				return []
		
	def update_num_roms(self):
		
		query = 'SELECT COUNT(id) FROM local_roms where system = {pid}'.format(pid = self.id if self.id else -999)
		if self.icon_id == 'FAVORITE': query = "SELECT COUNT(id) FROM local_roms WHERE flags like '%favorite%'"
		self.num_roms = int(self.cfg.local_cursor.execute(query).fetchone()[0])
		'''
		if isdir(self.rom_path):
			if '21' in self.scraper_id: #special check for scummvm:
				len_files = len([ f for f in listdir(self.rom_path) if isdir(join(self.rom_path,f)) and f != 'images'])	
			else:
				len_files = len([ f for f in listdir(self.rom_path) if isfile(join(self.rom_path,f)) and f != '.gitkeep' ])
		else:
			len_files = 0
			
			
		if (self.num_roms != len_files  
			and self.scraper_id  
			and self.override_menu != True
			and self.type != 'FRONTEND'):
						
			self.num_roms = len_files
			self.warning = "!"
		'''
	def get_rom_list(self):
		#@TODO - am I using the type field?
		
		keys = [item[1] for item in  self.cfg.local_cursor.execute('PRAGMA table_info(local_roms)').fetchall()]
		
		#basic query
		query = 'SELECT * FROM local_roms where system = {pid}'.format(pid = self.id if self.id else -999)
		
		#filter genres
		if self.cfg.options.rom_filter.lower() != 'all' : query += ' AND genres LIKE "%{genre_filter}%"'.format(genre_filter = self.cfg.options.rom_filter)
		
		#exclude clones
		if not self.cfg.options.show_clones: query += ' AND cloneof is NULL'
		
		#hide unmatched roms
		if not self.cfg.options.show_unmatched_roms: query += ' AND (flags is null or flags not like "%no_match%")'
		
		#order by category
		if self.cfg.options.rom_sort_category.lower() == 'favorites first':
			query += ' ORDER BY CASE WHEN flags LIKE "%favorite%" THEN 0 ELSE 1 END ASC, title ASC'
		else:
			query += ' ORDER BY {sort_category} {sort_order}, title ASC'.format(sort_category = self.cfg.options.rom_sort_category.lower().replace(' ', '_'), sort_order = 'DESC' if 'des' in self.cfg.options.rom_sort_order.lower() else 'ASC')
		
		if self.icon_id == 'FAVORITE': 
			query = "SELECT * FROM local_roms WHERE flags like '%favorite%'  ORDER BY {sort_category} {sort_order}, title ASC".format(
							sort_category = self.cfg.options.rom_sort_category.lower() if self.cfg.options.rom_sort_category.lower() != 'favorites first' else 'title',
							sort_order = 'DESC' if 'des' in self.cfg.options.rom_sort_order.lower() else 'ASC')
		
		values = self.cfg.local_cursor.execute(query).fetchall()
		
		
		return {'id': self.id, 'icon_id': self.icon_id,  'scraper_id': self.scraper_id.split(',')[0], 'list': [dict(zip(keys,value)) for value in values]}


	def run_command(self):
		print self.command
		system(self.command)
