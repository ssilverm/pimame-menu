import os
import pygame


class PMHeader(pygame.sprite.Sprite):
	def __init__(self, opts):
		pygame.sprite.Sprite.__init__(self)

		# @TODO - dont have to pass size around, can just get it like this:
		header_width = pygame.display.Info().current_w
		header_height = opts.header_height
		
		
		
		self.image = pygame.Surface([header_width, header_height], pygame.SRCALPHA, 32).convert_alpha()
		background_image = opts.pre_loaded_background
		self.image.blit(background_image, (0,0))
		self.image.fill(opts.header_color)

		icon_file_path = opts.theme_pack + opts.logo_image
		icon = opts.load_image(icon_file_path)


		icon_rect = icon.get_rect()
		icon_pos = ((header_width - icon_rect.w) / 2, (header_height - icon_rect.h) / 2)

		#icon = pygame.transform.scale(icon, (50,50))
		self.image.blit(icon, icon_pos)

		self.rect = self.image.get_rect()