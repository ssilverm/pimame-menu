import os
import pygame
import subprocess
import string
from os import system
from pmcontrols import *
from pmutil import *

class PMPopup(pygame.sprite.Sprite):

	def __init__(self, scene_type, cfg, list = None):
		pygame.sprite.Sprite.__init__(self)
		
		self.cfg = cfg
		self.scene_type = scene_type
		
		
		self.hover = 0
		self.selected = False
		self.menu_open = False
		
		self.screen = None
		self.effect = None
		
		self.menu_work = WorkFunctions(self.cfg)
		self.list = self.build_menu(self.scene_type)
		self.item_height = self.list[0]['value'].rect.h
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
			"value": PMPopitem(self.menu_work.get_sound_volume(), self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMPopitem("Volume:", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"value_selected": PMPopitem(self.menu_work.get_sound_volume(), self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"prev": self.menu_work.volume_up,
			"next": self.menu_work.volume_down
			}
			
			self.theme = {
			"title": PMPopitem("Theme:", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"value": PMPopitem(self.menu_work.theme_list[self.menu_work.theme_count], self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMPopitem("Theme:", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"value_selected": PMPopitem(self.menu_work.theme_list[self.menu_work.theme_count], self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"prev": self.menu_work.theme_prev,
			"next": self.menu_work.theme_next
			}
			
			popup = [self.volume, self.theme]
			
			return popup
			#self.themes = PMPopitem(get_theme(), cfg.popup_font, cfg.popup_menu_font_color)
			
		elif scene_type == "romlist":
			
			self.selected = True
			
			self.letter = {
			"value": PMPopitem(self.menu_work.abc_list[self.menu_work.abc_count], self.cfg.popup_rom_letter_font, self.cfg.popup_menu_font_color),
			"value_selected": PMPopitem(self.menu_work.abc_list[self.menu_work.abc_count], self.cfg.popup_rom_letter_font, self.cfg.popup_menu_font_selected_color),
			"prev": self.menu_work.abc_prev,
			"next": self.menu_work.abc_next,
			}
			
			popup = [self.letter]
			
			return popup
	
	def update_menu(self):
		if self.scene_type == 'main':
			
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
				
		elif self.scene_type == 'romlist':
			
			text_rect = pygame.Rect(0,0, int(self.item_height * 1.5), int(self.item_height * 1.5))
			self.menu = pygame.Surface([text_rect.w, text_rect.h], pygame.SRCALPHA, 32).convert_alpha()
			self.menu.fill(self.cfg.popup_menu_background_color, text_rect)
			
			
			y = 0
			for index, item in enumerate(self.list):
				self.menu.blit(item['value'].image, ((text_rect.w - item['value'].rect.w)/2, (text_rect.h - item['value'].rect.h)/2))
					
				y += item['value'].rect.height
			
	def handle_events(self, action, screen, effect):
		self.screen = screen
		self.effect = effect
		
		if action == 'LEFT':
			self.cfg.menu_navigation_sound.play()
			if not self.selected: self.hover_prev()
			else:
				self.list[self.hover]['prev']()
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
		elif action == 'RIGHT':
			self.cfg.menu_navigation_sound.play()
			if not self.selected: self.hover_next()
			else: 
				self.list[self.hover]['next']()
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
		elif action == 'UP':
			self.cfg.menu_navigation_sound.play()
			if not self.selected: self.hover_prev()
			else:
				self.list[self.hover]['prev']()
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
		elif action == 'DOWN':
			self.cfg.menu_navigation_sound.play()
			if not self.selected: self.hover_next()
			else: 
				self.list[self.hover]['next']()
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
		elif action == 'MENU':
			if self.selected and self.scene_type != 'romlist':
				action = 'SELECT'
			else:
				self.cfg.menu_back_sound.play()
				self.menu_open = False
				self.screen.blit(self.cfg.fade_image,(0,0))
				if self.menu_work.theme_list[self.menu_work.theme_count] != self.cfg.theme_name:
					PMUtil.replace('/home/pi/pimame/pimame-menu/config.yaml', 'theme_pack: "' + self.cfg.theme_name, 'theme_pack: "' + self.menu_work.theme_list[self.menu_work.theme_count])
					PMUtil.run_command_and_continue('echo Changing theme and restarting PiPlay')
		elif action == 'BACK':
				self.cfg.menu_back_sound.play()
				self.menu_open = False
				self.screen.blit(self.cfg.fade_image,(0,0))
				if self.menu_work.theme_list[self.menu_work.theme_count] != self.cfg.theme_name:
					PMUtil.replace('/home/pi/pimame/pimame-menu/config.yaml', 'theme_pack: "' + self.cfg.theme_name, 'theme_pack: "' + self.menu_work.theme_list[self.menu_work.theme_count])
					PMUtil.run_command_and_continue('echo Changing theme and restarting PiPlay')
		
		if action == 'SELECT':
			if self.scene_type != 'romlist':
				self.cfg.menu_select_sound.play()
				self.selected = not self.selected
				self.update_menu()
				self.draw_menu()
				
			
				
	
	def draw_menu(self):
		self.screen.blit(self.effect,(0,0))
		self.screen.blit(self.menu, ((pygame.display.Info().current_w - self.rect.w)/2, (pygame.display.Info().current_h - self.rect.h)/2))
		

		
class WorkFunctions():
	def __init__(self, cfg):
		self.cfg = cfg
		self.theme_count = 0
		self.theme_list = self.get_themes()
		self.abc_count = 0
		self.abc_list = map(chr, range(65, 91))
	
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
		
	def abc_prev(self):
		self.abc_count -= 1
		if self.abc_count < 0: self.abc_count = len(self.abc_list) - 1
		
	def abc_next(self):
		self.abc_count += 1
		if self.abc_count >= len(self.abc_list): self.abc_count = 0
	
	
	def abc_find(self, list):
        #list = ['alpha','bravo','charlie','delta','echo','foxtrot','golf','hotel','india',
                #'juliet','kilo','lima','mike','november','oscar','papa','Quebec','romeo',
                #'sierra','tango','uniform','victor','whiskey','x-ray','yankee','zulu']

        #abc_list = map(chr, range(65,91))
		for index, i in enumerate(list):
			
			if ord(i['title'][0].upper()) >= ord(self.abc_list[self.abc_count]):
				return index
		return 0

		
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