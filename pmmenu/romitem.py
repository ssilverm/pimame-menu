import os
import pygame


class PMRomItem(pygame.sprite.Sprite):
	def __init__(self, label_text, font, color_fg, color_bg, font_bold = False, rom_list_offset=[0,0,0,0], create_romlist_image = False, new_rom = False, min_scale_size = [600,12], text_align = 'left'):
		pygame.sprite.Sprite.__init__(self)

		
		self.text = label_text
		self.color_fg = color_fg
		self.font = font
		
		#font_opts = font_file, font_size, color_fg, color_bg
		
		if create_romlist_image or new_rom:
			if new_rom:
				self.image = new_rom.image.copy()
				font.set_bold(font_bold)
				text = font.render(label_text, 1, color_fg)
				text_rect = text.get_rect()
				if text_align == 'right': text_align = new_rom.icon_rect.w - text_rect.w
				elif text_align == 'center': text_align = (new_rom.icon_rect.w - text_rect.w)/2
				else: text_align = 0
				text_rect =  (rom_list_offset['left'] + text_align , ((new_rom.icon_rect.h - text_rect.h) / 2) + rom_list_offset['top'])
				area_rect = [0,0,new_rom.icon_rect.w - rom_list_offset['right'] - rom_list_offset['left'],new_rom.icon_rect.h - rom_list_offset['bottom'] - rom_list_offset['top']]
				self.image.blit(text, text_rect, area_rect)
			else:
				self.icon = create_romlist_image
				self.icon_rect = self.icon.get_rect()
				if self.icon_rect.w < min_scale_size[0]:
					self.icon_rect.w = min_scale_size[0]
				if self.icon_rect.h < min_scale_size[1]:
					self.icon_rect.h = min_scale_size[1]
				self.image = pygame.Surface([self.icon_rect.w,self.icon_rect.h], pygame.SRCALPHA, 32).convert_alpha()
				self.image.fill(color_bg, self.icon_rect)
				self.image.blit(self.icon, (0,0))

		self.rect = self.image.get_rect()
		