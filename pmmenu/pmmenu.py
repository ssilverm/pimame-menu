import os
import pygame, sys
from pygame.locals import *
from pmconfig import *
from pmheader import *
from pmselection import *
from pmlabel import *
from pmutil import *


class PMMenu:
	selected_index = 0

	def __init__(self, config_path):
		self.cfg = PMCfg(config_path)
		self.screen = self.cfg.screen
		self.header = PMHeader(self.cfg.options)
		self.selection = PMSelection(self.cfg.options)
		self.clock = pygame.time.Clock()

		if self.cfg.options.show_ip:
			self.ip_addr = PMLabel('Your IP is: ' + PMUtil.get_ip_addr(), self.cfg.options)

	def get_selected_item(self):
		return self.cfg.menu_items.sprites()[self.selected_index]

	def set_selected_index(self, new_selected_index):
		num_menu_items = len(self.cfg.menu_items.sprites())

		if new_selected_index < 0:
			new_selected_index = 0
		elif new_selected_index >= num_menu_items:
			new_selected_index = num_menu_items - 1

		self.selected_index = new_selected_index
		#self.selection.clear(self.screen)
		self.selection.update(self.get_selected_item())
		self.draw_items()
		self.draw_selection()

	def draw(self):
		self.draw_bg()
		self.draw_header()
		self.draw_ip_addr()
		self.draw_items()
		#self.draw_selection()
		self.set_selected_index(0)
		self.run()
		

	def draw_bg(self):
		self.screen.fill(self.cfg.options.background_color)

	def draw_header(self):
		# @TODO - how to prepare ahead of time:
		header = pygame.sprite.RenderPlain((self.header))
		header.draw(self.screen)

	def draw_ip_addr(self):
		if self.cfg.options.show_ip:
			label = pygame.sprite.RenderPlain((self.ip_addr))
			label.draw(self.screen)

	def draw_selection(self):
		selection = pygame.sprite.RenderPlain((self.selection))
		selection.draw(self.screen)

	def draw_items(self):
		padding = self.cfg.options.padding
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding

		x = padding
		y = self.header.rect.h + padding
		i = 1

		sprites = self.cfg.menu_items.sprites()
		for menu_item in sprites:
			menu_item.rect.x = x
			menu_item.rect.y = y

			if i % self.cfg.options.num_items_per_row == 0:
				x = padding
				y += self.cfg.options.item_height + padding
			else:
				x += item_width + padding

			i += 1

		self.cfg.menu_items.draw(self.screen)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONUP:
					pos = pygame.mouse.get_pos()

					# get all rects under cursor
					clicked_sprites = [s for s in self.cfg.menu_items if s.rect.collidepoint(pos)]

					if len(clicked_sprites) > 0:
						sprite = clicked_sprites[0]
						self.run_command_and_quit(sprite)
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_LEFT:
						self.set_selected_index(self.selected_index - 1)
					elif event.key == pygame.K_RIGHT:
						self.set_selected_index(self.selected_index + 1)
					elif event.key == pygame.K_UP:
						self.set_selected_index(self.selected_index - self.cfg.options.num_items_per_row)
					elif event.key == pygame.K_DOWN:
						self.set_selected_index(self.selected_index + self.cfg.options.num_items_per_row)
					elif event.key == pygame.K_RETURN:
						self.run_command_and_quit(self.get_selected_item())

			#######self.cfg.menu_items.draw(self.screen)

			####self.selection.update(self.get_selected_item())

			#pygame.display.update()
			pygame.display.flip()

			self.clock.tick(self.cfg.options.max_fps)

	def run_command_and_quit(self, sprite):
		sprite.run_command()
		pygame.quit()
		sys.exit()