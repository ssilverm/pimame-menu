import os
import pygame
from pmlabel import *


class PMList(pygame.sprite.OrderedUpdates):
	labels = []

	def __init__(self, rom_list, global_opts):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.first_index = self.last_index = 0
		self.labels = []

		self.rom_list = rom_list

		back_item = {'type': 'back', 'title': '<- Back', 'command': None}
		rom_list.insert(0, back_item)

		for list_item in rom_list:
			label = PMLabel(list_item['title'], global_opts.font, global_opts.text_color, global_opts.background_color)
			label.type = list_item['type']
			label.command = list_item['command']
			self.labels.append(label)

	def set_visible_items(self, first_index, last_index):
		self.first_index = first_index
		self.last_index = last_index

		self.empty()
		self.add(self.labels[first_index:last_index])