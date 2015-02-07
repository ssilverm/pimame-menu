import pygame


class PMParagraph(pygame.sprite.Sprite):
	def __init__(self, paragraph_text, font, color_fg, max_paragraph_width, justify = 'left'):
		pygame.sprite.Sprite.__init__(self)

		
		self.text = paragraph_text
		self.color_fg = color_fg
		self.font = font
		
		lines = [font.render(line, 1, color_fg) for line in self.build_lines(paragraph_text, font, max_paragraph_width)]
		line_height = lines[0].get_size()[1]
		self.P = pygame.Surface([max_paragraph_width, line_height * len(lines)], pygame.SRCALPHA, 32).convert_alpha()
		self.rect = self.P.get_rect()
		
		justify = justify.lower()
		position = {'left':{'left':0}, 'center': {'centerx': self.rect.centerx}, 'right': {'right': self.rect.width}}
		
		y = 0
		for line in lines:
			line_rect = line.get_rect(top=y,**position[justify])
			self.P.blit(line, line_rect)
			y += line_height
		
		#self.P -> surface to blit
		
	def build_lines(self, text, dfont, max_paragraph_width):
		
		text = text.replace('\t', ' [t] ')
		paragraphs = text.split('\n')
		for paragraph in paragraphs:
			current_line = ''
			for word in paragraph.split():
				if word == '[t]': word = '   '
				if dfont.size(current_line)[0] + dfont.size(word)[0] < max_paragraph_width:
					current_line += word + ' '
				else:
					yield current_line.strip()
					current_line = word + ' '
			yield current_line.strip()
