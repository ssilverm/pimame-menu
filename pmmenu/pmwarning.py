import os
import pygame
from pmcontrols import *
from pmutil import *
from pmlabel import *

class PMWarning(pygame.sprite.Sprite):

	def __init__(self, screen, cfg, message, buttons = "ok", title = "warning", max_line_length = 45):
		pygame.sprite.Sprite.__init__(self)
		
		self.cfg = cfg
		self.screen = screen
		self.buttons = buttons
		self.title = title
		
		self.hover = 0
		self.selected = False
		self.menu_open = True
		
		self.effect = None
		self.rect = None
		self.answer = False
		
		self.item_width = 0
		self.item_height = 0
		
		self.cfg.blur_image.blit(self.screen,(0,0))
		if self.cfg.use_scene_transitions:
			self.effect = PMUtil.blurSurf(self.cfg.blur_image, 20)
		else:
			self.effect = self.screen.copy()

		self.list = BuildMessage(cfg, message, max_line_length)
		self.update_menu()
		self.rect = self.menu.get_rect()
		
		self.draw_menu()
	
	#MENU FUNCTIONS
	def hover_next(self):
		self.hover += 1
		if self.hover > (len(self.list.options[self.buttons])-1): self.hover = 0
		self.update_menu()
		
	def hover_prev(self):
		self.hover -= 1
		if self.hover < 0: self.hover = len(self.list.options[self.buttons])-1
		self.update_menu()
	
	def set_selected(self):
		self.selected = not self.selected
		self.update_menu()
		
	
	def update_menu(self):
			
			self.menu = pygame.Surface([self.list.rect.w, self.list.rect.h], pygame.SRCALPHA, 32).convert_alpha()
			self.menu.blit(self.list.message, (0,0))
			
			y = self.list.rect.h
			spacer = (self.list.rect.w - 20) / len(self.list.options[self.buttons])
			chunk = ((self.list.rect.w - 20) / len(self.list.options[self.buttons])) / 2 + 10
			for index, item in enumerate(self.list.options[self.buttons]):
				x = chunk + (spacer * index)
				if index == self.hover:
					self.menu.blit(item['title_selected'].image, (x - (item['title_selected'].rect.w / 2), y - item['title_selected'].rect.height - 20))
				else:
					self.menu.blit(item['title'].image, (x - (item['title'].rect.w / 2), y - item['title'].rect.height - 20))
					

			
	def handle_events(self, action):
		self.answer = False
		
		if action == 'LEFT':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_prev()
			self.draw_menu()
		elif action == 'RIGHT':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_next()
			self.draw_menu()
		elif action == 'UP':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_prev()
			self.draw_menu()
		elif action == 'DOWN':
			self.cfg.menu_move_sound.play()
			if not self.selected: self.hover_next()
			self.draw_menu()
		#REQUIRE ANSWER FROM USER
		#DON'T ALLOW BACK ACTION
		'''elif action == 'BACK':
				self.cfg.menu_back_sound.play()
				self.menu_open = False
				self.screen.blit(self.cfg.blur_image,(0,0))
				pygame.display.update()
				self.screen.blit(self.cfg.blur_image,(0,0))'''
		
		if action == 'SELECT':
			self.cfg.menu_select_sound.play()
			self.menu_open = False
			self.screen.blit(self.cfg.blur_image,(0,0))
			pygame.display.update()
			self.answer = self.list.options[self.buttons][self.hover]['return']
				
		
	def draw_menu(self):
			self.screen.blit(self.effect,(0,0))
			self.screen.blit(self.menu, ((pygame.display.Info().current_w - self.rect.w)/2, (pygame.display.Info().current_h - self.rect.h)/2))
			pygame.display.update()
		
	def take_action(self, dict):
		if self.answer in dict:
			PMUtil.run_command_and_continue(dict[self.answer])
		

		
class BuildMessage():
		def __init__(self, cfg, message, max_line_length = 45):
			text_line = ''
			self.cfg = cfg
			self.lines = []
			
			try:
				message + "1"
				message = message.replace('\n', ' \n ')
				for word in message.split(' '):
					if (len(text_line) + len(word) > max_line_length) or ('\n' in word):
						self.lines.append(["center", text_line.strip()])
						text_line = ''
					if word != '\n': text_line += word + ' '
				self.lines.append(text_line)
			except:
				self.lines = message
				

			#self.lines = [PMLabel(line[1], self.cfg.popup_font, self.cfg.popup_menu_font_color) for line in self.lines]
			self.lines = [([line[0], PMLabel(line[1], self.cfg.popup_font, self.cfg.popup_menu_font_color)]) for line in self.lines]
			
			y = 10
			self.item_width = max(self.lines, key=lambda x: x[1].rect.w)[1].rect.w + 20
			self.item_height = self.lines[0][1].rect.h * (len(self.lines) + 1) + 40
			
			self.message = pygame.Surface([self.item_width, self.item_height], pygame.SRCALPHA, 32).convert_alpha()
			self.rect = self.message.get_rect()
			self.message.fill(self.cfg.popup_menu_background_color, self.rect)
			
			for line in self.lines:
				if line[0] == 'center': self.message.blit( line[1].image, ((self.item_width - line[1].rect.w) / 2, y) )
				if line[0] == 'left': self.message.blit( line[1].image, (10, y) )
				if line[0] == 'right': self.message.blit( line[1].image, ((self.item_width - line[1].rect.w - 10), y) )
				
				y += line[1].rect.h
			
			self.OK = {
			"title": PMLabel("OK", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMLabel("[OK]", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"return": 'OK'
			}
			
			self.CANCEL = {
			"title": PMLabel("CANCEL", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMLabel("[CANCEL]", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"return": 'CANCEL'
			}
			
			self.YES = {
			"title": PMLabel("YES", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMLabel("[YES]", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"return": 'YES'
			}
			
			self.NO = {
			"title": PMLabel("NO", self.cfg.popup_font, self.cfg.popup_menu_font_color),
			"title_selected": PMLabel("[NO]", self.cfg.popup_font, self.cfg.popup_menu_font_selected_color),
			"return": 'NO'
			}
			
			self.options = {
			"ok": [self.OK],
			"ok/cancel": [self.OK, self.CANCEL], 
			"yes/no": [self.YES, self.NO], 
			"yes/no/cancel": [self.YES, self.NO, self.CANCEL]
			}
		
