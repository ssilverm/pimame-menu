import pygame


class PMLabel(pygame.sprite.Sprite):
	def __init__(self, label_text, font, color_fg, color_bg = (0,0,0,0), font_bold = False, max_text_width = False):
		pygame.sprite.Sprite.__init__(self)

		
		self.text = label_text
		self.color_fg = color_fg
		self.font = font
		
		#pygame faux bold font
		font.set_bold(font_bold)
		text = font.render(label_text, 1, color_fg).convert_alpha()
		text_rect = text.get_rect()
		
		if max_text_width and text_rect.w > max_text_width:
			scale = float(max_text_width) / text_rect.w
			text = pygame.transform.smoothscale(text, (int(max_text_width), int(text_rect.h * scale)))
			text_rect = text.get_rect()
		#make text smoother
		text.blit(text, text_rect)
			
		if label_text == '': text_rect.w = 0
		self.image = pygame.Surface([text_rect.w, text_rect.h]).convert_alpha()
		self.image.fill(color_bg, text_rect)
		self.image.blit(text, text_rect)
		
		self.rect = self.image.get_rect()
		
		
		