import os
import pygame


class PMLabel(pygame.sprite.Sprite):
	def __init__(self, label_text, font, color_fg, color_bg, rom_list_offset=[0,0,0,0], create_romlist_image = False, new_rom = False):
		pygame.sprite.Sprite.__init__(self)

		
		self.text = label_text
		self.color_fg = color_fg
		self.font = font
		
		#font_opts = font_file, font_size, color_fg, color_bg
		
		if create_romlist_image or new_rom:
			if new_rom:
				self.image = new_rom.image.copy()
				text = font.render(label_text, 1, color_fg)
				text_rect = text.get_rect()
				text_rect =  (rom_list_offset['left'] , ((new_rom.icon_rect.h - text_rect.h) / 2) + rom_list_offset['top'])
				area_rect = [0,0,new_rom.icon_rect.w - rom_list_offset['right'] - rom_list_offset['left'],new_rom.icon_rect.h - rom_list_offset['bottom'] - rom_list_offset['top']]
				self.image.blit(text, text_rect, area_rect)
			else:
				self.icon = create_romlist_image
				self.icon_rect = self.icon.get_rect()
				if self.icon_rect.w < 5: 
					self.icon_rect.w = 600
					self.icon_rect.h = font.size('Ip')[1]
				self.image = pygame.Surface([self.icon_rect.w,self.icon_rect.h], pygame.SRCALPHA, 32).convert_alpha()
				self.image.fill(color_bg, self.icon_rect)
				self.image.blit(self.icon, (0,0))

		else:
			text = font.render(label_text, 1, color_fg).convert_alpha()
			text_rect = text.get_rect()
			self.image = pygame.Surface([text_rect.w, text_rect.h], pygame.SRCALPHA, 32).convert_alpha()
			self.image.fill(color_bg, text_rect)
			self.image.blit(text, text_rect)

		
		self.rect = self.image.get_rect()
		