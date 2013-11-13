import os
import pygame


class PMSelection(pygame.sprite.Sprite):
	def __init__(self, global_opts):
		pygame.sprite.Sprite.__init__(self)

		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - global_opts.padding) / global_opts.num_items_per_row) - global_opts.padding
		item_height = global_opts.item_height

		colorkey_color = (0, 0, 0)
		if colorkey_color == global_opts.selection_color:
			colorkey_color = (255, 255, 255)

		self.image = pygame.Surface([item_width, global_opts.item_height])
		self.image.fill(colorkey_color)
		self.image.set_colorkey(colorkey_color)
		pygame.draw.rect(self.image, global_opts.selection_color, (0, 0, item_width, global_opts.item_height), global_opts.selection_size)
		#pygame.draw.lines(self.image, global_opts.selection_color, True, [(0, 0), (item_width, 0), (item_width, item_height), (0, item_height)], global_opts.selection_size)

		self.rect = self.image.get_rect()

	def update(self, menu_item):
		item_rect = menu_item.rect;

		self.rect.x = item_rect.x;
		self.rect.y = item_rect.y;
