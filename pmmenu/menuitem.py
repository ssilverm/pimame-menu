import os
import pygame


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

		font = pygame.font.Font(global_opts.font_file, global_opts.font_size)
		text = font.render(self.label, 1, (0, 0, 0))
		textpos = text.get_rect()
		textpos.y = 50

		self.image.blit(text, textpos)

		# self.image.set_alpha(128)

		self.rect = self.image.get_rect()
		#print self.command

		#self.sprite = pygame.image.load(opts['icon_file']).convert_alpha()

	#def draw(self, screen, item_color, pos):
	#	self.sprite = pygame.draw.rect(screen, item_color, pos)
	#	return self.sprite

	#def get_pos(self):
	#	return self.sprite.x + ',' + self.sprite.y

	def run_command(self):
		print self.command
		os.system(self.command)