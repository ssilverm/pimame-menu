import pygame
import glob


class PMRomItem(pygame.sprite.Sprite):
	def __init__(self, list_item, cfg, create_template = False, new_rom = False, min_scale_size = [600,12]):
		pygame.sprite.Sprite.__init__(self)

		
		self.cfg = cfg
		self.font = self.cfg.options.rom_list_font
		self.offset = self.cfg.options.rom_list_offset,
		self.max_text_width = self.cfg.options.rom_list_max_text_width
		self.create_template = create_template
		self.new_rom = new_rom
		self.min_scale_size = min_scale_size
		
		
		#try:
		if create_template:
			self.text = list_item
			self.favorite = ''
		else:
			list_item = dict(map(lambda (k,v): (k,v if v else ''), list_item.iteritems()))
			
			display_text = str(list_item[ self.cfg.options.rom_sort_category]) + ' - ' + list_item['title'] if self.cfg.options.rom_sort_category != 'title' else list_item['title']
			self.text = display_text if list_item['flags'] != 'display_platform' else '<- Back'
			self.title = list_item['title']
			self.id = list_item['id']
			self.type = 'command' if list_item['command'] else 'back'
			self.command = list_item['command']
			self.rom_file = list_item['rom_file']
			self.boxart = list_item['image_file']
			self.release_date = list_item['release_date']
			self.overview = list_item['overview']
			self.esrb = list_item['esrb']
			self.genres = list_item['genres']
			self.players = list_item['players']
			self.coop = list_item['coop']
			self.publisher = list_item['publisher']
			self.developer = list_item['developer']
			self.rating = list_item['rating']
			self.number_of_runs = list_item['number_of_runs'] if list_item['number_of_runs'] else 0
			self.flags = list_item['flags']
			self.favorite = 'favorite,' if 'favorite' in self.flags else ''

		self.selected = True
		self.toggle_selection()
		self.rect = self.image.get_rect()
		
	def build_item(self):

		if self.new_rom:
			
			self.font.set_bold(self.font_bold)
			text_image = self.font.render(self.text, 1, self.font_color)
			text_rect = text_image.get_rect()
			
			if self.favorite: full_width = max(self.max_text_width - self.cfg.options.rom_list_favorite_icon_rect.w - 10, 0)
			else: full_width = self.max_text_width

			if self.max_text_width and text_rect.w > full_width:
				scale = float(full_width) / text_rect.w
				text_image = pygame.transform.smoothscale(text_image, (full_width, int(text_rect.h * scale)))
				text_rect = text_image.get_rect()
			
			if self.favorite:
				cropping = self.cfg.options.rom_list_offset
				crop_rect = pygame.Rect(0,0, self.cfg.options.romlist_item_width  - cropping['left'] - cropping['right'] - self.cfg.options.rom_list_favorite_icon_rect.w - 10, text_rect.h)
				
				if self.cfg.options.rom_list_favorite_icon_rect.h > crop_rect.h: 
					self.cfg.options.rom_list_favorite_icon = pygame.transform.scale(self.cfg.options.rom_list_favorite_icon, (crop_rect.h, crop_rect.h))
					self.cfg.options.rom_list_favorite_icon_rect = self.cfg.options.rom_list_favorite_icon.get_rect()
					
				self.image = pygame.Surface([crop_rect.w + self.cfg.options.rom_list_favorite_icon_rect.w + 10, text_rect.h], pygame.SRCALPHA, 32).convert_alpha()
				self.image.blit(text_image, (0,0), crop_rect)
				self.image.blit( self.cfg.options.rom_list_favorite_icon,(crop_rect.w + 10, 0))
			else:
				self.image = text_image.copy()
		
		if self.create_template:
			self.icon = self.create_template
			self.icon_rect = self.icon.get_rect()
			if self.icon_rect.w < self.min_scale_size[0]:
				self.icon_rect.w = self.min_scale_size[0]
			if self.icon_rect.h < self.min_scale_size[1]:
				self.icon_rect.h = self.min_scale_size[1]
			self.image = pygame.Surface([self.icon_rect.w,self.icon_rect.h], pygame.SRCALPHA, 32).convert_alpha()
			self.image.fill(self.background_color, self.icon_rect)
			self.image.blit(self.icon, (0,0))
				

	def toggle_selection(self):
		self.selected = not self.selected
		
		if self.selected:
			self.font_color = self.cfg.options.rom_list_font_selected_color
			self.background_color = self.cfg.options.rom_list_background_selected_color
			self.font_bold = self.cfg.options.rom_list_font_selected_bold
		else:
			self.font_color = self.cfg.options.rom_list_font_color
			self.background_color = self.cfg.options.rom_list_background_color
			self.font_bold = self.cfg.options.rom_list_font_bold
		
		self.build_item()
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		