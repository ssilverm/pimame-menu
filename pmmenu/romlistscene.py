import thread, time
import pygame
from pmcontrols import *
from pmpopup import *
from pmlist import *
from pmutil import *

class RomListScene(object):

	SCENE_NAME = 'romlist'
	
						
	selected_item = None
	selected_index = 0
	update_display = []
	
	sprites = []
	
	boxart_thread = None

	def __init__(self, rom_list):
		super(RomListScene, self).__init__()
		self.CONTROLS = PMControls()
		self.rom_list = rom_list
	
	def draw_bg(self, rect=None):
		if not rect:
			self.screen.fill(self.cfg.options.background_color)
			self.screen.blit(self.cfg.options.pre_loaded_rom_list_background, (0,0))
			self.update_display = [self.screen.get_rect()]
		else:
			self.screen.fill(self.cfg.options.background_color, rect)
			self.screen.blit(self.cfg.options.pre_loaded_rom_list_background, rect, rect)
			self.update_display.append(rect)
	
	def get_dimensions(self):
	
		self.avail_width = self.screen.get_width()
		self.avail_height = self.screen.get_height()
		cropping = self.cfg.options.rom_list_offset
		

		self.list_container = pygame.Rect(0, 0, self.list.rom_template.rect.w + (self.cfg.options.rom_list_padding * 2), self.avail_height)
		self.list_rect = pygame.Rect(0,0, self.list.rom_template.rect.w, self.avail_height - (self.cfg.options.rom_list_padding *2))
		self.crop_rect = pygame.Rect(0,0, self.list.rom_template.rect.w - cropping['left'] - cropping['right'], self.list.rom_template.rect.h - cropping['bottom'])
		self.info_container = pygame.Rect(0, 0, self.avail_width - self.list_container.w, self.avail_height)
		self.boxart_area = pygame.Rect(0, 0, self.info_container.w, int(self.info_container.h * .4))
		self.description_area = pygame.Rect(0, self.boxart_area.h, self.info_container.w, self.info_container.h - self.boxart_area.h)
		
			
		
		if self.cfg.options.rom_list_align == 'right':
			self.list_container.right = self.avail_width
			self.list_rect.center = self.list_container.center
			self.title_rect = self.list_rect.move(cropping['left'], cropping['top'])
			self.info_container.right = self.list_container.left
			self.boxart_area.right = self.info_container.right
			self.description_area.right = self.info_container.right
		else:
			self.list_rect.center = self.list_container.center
			self.title_rect = self.list_rect.move(cropping['left'], cropping['top'])
			self.info_container.left = self.list_container.right
			self.boxart_area.left = self.info_container.left
			self.description_area.left = self.info_container.left
		

	def pre_render(self, screen):
		
		self.draw_bg()
		self.list = PMList(self.rom_list, self.cfg.options)
		self.get_dimensions()
		
		self.list_background = pygame.Surface([self.list_rect.w, self.list_rect.h], pygame.SRCALPHA, 32).convert_alpha()

		self.items_per_screen = int(self.measure_items_per_screen())
		self.list.set_visible_items(0, self.items_per_screen)
		y = 0
		
		for sprite in self.list.sprites():
			self.list_background.blit(self.list.rom_template.image,(0,y))
			y += self.list.rom_template.rect.h

				
		self.popup = None

		self.draw_list()

		self.selected_item = self.list.labels[0]
		
		self.draw()
		if self.cfg.options.use_scene_transitions: effect = PMUtil.fade_into(self, self.cfg.options.fade_image)
		self.cfg.options.fade_image.blit(self.screen,(0,0))
		
		#pygame.draw.rect(self.screen, (255,0,0), self.list_container,5)
		#pygame.draw.rect(self.screen, (0,255,0), self.list_rect,3)
		#pygame.draw.rect(self.screen, (0,0,255), self.title_rect,1)
		#pygame.draw.rect(self.screen, (0,255,255), self.crop_rect,1)
		#pygame.draw.rect(self.screen, (255,255,0), self.info_container,5)
		#pygame.draw.rect(self.screen, (255,0,255), self.boxart_area,1)
		#pygame.draw.rect(self.screen, (255,255,255), self.description_area,1)
		

	def measure_items_per_screen(self):
	
		item_size = self.cfg.options.romlist_item_height
		screen_size = self.list_background.get_rect().h
		
		alignment = {'left': self.cfg.options.rom_list_padding, 
							'right': (pygame.display.Info().current_w - self.cfg.options.romlist_item_width - self.cfg.options.rom_list_padding), 
							}
							
		self.rom_list_align = alignment[self.cfg.options.rom_list_align]

		return screen_size / item_size

	def render(self, screen):
		pass

	def update(self):
		pass

	def handle_events(self, action):

		if self.popup and self.popup.menu_open:
			self.popup.handle_events(action)
			
			if action == 'SELECT':
				self.popup.menu_open = False
				self.screen.blit(self.cfg.options.fade_image, (0,0))
				
				self.clear_rom_item(False)
				found_index = self.popup.menu_work.abc_find(self.list.rom_list)
				self.list.set_visible_items(found_index, found_index + self.items_per_screen)
				self.draw_list()
				self.selected_item = self.list.labels[0]
				self.draw()
				
		else:
			if action == 'SELECT':
				self.run_sprite_command(self.selected_item)
			elif action == 'BACK':
				self.cfg.options.menu_back_sound.play()
				self.manager.back()
			elif action == 'MENU':
				self.popup = PMPopup(self.screen, self.manager.scene.SCENE_NAME, self.cfg.options, True)
				
			elif action in "UP/DOWN/LEFT/RIGHT":
				self.set_selected_index(action)
				
			#MOUSE CLICK
			elif action == "MOUSEUP":
				pos = pygame.mouse.get_pos()
				# get all rects under cursor
				clicked_sprites = [s for s in self.sprites if s.rect.collidepoint(pos)]
				
				if clicked_sprites:
					sprite = clicked_sprites[0]
					self.run_sprite_command(sprite)
			
			#MOUSE MOVE
			elif action == "MOUSEMOVE":
				pos = pygame.mouse.get_pos()
				# get all rects under cursor
				if not self.sprites[self.selected_index].rect.collidepoint(pos):
					clicked_sprites = [index for index, s in enumerate(self.sprites) if s.rect.collidepoint(pos)]
				
					if len(clicked_sprites) > 0:
						sprite = clicked_sprites[0]
						self.selected_item = self.sprites[sprite]
						self.set_selected_index(None)
						
		return self.update_display

	def set_selected_index(self, direction, play_sound = True):
		self.clear_rom_item()
		#move selection up by 1
		if play_sound: self.cfg.options.menu_move_sound.play()
		if direction == "UP":
			self.selected_index = self.sprites.index(self.selected_item)
			#check if selected item is highest item on screen
			if self.selected_index == 0:
				#check to see if this is the very first rom. if not, then advance list upwards, otherwise do nothing
				if self.list.first_index > 0:
					#get the smaller number to determine how far to advance the list
					difference = min(self.list.first_index, len(self.list.labels))
					self.list.set_visible_items(self.list.first_index - difference, self.list.last_index - difference)
					self.draw_list()
					self.selected_item = self.list.labels[len(self.list.labels)-1]
			else:
				#if not highest item on screen, just advance selection
				self.selected_item = self.sprites[self.selected_index - 1]
	
		#move selection down by 1
		elif direction == "DOWN":
			self.selected_index = self.sprites.index(self.selected_item)
			if self.selected_index == (len(self.list.labels)-1):
				if self.list.last_index < len(self.rom_list):
					difference = min(len(self.rom_list) - self.list.last_index + 1, len(self.list.labels))
					self.list.set_visible_items(self.list.first_index + difference, self.list.last_index + difference)
					self.draw_list()
					self.selected_item = self.list.labels[0]
			else:
				self.selected_item = self.sprites[self.selected_index + 1]
				
		#move selection down by number of items on screen	
		elif direction == "RIGHT":
			self.selected_index = self.sprites.index(self.selected_item)
			if self.selected_index < int(self.items_per_screen/2):
				self.selected_index = min((self.items_per_screen/2),(len(self.list.labels)-1))
				self.selected_item = self.list.labels[self.selected_index]
			else:
				difference = min(len(self.rom_list) - self.list.last_index + 1, len(self.list.labels))
				self.list.set_visible_items(self.list.first_index + difference, self.list.last_index + difference)
				self.draw_list()
				self.selected_index = min((self.items_per_screen/2),(len(self.list.labels)-1))
				self.selected_item = self.list.labels[self.selected_index]
				
		#move selection up by number of items on screen
		if direction == "LEFT":
			self.selected_index = self.sprites.index(self.selected_item)
			if self.selected_index > int(self.items_per_screen/2):
				self.selected_index = min((self.items_per_screen/2),(self.list.last_index - len(self.list.labels)))
				self.selected_item = self.list.labels[self.selected_index]
			else:
				difference = min(self.list.first_index, len(self.list.labels))
				self.list.set_visible_items(self.list.first_index - difference, self.list.last_index - difference)
				self.draw_list()
				self.selected_index = min((self.items_per_screen/2),(self.list.first_index))
				self.selected_item = self.list.labels[self.selected_index]
		
		self.draw()

	def draw_list(self, clear_list = True):
			
		y = 0
			
		self.sprites = []
		
		if clear_list:
			self.draw_bg(self.list_rect)
			self.screen.blit(self.list_background, self.list_rect)
		
		for sprite in self.list.sprites():
			self.sprites.append(sprite)
			if self.cfg.options.rom_list_font_align == 'center':
				sprite.rect.width = min(sprite.rect.width,self.crop_rect.width)
				sprite.rect.centerx = self.title_rect.centerx
			elif self.cfg.options.rom_list_font_align == 'right':
				sprite.rect.right = self.title_rect.right
			else:
				sprite.rect.x = self.title_rect.x
			sprite.rect.y = self.title_rect.y + y


			y += self.list.rom_template.rect.h
			self.screen.blit(sprite.image, sprite.rect, self.crop_rect)
				
		#self.list_container
		#self.list_rect
		#self.title_rect
		#self.crop_rect
		#self.info_container
		#self.boxart_area
		#self.description_area
		
		#self.list.draw(self.text_canvas)
		#self.screen.blit(self.text_canvas, rect)
			
		

	def draw_boxart(self, delay):
		for i in xrange(0, delay):
			time.sleep(.01)
			if thread.get_ident() != self.boxart_thread: thread.exit()
			
		
		boxart = self.cfg.options.load_image(self.selected_item.boxart, self.cfg.options.missing_boxart_image)
		boxart_rect = boxart.get_rect()
		
		scale = min(float((self.boxart_area.w * self.cfg.options.boxart_max_width) / boxart_rect.w), float((self.boxart_area.h * self.cfg.options.boxart_max_height) / boxart_rect.h))
		self.boxart_scale_size = (int(boxart_rect.w * scale), int(boxart_rect.h * scale))
		
		
		if thread.get_ident() != self.boxart_thread or boxart_rect.w == 1: thread.exit()
		
		#depending on type of file, either scale or smoothscale needs to be used
		try:
			boxart = pygame.transform.smoothscale(boxart, self.boxart_scale_size) 
		except:
			boxart = pygame.transform.scale(boxart, self.boxart_scale_size)
		
		boxart_rect = boxart.get_rect(center=self.boxart_area.center)
		
		if self.manager.scene.SCENE_NAME == 'romlist' and boxart_rect.w > 1:
			inflate = self.cfg.options.boxart_border_padding + self.cfg.options.boxart_border_thickness
			inflate = boxart_rect.inflate(inflate, inflate)
			
			if self.cfg.options.draw_rect:
				self.cfg.options.draw_rect.fill((0,0,0,0))
				pygame.draw.rect(self.cfg.options.draw_rect, self.cfg.options.boxart_border_color, inflate, self.cfg.options.boxart_border_thickness)
				self.screen.blit(self.cfg.options.draw_rect, inflate, inflate)
			self.screen.blit(boxart, boxart_rect)
			pygame.display.update(self.boxart_area)
			del boxart, boxart_rect, inflate, self
			thread.exit()
		else: thread.exit()
		
	def clear_rom_item(self, single_item = True):
		
		if single_item:
			rect = self.list.rom_template.rect
			rect.left = self.list_rect.left
			rect.top = self.list_rect.top + (self.list.rom_template.rect.h * self.sprites.index(self.selected_item))
			
			self.draw_bg(rect)
			self.screen.blit(self.list.rom_template.image, rect)

			self.screen.blit(self.selected_item.image, self.selected_item.rect, self.crop_rect)
			
		else:
			self.draw_bg()

	
	def draw(self, draw_boxart = True):
		if draw_boxart:
			try:
				if self.boxart_thread: 
					self.draw_bg(self.boxart_area)
			except: pass
			self.boxart_thread = thread.start_new_thread(self.draw_boxart, (20,))
		

		text = self.selected_item.text
		rect = self.list.rom_template.rect.copy()
		rect.left = self.list_rect.left
		rect.top = self.list_rect.top + (self.list.rom_template.rect.h * self.sprites.index(self.selected_item))

		#build and draw selected item on the fly
		selected_romlist_image = self.cfg.options.pre_loaded_romlist_selected.convert_alpha()
		
		self.screen.fill(self.cfg.options.background_color, rect)
		self.screen.blit(self.cfg.options.pre_loaded_rom_list_background, rect, rect)

		selected_label = PMRomItem(text, self.cfg.options.rom_list_font, self.cfg.options.rom_list_font_selected_color, self.cfg.options.rom_list_background_selected_color, self.cfg.options.rom_list_font_selected_bold, self.cfg.options.rom_list_offset, False, self.list.selected_rom_template, [], self.cfg.options.rom_list_font_align, self.cfg.options.rom_list_max_text_width)
		
		self.screen.blit(self.list.selected_rom_template.image, rect)
		
		if self.cfg.options.rom_list_font_align == 'center':
			selected_label.rect.width = min(selected_label.rect.width,self.crop_rect.width)
			selected_label.rect.centerx = self.title_rect.centerx
		elif self.cfg.options.rom_list_font_align == 'right':
			selected_label.rect.right = self.title_rect.right
		else:
			selected_label.rect.x = self.title_rect.x

		selected_label.rect.y = self.title_rect.y + (self.list.rom_template.rect.h * self.sprites.index(self.selected_item))

		self.screen.blit(selected_label.image, selected_label.rect, self.crop_rect)
		
		self.update_display.append(rect)

		
		

	def run_sprite_command(self, sprite):
		if(sprite.type == 'back'):
			self.cfg.options.menu_back_sound.play()
			self.manager.back()
		else:
			PMUtil.run_command_and_continue(sprite.command)
