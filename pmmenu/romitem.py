import pygame


class PMRomItem(pygame.sprite.Sprite):
	def __init__(self, label_text, font, color_fg, color_bg, font_bold = False, rom_list_offset=[0,0,0,0], create_romlist_image = False, new_rom = False, min_scale_size = [600,12], text_align = 'left', max_text_width = False):
		pygame.sprite.Sprite.__init__(self)

		
		self.text = label_text
		self.color_fg = color_fg
		self.font = font
		
		#font_opts = font_file, font_size, color_fg, color_bg
		
		#create_romlist_image = template
		#new_rom = new rom item to be added to pmlist
		if create_romlist_image or new_rom:
			if new_rom:
				#self.image = new_rom.image.copy()
				
				font.set_bold(font_bold)
				self.image = font.render(label_text, 1, color_fg)
				text_rect = self.image.get_rect()
				
				if max_text_width and text_rect.w > max_text_width:
					scale = float(max_text_width) / text_rect.w
					self.image = pygame.transform.smoothscale(self.image, (max_text_width, int(text_rect.h * scale)))
					text_rect = self.image.get_rect()
			
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
		