import os
import pygame


class PMLabel(pygame.sprite.Sprite):
	def __init__(self, label_text, global_opts):
		pygame.sprite.Sprite.__init__(self)

		font = pygame.font.Font(global_opts.font_file, global_opts.font_size)
		text = font.render(label_text, 1, (0, 0, 0))
		text_rect = text.get_rect()

		colorkey_color = (255, 255, 255)

		self.image = pygame.Surface([text_rect.w, text_rect.h])
		self.image.fill(colorkey_color)
		self.image.set_colorkey(colorkey_color)
		

		self.image.blit(text, text_rect)

		self.rect = self.image.get_rect()
