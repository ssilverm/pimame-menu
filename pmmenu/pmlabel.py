import os
import pygame


class PMLabel(pygame.sprite.Sprite):
	def __init__(self, label_text, font, color_fg, color_bg):
		pygame.sprite.Sprite.__init__(self)

		self.text = label_text

		#font_opts = font_file, font_size, color_fg, color_bg

		text = font.render(label_text, 1, color_fg, color_bg)
		text_rect = text.get_rect()

		#colorkey_color = (255, 255, 255)

		self.image = pygame.Surface([text_rect.w, text_rect.h])
		#self.image.fill(colorkey_color)
		#self.image.set_colorkey(colorkey_color)
		

		self.image.blit(text, text_rect)

		self.rect = self.image.get_rect()