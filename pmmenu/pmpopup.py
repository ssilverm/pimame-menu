import os
import pygame
import subprocess
import string
from os import system
from pmutil import *
from pmlabel import *
import sqlite3

class PMPopup(pygame.sprite.Sprite):

	def __init__(self, screen, scene_type, cfg, popup_open = False, list = None, ):
		pygame.sprite.Sprite.__init__(self)
		
		self.cfg = cfg
		self.scene_type = scene_type
		self.answer = []
		
		
		self.hover = 0
		self.selected = False
		self.menu_open = popup_open
		
		self.screen = screen
		self.effect = None
		
		self.menu_work = WorkFunctions(self.cfg)
		self.list = list if list != None else self.build_menu(self.scene_type)
		
		self.item_height = self.list[0]['title'].rect.h
		self.item_width = 0
		
		self.cfg.options.blur_image.blit(self.screen,(0,0))
		if self.cfg.options.use_scene_transitions:
			self.effect = PMUtil.blurSurf(self.cfg.options.blur_image, 20)
		else:
			self.effect = self.screen.copy()
		
		self.update_menu()

		self.screen.blit(self.effect, (0,0))
		pygame.display.update()
		
		self.rect = self.menu.get_rect()
		self.draw_menu()
	
	#MENU FUNCTIONS
	def hover_next(self, skip_to = None):
		if skip_to != None:
			self.hover = skip_to
		else:
			self.hover += 1
		if self.hover > (len(self.list)-1): self.hover = 0
		self.update_menu()
		
	def hover_prev(self, skip_to = None):
		if skip_to != None:
			self.hover = skip_to
		else:
			self.hover -= 1
		if self.hover < 0: self.hover = len(self.list)-1
		self.update_menu()
	
	def set_selected(self):
		self.selected = not self.selected
		self.update_menu()
		
		
	def build_menu(self, scene_type):
		if scene_type == "main":
			self.volume = {
			"title": PMLabel("System Volume:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(self.menu_work.get_sound_volume(), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("System Volume:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(self.menu_work.get_sound_volume(), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.volume_adjust,
			"next": self.menu_work.volume_adjust
			}
			
			if self.cfg.options.menu_music:
				self.music_volume = {
				"title": PMLabel("Music Volume:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
				"value": PMLabel(self.menu_work.get_music_volume(), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
				"title_selected": PMLabel("Music Volume:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
				"value_selected": PMLabel(self.menu_work.get_music_volume(), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
				"prev": self.menu_work.music_volume_adjust,
				"next": self.menu_work.music_volume_adjust
				}
			
			self.theme = {
			"title": PMLabel("Theme:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(self.menu_work.theme_list[self.menu_work.theme_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Theme:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(self.menu_work.theme_list[self.menu_work.theme_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.theme_scroll,
			"next": self.menu_work.theme_scroll
			}
			
			self.cursor = {
			"title": PMLabel("Show Cursor:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.cursor_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Show Cursor:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.cursor_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.cursor_swap,
			"next": self.menu_work.cursor_swap
			}
			
			self.transitions = {
			"title": PMLabel("Scene FX:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.scene_trans_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Scene FX:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.scene_trans_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.transition_swap,
			"next": self.menu_work.transition_swap
			}

			self.show_ip = {
			"title": PMLabel("Show IP:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.ip_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Show IP:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.ip_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.ip_swap,
			"next": self.menu_work.ip_swap
			}
			
			self.show_update = {
			"title": PMLabel("Show Update:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.update_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Show Update:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.update_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.update_swap,
			"next": self.menu_work.update_swap
			}
			
			self.sort_alphanum = {
			"title": PMLabel("Sort ABC:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.sort_abc_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Sort ABC:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.sort_abc_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.sort_abc_swap,
			"next": self.menu_work.sort_abc_swap
			}
			
			self.roms_first = {
			"title": PMLabel("Show roms 1st:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.roms_first_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Show roms 1st:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.roms_first_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.roms_first_swap,
			"next": self.menu_work.roms_first_swap
			}
			
			self.hide_system_tools = {
			"title": PMLabel("Hide System Tools:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.hide_system_tools_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Hide System Tools:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.hide_system_tools_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.hide_items_swap,
			"next": self.menu_work.hide_items_swap
			}
			
			self.quit_to_console = {
			"title": PMLabel("Allow PiPlay Quit:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.quit_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Allow PiPlay Quit:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.quit_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.quit_swap,
			"next": self.menu_work.quit_swap
			}
			
			self.controller_setup = {
			"title": PMLabel("Controller Setup", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel("", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Controller Setup", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel("", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.run_controller_setup,
			"next": self.run_controller_setup
			}
			

			
			popup = [self.volume, self.theme, self.cursor, self.transitions, self.show_ip, self.show_update, self.sort_alphanum,
						self.roms_first, self.hide_system_tools, self.quit_to_console, self.controller_setup]
			
			if self.cfg.options.menu_music:
				popup.insert(1, self.music_volume)
			
			return popup
			#self.themes = PMLabel(get_theme(), cfg.popup_font, cfg.popup_menu_font_color)
			
		elif scene_type == "romlist":
			
			self.letter = [{
			"title": PMLabel(temp_letter, self.cfg.options.popup_rom_letter_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel(temp_letter, self.cfg.options.popup_rom_letter_font, self.cfg.options.popup_menu_font_selected_color),
			"on_select": "self.update_answer(['letter_search', '" + str(temp_letter) + "'])",
			"prev": self.menu_work.abc_scroll,
			"next": self.menu_work.abc_scroll,
			} for temp_letter in map(chr, [35] + range(65, 91))]
			
			self.sort_by = {
			"title": PMLabel("Sort By:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(self.menu_work.sort_by_list[self.menu_work.sort_by_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Sort By:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(self.menu_work.sort_by_list[self.menu_work.sort_by_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.sort_by_scroll,
			"next": self.menu_work.sort_by_scroll
			}
						
			self.sort_order = {
			"title": PMLabel("Sort Order:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(self.menu_work.sort_order_list[self.menu_work.sort_order_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Sort Order:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(self.menu_work.sort_order_list[self.menu_work.sort_order_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.sort_order_scroll,
			"next": self.menu_work.sort_order_scroll
			}
			
			self.genres = {
			"title": PMLabel("Filter by Genre:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(self.menu_work.genre_list[self.menu_work.genre_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Filter by Genre (" + str(self.menu_work.genre_count) + '/' + str(len(self.menu_work.genre_list)) + "):", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(self.menu_work.genre_list[self.menu_work.genre_count], self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.genre_scroll,
			"next": self.menu_work.genre_scroll
			}
			
			self.hide_clones = {
			"title": PMLabel("Show Clones:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.show_clones_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Show Clones:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.show_clones_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.show_clones_swap,
			"next": self.menu_work.show_clones_swap
			}
			
			self.hide_unmatched = {
			"title": PMLabel("Show Unmatched Roms:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel(str(bool(self.menu_work.show_unmatched_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"title_selected": PMLabel("Show Unmatched Roms:", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel(str(bool(self.menu_work.show_unmatched_bool)), self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.menu_work.show_unmatched_swap,
			"next": self.menu_work.show_unmatched_swap
			}
			
			self.reset_rom_sort = {
			"title": PMLabel("Reset Search Options", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"value": PMLabel('', self.cfg.options.popup_font, self.cfg.options.popup_menu_font_color),
			"on_select": "self.reset_search()",
			"title_selected": PMLabel("Reset Search Options", self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"value_selected": PMLabel('', self.cfg.options.popup_font, self.cfg.options.popup_menu_font_selected_color),
			"prev": self.reset_search,
			"next": self.reset_search
			}
			
			self.list_items = [self.sort_by, self.sort_order, self.genres, self.hide_clones, self.hide_unmatched, self.reset_rom_sort]
			popup = self.letter + self.list_items
			
			return popup
	
	def reset_search(self):

		self.cfg.options.show_clones = self.menu_work.show_clones_bool = 1
		self.cfg.options.show_unmatched_roms = self.menu_work.show_unmatched_bool = 1
		self.menu_work.sort_by_count = 0
		self.menu_work.sort_order_count = 0
		self.menu_work.genre_count = 0
		self.cfg.options.rom_sort_category = 'Title'
		self.cfg.options.rom_sort_order = 'Ascending'
		self.cfg.options.rom_filter = 'All'
		
		update_options = (self.cfg.options.show_clones, self.cfg.options.show_unmatched_roms, 
									self.cfg.options.rom_sort_category, self.cfg.options.rom_sort_order,
									self.cfg.options.rom_filter)
		
		self.cfg.config_cursor.execute('UPDATE options SET show_rom_clones=?, show_unmatched_roms=?, ' +
													'sort_roms_by=?, rom_sort_order=?, filter_roms_by=?', update_options)
		self.cfg.config_db.commit()
		
		#un-select and redraw
		self.selected = False
		self.list = self.build_menu(self.scene_type)
		self.update_menu()
		self.draw_menu()
		
	def update_answer(self, answer):
		self.answer = answer
		return self.answer
	
	def run_controller_setup(self):
		self.screen.blit(self.cfg.options.blur_image,(0,0))
		return "CONTROLLER"
	
	def update_menu(self):
		if self.scene_type == 'main':
		
			if self.item_width == 0: 
				self.item_width = max(self.list, key=lambda x: x['title'].rect.w)['title'].rect.w + max(self.list, key=lambda x: x['value'].rect.w)['value'].rect.w + 40

			text_rect = pygame.Rect(0,0, self.item_width, (self.item_height * len(self.list)) + 20)
			self.menu = pygame.Surface([text_rect.w, text_rect.h], pygame.SRCALPHA, 32).convert_alpha()
			self.menu.fill(self.cfg.options.popup_menu_background_color, text_rect)
			
			y = 10
			x = 10
			for index, item in enumerate(self.list):
				if index == self.hover:
					self.menu.blit(item['title_selected'].image, (x,y))
				else:
					self.menu.blit(item['title'].image, (x,y))
				if self.selected and index == self.hover:
					self.menu.blit(item['value_selected'].image, (text_rect.w - item['value'].rect.w - x, y))
				else:
					self.menu.blit(item['value'].image, (text_rect.w - item['value'].rect.w - x, y))
					
				y += item['title'].rect.height
				
		elif self.scene_type == 'romlist':
			
			#text_rect = pygame.Rect(0,0, int(self.item_height * 1.5), int(self.item_height * 1.5))
			text_rect = pygame.Rect(0,0, int(self.screen.get_width() *.8), int(self.screen.get_height() * .8))
			self.menu = pygame.Surface([text_rect.w, text_rect.h], pygame.SRCALPHA, 32).convert_alpha()
			self.menu.fill(self.cfg.options.popup_menu_background_color, text_rect)
			
			
			x = 10
			x_spacing = int((text_rect.w - 20) / 27)
			x += x_spacing/2
			y = 10
			for index, item in enumerate(self.letter):
				if index == self.hover:
					self.menu.blit(item['title_selected'].image, (x, y))
				else:
					self.menu.blit(item['title'].image, (x, y))
				x += x_spacing
			
			x = 10
			y += 25
			
			if self.item_width == 0: 
				self.item_width = max(self.list_items, key=lambda x: x['title'].rect.w)['title'].rect.w + 40 + x
			
			for index, item in enumerate(self.list):
				if not item in self.letter:
					if index == self.hover:
						self.menu.blit(item['title_selected'].image, (x,y))
					else:
						self.menu.blit(item['title'].image, (x,y))
					if self.selected and index == self.hover:
						self.menu.blit(item['value_selected'].image, (self.item_width, y))
					else:
						self.menu.blit(item['value'].image, (self.item_width, y))
						
					y += item['title'].rect.height
					
			
	def handle_events(self, action):
		
		if action == 'LEFT':
			self.cfg.options.menu_move_sound.play()
			if not self.selected: self.hover_prev()
			else:
				self.list[self.hover]['prev']('prev')
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
			
		elif action == 'RIGHT':
			self.cfg.options.menu_move_sound.play()
			if not self.selected: self.hover_next()
			else: 
				self.list[self.hover]['next']('next')
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
			
		elif action == 'UP':
			self.cfg.options.menu_move_sound.play()
			if (not self.selected) and self.scene_type == 'romlist' and self.hover == 27: self.hover_prev(skip_to=0)
			elif not self.selected: self.hover_prev()
			else:
				self.list[self.hover]['next']('next')
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
			
		elif action == 'DOWN':
			self.cfg.options.menu_move_sound.play()
			if (not self.selected) and self.scene_type == 'romlist' and self.hover < 27: self.hover_next(skip_to=27)
			elif not self.selected: self.hover_next()
			else: 
				self.list[self.hover]['prev']('prev')
				self.list = self.build_menu(self.scene_type)
				self.update_menu()
			self.draw_menu()
			
		elif action == 'MENU':
			if self.selected:
				action = 'SELECT'
			else:
				self.cfg.options.menu_back_sound.play()
				self.menu_open = False
				self.on_exit_actions()
				
		elif action == 'BACK':
				self.cfg.options.menu_back_sound.play()
				self.menu_open = False
				self.on_exit_actions()
		
		if action == 'SELECT':
			if self.scene_type != 'romlist':
				self.cfg.options.menu_select_sound.play()
				self.selected = not self.selected
				self.update_menu()
				self.draw_menu()
				#check if controller setup is selected
				if self.selected and (self.list[self.hover] == self.controller_setup):
					return  self.run_controller_setup()
			else:
				self.cfg.options.menu_select_sound.play()
				self.selected = not self.selected
				if self.selected:
					try: exec( self.list[self.hover]['on_select'] )
					except KeyError: pass
				self.cfg.options.menu_back_sound.play()
				self.update_menu()
				self.draw_menu()

			
		return None
				
	def on_exit_actions(self):
	
		requires_restart = False
		
		if self.scene_type == 'main':
			#SOUND
			system("alsactl --file ~/pimame/config/piplay-sound.state store")
				
			#THEME
			if self.menu_work.theme_list[self.menu_work.theme_count] != self.cfg.options.theme_name:
				requires_restart = True
				
			#SORT EMU BY ALPHANUM
			if self.cfg.options.sort_items_alphanum != self.menu_work.sort_abc_bool:
				requires_restart = True
			
			#SORT EMU WITH ROMS FIRST
			if self.cfg.options.sort_items_with_roms_first != self.menu_work.roms_first_bool:
				requires_restart = True
			
			#HIDE SYSTEM TOOLS
			if self.cfg.options.hide_system_tools != self.menu_work.hide_system_tools_bool:
				requires_restart = True
				
			update_options = (self.menu_work.theme_list[self.menu_work.theme_count], self.menu_work.cursor_bool, (self.menu_work.music_volume / 100),
								 self.menu_work.scene_trans_bool, self.menu_work.ip_bool, self.menu_work.update_bool, self.menu_work.sort_abc_bool,  
								self.menu_work.roms_first_bool, self.menu_work.hide_system_tools_bool, self.menu_work.quit_bool)
								
			self.cfg.config_cursor.execute('UPDATE options SET theme_pack=?, show_cursor=?, ' + 
				'default_music_volume=?, use_scene_transitions=?, show_ip=?, show_update=?, ' + 
				'sort_items_alphanum=?, sort_items_with_roms_first=?, hide_system_tools=?, allow_quit_to_console=?', update_options)
			self.cfg.config_db.commit()
			
			pygame.mouse.set_visible(self.menu_work.cursor_bool)
			self.cfg.options.use_scene_transitions = self.menu_work.scene_trans_bool
			self.cfg.options.show_ip = self.menu_work.ip_bool
			self.cfg.options.show_update = self.menu_work.update_bool
			self.cfg.options.sort_items_alphanum = self.menu_work.sort_abc_bool
			self.cfg.options.sort_items_with_roms_first = self.menu_work.roms_first_bool
			self.cfg.options.hide_system_tools = self.menu_work.hide_system_tools_bool
			self.cfg.options.allow_quit_to_console = self.menu_work.quit_bool

		
		elif self.scene_type == 'romlist':
			#romlist options
			self.cfg.options.show_clones = self.menu_work.show_clones_bool
			self.cfg.options.show_unmatched_roms = self.menu_work.show_unmatched_bool
			self.cfg.options.rom_sort_category = self.menu_work.sort_by_list[self.menu_work.sort_by_count].lower()
			self.cfg.options.rom_sort_order = self.menu_work.sort_order_list[self.menu_work.sort_order_count].lower()
			self.cfg.options.rom_filter = self.menu_work.genre_list[self.menu_work.genre_count]
			
			update_options = (self.cfg.options.show_clones, self.cfg.options.show_unmatched_roms, 
										self.cfg.options.rom_sort_category, self.cfg.options.rom_sort_order,
										self.cfg.options.rom_filter)
			
			self.cfg.config_cursor.execute('UPDATE options SET show_rom_clones=?, show_unmatched_roms=?, ' +
														'sort_roms_by=?, rom_sort_order=?, filter_roms_by=?', update_options)
			self.cfg.config_db.commit()
		
		
		if requires_restart: 
			system('clear')
			PMUtil.run_command_and_continue('echo Changing settings and restarting PiPlay')
		
		self.screen.blit(self.cfg.options.blur_image,(0,0))
		pygame.display.update()
		
	def draw_menu(self):
		self.rect.x = (pygame.display.Info().current_w - self.rect.w)/2
		self.rect.y =  (pygame.display.Info().current_h - self.rect.h)/2
		self.screen.blit(self.effect, (self.rect.x, self.rect.y), self.rect)
		self.screen.blit(self.menu, (self.rect.x, self.rect.y))
		pygame.display.update(self.rect)
		

		
class WorkFunctions():
	def __init__(self, cfg):
		
		#mainscene
		self.cfg= cfg
		self.theme_count = 0
		self.theme_list = self.get_themes()
		self.music_volume = round(int(pygame.mixer.music.get_volume() * 100), -1)
		self.cursor_bool = self.cfg.options.show_cursor
		self.scene_trans_bool = self.cfg.options.use_scene_transitions
		self.ip_bool = self.cfg.options.show_ip
		self.update_bool = self.cfg.options.show_update
		self.sort_abc_bool = self.cfg.options.sort_items_alphanum
		self.roms_first_bool = self.cfg.options.sort_items_with_roms_first
		self.hide_system_tools_bool = self.cfg.options.hide_system_tools
		self.quit_bool = self.cfg.options.allow_quit_to_console
		self.scraper_clones_bool = self.cfg.options.show_clones

		
		#romlist
		self.abc_count = 0
		self.abc_list = map(chr, range(65, 91))
		
		self.sort_by_list = ['Title', 'Release_date', 'Players', 'Rating', 'Esrb', 'Coop', 'Publisher', 'Developer']
		try: self.sort_by_count = self.sort_by_list.index(self.cfg.options.rom_sort_category.capitalize())
		except ValueError: self.sort_by_count = 0
		
		self.sort_order_list = ['Ascending', 'Descending']
		try: self.sort_order_count = self.sort_order_list.index(self.cfg.options.rom_sort_order.capitalize())
		except ValueError: self.sort_order_count = 0
		
		self.genre_list = ['All', 'Action', 'Sports', 'Platform', 'Racing', 'Adventure', 'RPG', 'Puzzle', 'Shooter', 'Side-Scroller', 'Fighting', 'Misc.Sports', 'Strategy', 'Run-and-Gun', 'Soccer', 'Football(World)', 'Football(USA)', "Beat'em Up", 'Arcade', 'Baseball', 'Basketball', 'Scrolling-Shooter', 'Golf', 'Turn-Based', 'Vertical-Scroller', 'Hockey']
		try: self.genre_count = self.genre_list.index(self.cfg.options.rom_filter)
		except ValueError: self.genre_count = 0
		
		self.show_clones_bool = self.cfg.options.show_clones
		self.show_unmatched_bool = self.cfg.options.show_unmatched_roms
		
	
		#MENU ITEM FUNCTIONS
	def get_sound_volume(self):
		try: 
			volume = subprocess.check_output("amixer -c 0 get PCM | awk '/dB/ {print $4}'", shell=True)
			return volume.split("]")[0].split("[")[1]
		except:
			return "Not available"
			
	def volume_adjust(self, direction):
		if direction == 'next': #volume up
			system("/usr/bin/amixer -q -c 0 sset PCM 3dB+ unmute nocap")
		else: #volume down
			system("/usr/bin/amixer -q -c 0 sset PCM 3dB- unmute nocap")
		
		
	def get_music_volume(self):
		try: 
			return (str(int(round((pygame.mixer.music.get_volume() * 100), -1))) + "%")
		except:
			return "Not available"
			
	def music_volume_adjust(self, direction):
		if direction == 'next': #volume up
			self.music_volume = min(round(int(pygame.mixer.music.get_volume() * 100), -1) + 10, 100)
			pygame.mixer.music.set_volume(self.music_volume / 100)
			if self.music_volume == 10:
				pygame.mixer.music.play(-1)
		else:
			self.music_volume = max(round(int(pygame.mixer.music.get_volume() * 100), -1) - 10, 0)
			pygame.mixer.music.set_volume(self.music_volume / 100)
			if self.music_volume == 0:
				pygame.mixer.music.stop()
		
	def get_themes(self):
		a = [x for x in os.walk('/home/pi/pimame/pimame-menu/themes/').next()[1] if os.path.isfile('/home/pi/pimame/pimame-menu/themes/' + x + '/theme.yaml') and x != self.cfg.options.theme_name]
		a.insert(0, self.cfg.options.theme_name)
		return a
			
	def theme_scroll(self, direction):
		if direction == 'next':
			self.theme_count += 1
			if self.theme_count >= len(self.theme_list): self.theme_count = 0
		else:
			self.theme_count -= 1
			if self.theme_count < 0: self.theme_count = len(self.theme_list) - 1
		
	def cursor_swap(self, calling_event):
		self.cursor_bool = not self.cursor_bool
		return self.cursor_bool
	
	def transition_swap(self, calling_event):
		self.scene_trans_bool = not self.scene_trans_bool
		return self.scene_trans_bool
		
	def ip_swap(self, calling_event):
		self.ip_bool = not self.ip_bool
		return self.ip_bool
		
	def update_swap(self, calling_event):
		self.update_bool = not self.update_bool
		return self.update_bool
		
	def sort_abc_swap(self, calling_event):
		self.sort_abc_bool = not self.sort_abc_bool
		return self.sort_abc_bool
		
	def roms_first_swap(self, calling_event):
		self.roms_first_bool = not self.roms_first_bool
		return self.roms_first_bool
		
	def hide_items_swap(self, calling_event):
		self.hide_system_tools_bool = not self.hide_system_tools_bool
		return self.hide_system_tools_bool
		
	def quit_swap(self, calling_event):
		self.quit_bool = not self.quit_bool
		return self.quit_bool
		
	def scraper_clones_swap(self, calling_event):
		self.scraper_clones_bool = not self.scraper_clones_bool
		return self.scraper_clones_bool
		
	#ROMLIST FUNCTIONS
	def abc_scroll(self, direction):
		if direction == 'next':
			self.abc_count += 1
			if self.abc_count >= len(self.abc_list): self.abc_count = 0
		else:
			self.abc_count -= 1
			if self.abc_count < 0: self.abc_count = len(self.abc_list) - 1

	
	def abc_find(self, list, letter):
        #Avoid returning anything that doesn't have a 'command' (ex. <-Back)
		for index, i in enumerate(list):
			if ord(i['title'][0].upper()) >= ord(letter) and i['command']:
				return index
		return 0
	
	def sort_by_scroll(self, direction):
		if direction == 'next':
			self.sort_by_count += 1
			if self.sort_by_count >= len(self.sort_by_list): self.sort_by_count = 0
		elif direction:
			self.sort_by_count -= 1
			if self.sort_by_count < 0: self.sort_by_count = len(self.sort_by_list) - 1	
		
	def sort_order_scroll(self, direction):
		if direction == 'next':
			self.sort_order_count += 1
			if self.sort_order_count >= len(self.sort_order_list): self.sort_order_count = 0
		elif direction:
			self.sort_order_count -= 1
			if self.sort_order_count < 0: self.sort_order_count = len(self.sort_order_list) - 1	
			
	def genre_scroll(self, direction):
		if direction == 'next':
			self.genre_count += 1
			if self.genre_count >= len(self.genre_list): self.genre_count = 0
		elif direction:
			self.genre_count -= 1
			if self.genre_count < 0: self.genre_count = len(self.genre_list) - 1
	
	def show_clones_swap(self, calling_event):
		self.show_clones_bool = not self.show_clones_bool
		return self.show_clones_bool
		
	def show_unmatched_swap(self, calling_event):
		self.show_unmatched_bool = not self.show_unmatched_bool
		return self.show_unmatched_bool
