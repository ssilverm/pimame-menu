import pygame
import subprocess
import thread
import time
from pmcontrols import *
from pmpopup import *
from pmwarning import *
from pmcontrollerconfig import *
from pmconfig import *
from pmheader import *
from pmlabel import *
from pmutil import *
from romlistscene import *

import os, time

class MainScene(object):

	SCENE_NAME = 'main'
	update_display = []
	
	pre_rendered = False
	toggle_item_visibility = False

	def __init__(self):
		super(MainScene, self).__init__()

	def draw_bg(self):
		#self.screen.fill(self.cfg.options.background_color)
		self.screen.blit(self.cfg.options.pre_loaded_background, (0,0))
		
	def draw_header(self):
		# @TODO - how to prepare ahead of time:
		header = pygame.sprite.RenderPlain((self.header))
		header.draw(self.screen)

	def draw_ip_addr(self):
		displayString = ''

		if self.cfg.options.show_ip:
			try:
				displayString = PMUtil.get_ip_addr()
			except:
				displayString = "No Network Connection"

			self.ip_addr = PMLabel(displayString, self.cfg.options.font, self.cfg.options.default_font_color, self.cfg.options.default_font_background_color)
			label = pygame.sprite.RenderPlain((self.ip_addr))
			textpos = self.ip_addr.rect
			textpos.x = pygame.display.Info().current_w - textpos.width - self.cfg.options.padding
			textpos.y = self.cfg.options.padding
			label.draw(self.screen)

	def draw_update(self):
		displayString = ''

		if self.cfg.options.show_update:
			user_agent = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0"}
			try:
				import requests
				version_web = float( requests.get('http://www.pimame.org/version', headers = user_agent).text)
				version_current = float(open("../version", 'r').read())
				if version_current < version_web:
					displayString = "New Version Available"
			except:
				displayString = "Could not check for updates"

			self.update_label = PMLabel(displayString, self.cfg.options.font, self.cfg.options.default_font_color, self.cfg.options.default_font_background_color)
			label = pygame.sprite.RenderPlain((self.update_label))
			textpos = self.update_label.rect
			textpos.x = self.cfg.options.padding
			textpos.y = self.cfg.options.padding
			label.draw(self.screen)

	def pre_render(self, screen, call_render):
		if not self.pre_rendered:
			if  self.cfg.options.theme_style == "flow":
				from pmflow import *
				self.menu_style = PMFlow(self.cfg.options.options_menu_items, self.cfg)
			elif self.cfg.options.theme_style == 'slide':
				from pmslide import *
				self.menu_style = PMSlide(self.cfg.options.options_menu_items, self.cfg)
			else:
				from pmgrid import *
				self.menu_style = PMGrid(self.cfg.options.options_menu_items, self.cfg)
			
			
			self.popup = None
			self.warning = None
			self.pre_rendered = True
		
		if call_render: 
			if self.cfg.options.theme_style == 'slide': self.menu_style.selected_index = None #do this to fix premature update when backing out of romlist
			self.render(self.screen)
	
	def set_item_visibility(self):
		
		self.temp_cfg = {'item_height':self.cfg.options.item_height, 
								'num_items_per_row': self.cfg.options.num_items_per_row,
								'header_height': self.cfg.options.header_height}
								
		self.cfg.options.item_height = 100
		self.cfg.options.num_items_per_row = 10
		self.cfg.options.header_height = 0
		
		from pmgrid import *
		self.menu_style = PMGrid(self.cfg.options.options_menu_items, self.cfg, toggle_item_visibility = True)
		
		if self.warning:
			self.warning.handle_events('SELECT')
		
		self.draw_bg()
	
		self.menu_style.draw_items()
		self.menu_style.set_selected_index(None, play_sound = False)
		
		if self.cfg.options.fade_image:
			effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
		else:
			effect = PMUtil.fade_in(self, self.cfg.options.use_scene_transitions)
		self.cfg.options.fade_image.blit(self.screen,(0,0))
	
	def exit_item_visibility(self):
		self.toggle_item_visibility = False
		
		self.warning = PMWarning(self.screen, self.cfg.options, "Saving settings...\nThis may take a minute.", "ok", "HIDE_ICONS")
		
		for sprite in self.menu_style.sprites():
			self.cfg.config_cursor.execute('UPDATE menu_items SET visible=? where id=? and icon_id=?',(sprite.visible, sprite.id, sprite.icon_id))
			for index, item in enumerate(self.cfg.options.options_menu_items):
				if sprite.id == item['id']:
					self.cfg.options.options_menu_items[index]['visible'] = sprite.visible
		
		self.cfg.config_db.commit()
		self.cfg.options.item_height = self.temp_cfg['item_height']
		self.cfg.options.num_items_per_row = self.temp_cfg['num_items_per_row']
		self.cfg.options.header_height = self.temp_cfg['header_height']
		self.pre_rendered = False
		self.pre_render(self.screen, call_render = True)
		
		if self.warning:
			self.warning.handle_events('SELECT')
	
	def render(self, screen):
		self.last_update = 0
		self.header = PMHeader(self.cfg.options)
		self.draw_bg()
		self.draw_header()
		self.draw_ip_addr()
		self.draw_update()
		self.menu_style.draw_items()
		self.menu_style.set_selected_index(self.menu_style.selected_index, play_sound = False)
		#self.draw_selection()
		

		if self.cfg.options.fade_image:
			effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
		else:
			effect = PMUtil.fade_in(self, self.cfg.options.use_scene_transitions)
		self.cfg.options.fade_image.blit(self.screen,(0,0))
		
		
		if self.cfg.options.first_run:
			self.cfg.options.first_run = 0
			self.cfg.config_cursor.execute('UPDATE options SET first_run=0')
			self.cfg.config_db.commit()
			open('/home/pi/pimame/changelogs/firstrun_passed', 'a').close()
			self.warning = PMWarning(self.screen, self.cfg.options, 
				[["center","Welcome to PiPlay!"], 
				["center", ""],
				["left", "Here's the default control scheme:"],
				["left", "-Press 'Enter' or 'joystick button 1' to make selections"],
				["left", "-Press 'Esc' or 'joystick button 2' to go back"],
				["left", "-Press 'Tab' or 'joystick button 3' to open your popup menu"],
				["center", ""],
				["left", "*Hint: try the popup menu when viewing a list of roms"]], "ok", "FIRST_RUN")


	def update(self):
		if pygame.time.get_ticks() - self.last_update > 10000:
			update_screen = self.cfg.config_cursor.execute('SELECT roms_added FROM options').fetchone()[0]
			
			if update_screen:
				for menu_item in self.menu_style.menu_items:
					rect = menu_item.check_changes()

				self.menu_style.draw_items()
				self.menu_style.erase_selection()
				self.menu_style.draw_selection()
				pygame.display.update()
				self.cfg.config_cursor.execute('UPDATE options SET roms_added = 0')
				self.cfg.config_db.commit()
				
		self.last_update = pygame.time.get_ticks()

		
	def warning_check(self):
		if self.warning.answer:
				if self.warning.title == 'ROMS':
					if self.warning.answer == "YES": 
						PMUtil.run_command_and_continue('python /home/pi/pimame/pimame-menu/scraper/scrape_script.py --platform ' + str(self.menu_style.get_selected_item().id) + "%%" + str(self.menu_style.get_selected_item().id))
					else:
						self.warning = PMWarning(self.screen, self.cfg.options, "Would you like to add these items to your romlist without scraping?", "yes/no", "ROMS_CONFIRM")
					return
				
				if self.warning.title == 'ROMS_CONFIRM':
					if self.warning.answer == "YES":
						self.warning = PMWarning(self.screen, self.cfg.options, [["center","Updating roms."], ["center","This may take a minute."]], "ok", "")
						subprocess.call(['python', '/home/pi/pimame/pimame-menu/scraper/scrape_script.py','--crc', 'False', '--dont_match', 'True', '--platform', str(self.menu_style.get_selected_item().id)])
						self.warning = None
						self.do_menu_item_action(self.menu_style.get_selected_item())
						#PMUtil.run_command_and_continue('python /home/pi/pimame/pimame-menu/scraper/scrape_script.py --crc False --dont_match True --platform ' + str(self.menu_style.get_selected_item().id) + "%%" +str(self.menu_style.get_selected_item().id))
					else:
						self.warning = None
						self.do_menu_item_action(self.menu_style.get_selected_item())
					return
				try:
					if self.warning.title == 'KICKSTARTER':
						if self.warning.answer == "OK":
							self.warning = None
							self.ks_line = ''
							self.ks_range += 20
							if self.ks_range < len(self.cfg.options.ks):
								self.ks_line = ' \n '.join(self.cfg.ks[self.ks_range:self.ks_range + 19])
								self.warning = PMWarning(self.screen, self.cfg.options, self.ks_line, "ok/cancel", 'KICKSTARTER')
						else:
							self.warning = None
						return
				except:
					pass
				
				if self.warning.title == 'FIRST_RUN':
					if not self.warning.menu_open: 
						self.warning = None
					return
						
				if self.warning.title == 'CHANGELOG':
					self.warning = None
					return

	def handle_events(self, action):
		
		if self.warning and not self.warning.menu_open: self.warning = None
		
		# self.warning = PMWarning(self.screen, self.cfg.options, "message goes here", "yes/no")
		#answer will return False until selection -> yes, no, ok, or cancel
		if self.warning and self.warning.menu_open:
			self.warning.handle_events(action)
			self.warning_check()
				
		elif self.popup and self.popup.menu_open:
			status = self.popup.handle_events(action)
			if status == "CONTROLLER": self.popup = PMControllerConfig(self.screen, self.cfg.options)
			if status == "HIDE_ICONS": 
				status = None
				self.popup = None
				self.toggle_item_visibility = True
				self.warning = PMWarning(self.screen, self.cfg.options, "Loading icons...\nThis may take a minute.", "ok", "HIDE_ICONS")
				self.set_item_visibility()
		else:
			
			#NAVIGATE MAIN MENU
			if action in "LEFT/RIGHT/UP/DOWN":
				self.update_display += self.menu_style.handle_events(action)
			elif action == 'SELECT':
				sprite = self.menu_style.get_selected_item()
				#DISPLAY WARNING IF FILES HAVE CHANGED
				if sprite.warning == "!" and not self.warning: 
					self.cfg.options.menu_select_sound.play()
					self.warning = PMWarning(self.screen, self.cfg.options, "Some files have changed, would you like to scrape this folder for new roms?", "yes/no", "ROMS")
				elif not self.warning:
					self.do_menu_item_action(sprite)
			elif action == 'BACK' and self.cfg.options.allow_quit_to_console:
				if not self.toggle_item_visibility:
					self.cfg.options.menu_back_sound.play()
					effect = PMUtil.fade_out(self, self.cfg.options.use_scene_transitions)
				
					for wait_time in xrange(0,15):
						if not pygame.mixer.get_busy(): break 
						time.sleep(.01)

					pygame.quit()
					sys.exit()
				else:
					self.exit_item_visibility()
			
			#POPUP OPTIONS MENU
			elif action == 'MENU':
				if not self.toggle_item_visibility:
					self.popup = PMPopup(self.screen, self.manager.scene.SCENE_NAME, self.cfg, True)
				else:
					self.exit_item_visibility()
					
			#SHOW KICKSTARTER SUPPORTERS
			elif action == 'KICKSTARTER':
				if not self.warning:
					self.cfg.options.load_ks()
					self.ks_range = 0
					self.ks_line = ' \n '.join(self.cfg.ks[0:19])
					self.warning = PMWarning(self.screen, self.cfg.options, self.ks_line, "ok/cancel", 'KICKSTARTER')
			
			#MOUSE CLICK
			elif action == "MOUSEBUTTON":
				pos = pygame.mouse.get_pos()
				# get all rects under cursor
				clicked_sprites = [s for s in self.menu_style.sprites() if s.rect.collidepoint(pos)]
				
				if len(clicked_sprites) > 0:
					sprite = clicked_sprites[0]
					self.do_menu_item_action(sprite)
			
			#MOUSE MOVE
			elif action == "MOUSEMOVE":
				pos = pygame.mouse.get_pos()
				# get all rects under cursor
				if not self.menu_style.menu_items[self.menu_style.selected_index].rect.collidepoint(pos):
					clicked_sprites = [index for index, s in enumerate(self.menu_style.sprites()) if s.rect.collidepoint(pos)]
				
					if len(clicked_sprites) > 0:
						sprite = clicked_sprites[0]
						self.set_selected_index(sprite)
					
		self.update()
		return self.update_display

	#@TODO - change name:
	def do_menu_item_action(self, sprite):
		
		if self.toggle_item_visibility and sprite.type != PMMenuItem.NAVIGATION:
			sprite.visible = not sprite.visible
			sprite.update_image()
			self.menu_style.set_selected_index(self.menu_style.selected_index, False)
			pygame.display.update(sprite.rect)
		else:
			if sprite.type == PMMenuItem.EMULATOR:
					self.cfg.options.fade_image.blit(self.screen,(0,0))
					self.cfg.options.menu_select_sound.play()
					self.manager.go_to(RomListScene(sprite.get_rom_list(), sprite.id))
			elif sprite.command == 'exit_piplay':
					pygame.quit()
					sys.exit()
			elif sprite.type == PMMenuItem.COMMAND:
					self.cfg.options.menu_select_sound.play()
					PMUtil.run_command_and_continue(sprite.command)
			elif sprite.type == PMMenuItem.NAVIGATION:
					self.cfg.options.menu_navigation_sound.play()
					self.cfg.options.fade_image.blit(self.screen,(0,0))
					if sprite.command == PMMenuItem.PREV_PAGE:
						self.menu_style.prev_page()
						self.menu_style.draw_items()
						self.menu_style.set_selected_index(len(self.menu_style.sprites()) - 1, play_sound = False)
						effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
					else:
						self.menu_style.next_page()
						self.menu_style.draw_items()
						self.menu_style.set_selected_index(0, play_sound = False)
						effect = PMUtil.fade_into(self, self.cfg.options.fade_image, self.cfg.options.use_scene_transitions)
			else:
					self.cfg.options.menu_select_sound.play()
					PMUtil.run_command_and_continue(sprite.command)
