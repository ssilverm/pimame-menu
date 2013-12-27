from os import listdir, system
from os.path import isfile, isdir, join
import pygame
from pmlabel import *


class PMMenuItem(pygame.sprite.Sprite):
	def __init__(self, item_opts, global_opts):
		pygame.sprite.Sprite.__init__(self)

		self.label = item_opts['label']
		self.command = item_opts['command']
		self.roms = item_opts['roms']

		#@TODO this code is duplicated
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - global_opts.padding) / global_opts.num_items_per_row) - global_opts.padding

		self.image = pygame.Surface([item_width, global_opts.item_height])
		self.image.fill(global_opts.item_color)

		icon_file_path = global_opts.icon_pack_path + item_opts['icon_file']
		icon = pygame.image.load(icon_file_path).convert_alpha()
		
		icon = pygame.transform.scale(icon, (50,50))
		self.image.blit(icon, (0, 0))

		#font = pygame.font.Font(global_opts.font_file, global_opts.font_size)
		#text = font.render(self.label, 1, (0, 0, 0))
		label = PMLabel(self.label, global_opts.font, global_opts.text_color, global_opts.item_color)
		textpos = label.rect
		textpos.y = 50

		self.image.blit(label.image, textpos)

		

		# draw rom text
		num_roms = self.get_num_roms()

		if num_roms == 0:
			self.image.set_alpha(64)
		else:
			# draw rom circle
			rom_rect = (item_width - global_opts.padding - 30, global_opts.item_height - global_opts.padding - 30, 30, 30)
			pygame.draw.rect(self.image, global_opts.rom_dot_color, rom_rect)

			#text = font.render(str(num_roms), 1, (255, 255, 255))
			label = PMLabel(str(num_roms), global_opts.font, global_opts.text_highlight_color, global_opts.rom_dot_color)
			textpos = label.rect

			textpos.centerx = rom_rect[0] + rom_rect[2] / 2
			textpos.centery = rom_rect[1] + rom_rect[3] / 2
			self.image.blit(label.image, textpos)

		self.rect = self.image.get_rect()
		#print self.command

		#self.sprite = pygame.image.load(opts['icon_file']).convert_alpha()

	#def draw(self, screen, item_color, pos):
	#	self.sprite = pygame.draw.rect(screen, item_color, pos)
	#	return self.sprite

	#def get_pos(self):
	#	return self.sprite.x + ',' + self.sprite.y

	def get_num_roms(self):
		if not isdir(self.roms):
			return 0

		files = [ f for f in listdir(self.roms) if isfile(join(self.roms,f)) ]
		return len(files)

	def get_rom_list(self):
		#@TODO - am I using the type field?
		return [
			{
				'title': f,
				'type': 'command',
				'command': self.command + ' \'' + self.roms + f +'\'' 
			}
			for f in listdir(self.roms) if isfile(join(self.roms, f))
		]

	def run_command(self):
		print self.command
		system(self.command)