import os
import pygame
from pmlabel import *


class PMList(pygame.sprite.OrderedUpdates):
	def __init__(self, rom_list, global_opts):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.rom_list = rom_list

		for list_item in rom_list:
			#print list_item
			label = PMLabel(list_item['title'], global_opts)
			label.command = list_item['command']
			self.add(label)