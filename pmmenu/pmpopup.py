import os
import pygame
import subprocess
from os import system
from pmcontrols import *

class PMPopup(pygame.sprite.Sprite):

	def __init__(self, scene_type, cfg, list = None):
		pygame.sprite.Sprite.__init__(self)
		
		self.cfg = cfg
		self.scene_type = scene_type
		
		self.theme_list = self.get_themes()
		self.theme_count = 0
		
		self.list = self.build_menu(scene_type)
		self.item_height = self.list[0]['value'].rect.h
		self.hover = 0
		self.selected = False
		
		
		self.update_menu()

		
		self.rect = self.menu.get_rect()
	
	#MENU FUNCTIONS
	def hover_next(self):
		self.hover += 1
		if self.hover > (len(self.list)-1): self.hover = 0
		self.update_menu()
		
	def hover_prev(self):
		self.hover -= 1
		if self.hover < 0: self.hover = len(self.list)-1
		self.update_menu()
	
	def set_selected(self):
		self.selected = not self.selected
		self.update_menu()
		
		
	def build_menu(self, scene_type):
		if scene_type == "main":
			self.volume = {
			"title": PMPopitem("Volume:", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"value": PMPopitem(self.get_sound_volume(), self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMPopitem("Volume:", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"value_selected": PMPopitem(self.get_sound_volume(), self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"prev": self.volume_up,
			"next": self.volume_down
			}
			
			self.theme = {
			"title": PMPopitem("Theme:", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"value": PMPopitem(self.theme_list[self.theme_count], self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMPopitem("Theme:", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"value_selected": PMPopitem(self.theme_list[self.theme_count], self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"prev": self.theme_prev,
			"next": self.theme_next
			}
			
			popup = [self.volume, self.theme]
			
			return popup
			#self.themes = PMPopitem(get_theme(), cfg.popup_font, cfg.popup_menu_font_color)
			
		elif scene_type == "romlist":
			self.letter = PMPopitem("A", self.cfg.popup_font, self.cfg.popup_menu_font_color)
		return menu_items
	
	def update_menu(self):
		text_rect = pygame.Rect(0,0,300, self.item_height * len(self.list))
		self.menu = pygame.Surface([text_rect.w, text_rect.h], pygame.SRCALPHA, 32).convert_alpha()
		self.menu.fill(self.cfg.popup_menu_background_color, text_rect)
		
		y = 0
		for index, item in enumerate(self.list):
			if index == self.hover:
				self.menu.blit(item['title_selected'].image, (0,y))
			else:
				self.menu.blit(item['title'].image, (0,y))
			if self.selected and index == self.hover:
				self.menu.blit(item['value_selected'].image, (text_rect.w - item['value'].rect.w, y))
			else:
				self.menu.blit(item['value'].image, (text_rect.w - item['value'].rect.w, y))
				
			y += item['title'].rect.height
	
	#MENU ITEM FUNCTIONS
	def get_sound_volume(self):
		try: 
			volume = subprocess.check_output("amixer -c 0 get PCM | awk '/dB/ {print $4}'", shell=True)
			return volume.split("]")[0].split("[")[1]
		except:
			return "Not available"
			
	def volume_up(self):
		system("/usr/bin/amixer -q -c 0 sset PCM 3dB+ unmute nocap")
		
	def volume_down(self):
		system("/usr/bin/amixer -q -c 0 sset PCM 3dB- unmute nocap")
		
	def get_themes(self):
		a = [x for x in os.walk('/home/pi/pimame/pimame-menu/themes/').next()[1] if os.path.isfile('/home/pi/pimame/pimame-menu/themes/' + x + '/theme.yaml') and x != self.cfg.theme_name]
		a.insert(0, self.cfg.theme_name)
		return a
			
	def theme_prev(self):
		self.theme_count -= 1
		if self.theme_count < 0: self.theme_count = len(self.theme_list) - 1
		
	def theme_next(self):
		self.theme_count += 1
		if self.theme_count >= len(self.theme_list): self.theme_count = 0
		
		
class PMPopitem(pygame.sprite.Sprite):
	def __init__(self, label_text, font, color_fg, font_bold = False):
		pygame.sprite.Sprite.__init__(self)
		
		self.text = label_text
		self.color_fg = color_fg
		self.font = font
		
		#pygame faux bold font
		font.set_bold(font_bold)
		text = font.render(label_text, 1, color_fg).convert_alpha()
		text_rect = text.get_rect()
		if label_text == '': text_rect.w = 0
		self.image = pygame.Surface([text_rect.w, text_rect.h], pygame.SRCALPHA, 32).convert_alpha()
		self.image.blit(text, text_rect)

		
		self.rect = self.image.get_rect()