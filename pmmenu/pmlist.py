import os
import pygame
from pmlabel import *


class PMList(pygame.sprite.OrderedUpdates):
	def __init__(self, rom_list, global_opts):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.rom_list = rom_list

		for list_item in rom_list:
			#print list_item
			label = PMLabel(list_item['title'], global_opts.font, global_opts.text_color, global_opts.background_color)
			label.command = list_item['command']
			self.add(label)