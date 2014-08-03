import os
import pygame
from romitem import *


class PMList(pygame.sprite.OrderedUpdates):
	labels = []

	def __init__(self, rom_list, global_opts, get_labels = False):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.global_opts = global_opts
		self.first_index = self.last_index = 0
		self.labels = []

		self.rom_list = sorted(rom_list, key=lambda rom: rom['title'])

		back_item = {'type': 'back', 'title': '<- Back', 'image': '/home/pi/pimame/pimame-menu/assets/images/blank.png', 'command': None}
		self.rom_list.insert(0, back_item)
		
		#get pre-loaded (unselected) rom list image
		create_romlist_image = global_opts.pre_loaded_romlist
		create_romlist_selected = global_opts.pre_loaded_romlist_selected
		
		#make sure each romlist item reaches minimum sizes
		min_scale_size = [global_opts.romlist_item_width, global_opts.romlist_item_height]
		
		#Create rom list surface/image with no text
		self.rom_template = PMRomItem('', global_opts.rom_list_font, global_opts.rom_list_font_color, global_opts.rom_list_background_color, global_opts.rom_list_font_bold, global_opts.rom_list_offset, create_romlist_image, False, min_scale_size)
		
		self.selected_rom_template = PMRomItem('', global_opts.rom_list_font, global_opts.rom_list_font_selected_color, global_opts.rom_list_background_selected_color, global_opts.rom_list_font_selected_bold, global_opts.rom_list_offset, create_romlist_selected, False, min_scale_size)
		
		if get_labels: self.build_labels(self.rom_list)
		
	def build_labels(self, rom_list):
		#Get rom title and blit to already created rom_template
		self.labels = []
		for list_item in rom_list:
			label = PMRomItem(list_item['title'], self.global_opts.rom_list_font, self.global_opts.rom_list_font_color, self.global_opts.rom_list_background_color, self.global_opts.rom_list_font_bold, self.global_opts.rom_list_offset, False, self.rom_template, [], self.global_opts.rom_list_font_align, self.global_opts.rom_list_max_text_width)
			label.type = list_item['type']
			label.command = list_item['command']
			label.boxart = list_item['image']
			self.labels.append(label)

	def set_visible_items(self, first_index, last_index):
		self.first_index = first_index
		self.last_index = last_index
	
		self.empty()
		self.build_labels(self.rom_list[first_index:last_index])
		self.add(self.labels)