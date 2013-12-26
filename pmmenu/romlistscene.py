import pygame
import sys
from os import system
from pmlist import *

class RomListScene(object):

	selected_index = 0

	def __init__(self, rom_list):
		super(RomListScene, self).__init__()
		#self.font = pygame.font.SysFont('Arial', 52)
		#self.sfont = pygame.font.SysFont('Arial', 32)
		self.rom_list = rom_list
		

	def render(self, screen):
		self.list = PMList(self.rom_list, self.cfg.options)
		# ugly! 
		screen.fill(self.cfg.options.background_color)
		#text1 = self.font.render('Crazy Game', True, (255, 255, 255))
		#text2 = self.sfont.render('> press space to start <', True, (255, 255, 255))
		#screen.blit(text1, (200, 50))
		#screen.blit(text2, (200, 350))

		self.draw_list()
		self.update_selection()

		


	def update(self):
		pass

	def handle_events(self, events):
		for event in events:
			# if event.type == pygame.QUIT:
			# 	pygame.quit()
			# 	sys.exit()
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()

				# get all rects under cursor
				clicked_sprites = [s for s in self.list if s.rect.collidepoint(pos)]

				if len(clicked_sprites) > 0:
					sprite = clicked_sprites[0]
					self.run_command_and_quit(sprite)
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_UP:
					self.set_selected_index(self.selected_index - 1)
				elif event.key == pygame.K_DOWN:
					self.set_selected_index(self.selected_index + 1)
				elif event.key == pygame.K_RETURN:
					self.run_command_and_quit(self.get_selected_item())

	def set_selected_index(self, new_selected_index):
		print 'set selected index'
		print new_selected_index
		num_menu_items = len(self.list.sprites())
		print num_menu_items

		if new_selected_index < 0:
			new_selected_index = 0
		elif new_selected_index >= num_menu_items:
			new_selected_index = num_menu_items - 1

		self.selected_index = new_selected_index

		self.draw_list()
		self.update_selection()

	def get_selected_item(self):
		return self.list.sprites()[self.selected_index]

	def draw_list(self):
		#x = 0
		y = 0
		#i = 0

		for sprite in self.list.sprites():
			sprite.rect.x = 0
			sprite.rect.y = y

			y += sprite.rect.height

		#self.list.clear(self.screen, self.cfg.options.background_color)
		self.list.draw(self.screen)

	def update_selection(self):
		rect = self.get_selected_item().rect
		pygame.draw.rect(self.screen, self.cfg.options.rom_dot_color, rect)

	def run_command_and_quit(self, sprite):
		print sprite
		system(sprite.command)
		#sprite.run_command()
		#print 'here'
		#print sprite.get_rom_list()
		#self.manager.go_to(RomListScene(sprite.get_rom_list()))
		pygame.quit()
		sys.exit()
