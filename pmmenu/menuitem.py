


#TODO: fix alpha for unused emulators

from os import listdir, system
from os.path import isfile, isdir, join, splitext, basename
import pygame
from pmlabel import *
import json


class PMMenuItem(pygame.sprite.Sprite):
	ROM_LIST = 'rom_list'
	COMMAND = 'command'
	NAVIGATION = 'nav'
	NEXT_PAGE = 'next'
	PREV_PAGE = 'prev'

	num_roms = 0

	def __init__(self, item_opts, global_opts, type = False):
		pygame.sprite.Sprite.__init__(self)

		self.label = item_opts['label']
		self.command = item_opts['command']
		self.full_path = item_opts['full_path']
		self.cache = "/home/pi/pimame/pimame-menu/.cache/" + item_opts['label'].lower() + ".cache"
		if item_opts['icon_selected']: 
			self.icon_selected = global_opts.theme_pack + item_opts['icon_selected']
			self.pre_loaded_selected_icon = global_opts.load_image(self.icon_selected, global_opts.generic_menu_item_selected)
		else:
			self.icon_selected = False
		#self.extension = item_opts['extension']
		
		if 'type' in item_opts: type = item_opts['type']
		
		try:
			self.roms = item_opts['roms']
		except KeyError:
			self.roms = False
		
		try:
			if item_opts['override_menu'] and item_opts['override_menu'] == True:
				self.override_menu = True
			else:
				self.override_menu = False
		except KeyError:
			self.override_menu = False

		try:
			if item_opts['extension'] and item_opts['extension'] == True:
				self.extension = True
			else:
				self.extension = False
		except KeyError:
			self.extension = False


		if type == False:
			if 'roms' in item_opts:
				self.type = self.ROM_LIST
			else:
				self.type = self.COMMAND
		else:
			self.type = type

		#@TODO this code is duplicated
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - global_opts.padding) / global_opts.num_items_per_row) - global_opts.padding

		self.image = pygame.Surface([item_width, global_opts.item_height], pygame.SRCALPHA, 32).convert_alpha()

		if item_opts['icon_file']:
			icon_file_path = global_opts.theme_pack + item_opts['icon_file']
			#load generic icon if icon_file_path doesn't exist
			icon = global_opts.load_image(icon_file_path, global_opts.generic_menu_item)

			# resize and center icon:
			icon_size = icon.get_size()
			text_align = icon_size[0]
			avail_icon_width = item_width - global_opts.padding * 2
			avail_icon_height = global_opts.item_height - global_opts.padding * 2
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

			

		if global_opts.display_labels:
			label = PMLabel(self.label, global_opts.label_font, global_opts.label_font_color, global_opts.label_background_color, global_opts.label_font_bold)
			textpos = label.rect
			if global_opts.label_text_align == 'right': textpos.x = text_align - label.rect.w + global_opts.labels_offset[0]
			elif  global_opts.label_text_align == 'center': textpos.x = ((text_align - label.rect.w)/2) + global_opts.labels_offset[0]
			else: textpos.x = global_opts.labels_offset[0]
			textpos.y = global_opts.labels_offset[1]
			
			
			icon.blit(label.image, textpos)

		if global_opts.display_rom_count:
			if self.type == self.ROM_LIST:
				self.update_num_roms()

			if self.type == self.ROM_LIST:
				#if self.num_roms == str(0):
				#	icon = icon.convert_alpha()
				#	icon.set_alpha(64)
				#else:
					#text = font.render(str(num_roms), 1, (255, 255, 255))
					label = PMLabel(str(self.num_roms), global_opts.rom_count_font, global_opts.rom_count_font_color, global_opts.rom_count_background_color, global_opts.rom_count_font_bold)
					textpos = label.rect
					
					if global_opts.rom_count_text_align == 'right': textpos.x = text_align - label.rect.w + global_opts.rom_count_offset[0]
					elif  global_opts.rom_count_text_align == 'center': textpos.x = ((text_align - label.rect.w)/2) + global_opts.rom_count_offset[0]
					else: textpos.x = global_opts.rom_count_offset[0]
					textpos.y = global_opts.rom_count_offset[1]
					
					icon.blit(label.image, textpos)

		icon = pygame.transform.smoothscale(icon, icon_size)
		self.image.blit(icon, ((avail_icon_width - icon_size[0]) / 2 + global_opts.padding, (avail_icon_height - icon_size[1]) / 2 + global_opts.padding))
		
		self.rect = self.image.get_rect()

	def update_num_roms(self, warning = "!"):
		
		self.num_roms = "0"
		if isfile(self.cache):
					json_data=open(self.cache)
					raw_data = json.load(json_data)
					files = raw_data['rom_data']
					file_count = raw_data['file_count']
					json_data.close()
					if file_count == len(listdir(self.roms)): warning = ""
					
		else:
			if not isdir(self.roms):
				return None

			files = [ f for f in listdir(self.roms) if isfile(join(self.roms,f)) and f != '.gitkeep'  ]
			
			
		if len(files) > 0: self.num_roms = str(len(files)) + warning
		else: self.num_roms = "0"

	def get_rom_list(self):
		#@TODO - am I using the type field?
		
		rom_data = None
		if isfile(self.cache):
					json_data=open(self.cache)
					raw_data = json.load(json_data)
					file_count = raw_data['file_count']
					rom_data = raw_data['rom_data']
					json_data.close()
					
		if not "!" in str(self.num_roms) and rom_data:
			return [
				
					{
						'title': f['real_name'] if ('real_name' in f) else f['file'],
						'type': 'command',
						'image': join( f['image_path'], f['image_file']),
						'command': (self.command + ' \"' + (join(f['rom_path'],f['file']) if (self.full_path and self.extension) else f['file'] if (self.extension and not self.full_path) else os.path.splitext(f['file'])[0] if (not self.extension and not self.full_path) else join(f['rom_path'], os.path.splitext(f['file'])[0])) + '\"')
					}
					for f in rom_data
			]
			
		elif "!" in str(self.num_roms) and rom_data:
			remaining_files = listdir(self.roms)
			list = []
			
			for f in rom_data:
				if isfile(join(f['rom_path'], f['file'])) and f['file'] != '.gitkeep':
					if f['file'] in remaining_files: remaining_files.remove(f['file'])
					list.append({
						'title': f['real_name'] if ('real_name' in f) else f['file'],
						'type': 'command',
						'image': join( f['image_path'], f['image_file']),
						'command': (self.command + ' \"' + (join(f['rom_path'],f['file']) if (self.full_path and self.extension) else f['file'] if (self.extension and not self.full_path) else os.path.splitext(f['file'])[0] if (not self.extension and not self.full_path) else join(f['rom_path'], os.path.splitext(f['file'])[0])) + '\"')
					})
					
			for f in remaining_files:
				if isfile(join(self.roms, f)) and f != '.gitkeep':
					list.append({
						'title': os.path.splitext(os.path.basename(f))[0],
						'type': 'command',
						'image': self.roms + 'images/' +  os.path.splitext(os.path.basename(f))[0],
						'command': (self.command + ' \"' + (join(self.roms,f) if (self.full_path and self.extension) else f if (self.extension and not self.full_path) else os.path.splitext(f)[0] if (not self.extension and not self.full_path) else join(self.roms, os.path.splitext(f)[0])) + '\"')
					})
					
			return list
			
		else:
			return [
				{
					'title': os.path.splitext(os.path.basename(f))[0],
					'type': 'command',
					'image': self.roms + 'images/' +  os.path.splitext(os.path.basename(f))[0],
					'command': (self.command + ' \"' + (join(self.roms,f) if (self.full_path and self.extension) else f if (self.extension and not self.full_path) else os.path.splitext(f)[0] if (not self.extension and not self.full_path) else join(self.roms, os.path.splitext(f)[0])) + '\"')
				}
				for f in listdir(self.roms) if isfile(join(self.roms, f)) and f != '.gitkeep'
			]

	def run_command(self):
		print self.command
		system(self.command)
