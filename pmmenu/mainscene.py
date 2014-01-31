import pygame
import sys
from pmconfig import *
from pmheader import *
from pmselection import *
from pmlabel import *
from pmutil import *
from romlistscene import *

pygame.joystick.init()
js_count = pygame.joystick.get_count()
for i in range(js_count):
  js = pygame.joystick.Joystick(i)
  js.init()

class MainScene(object):
	selected_index = 0

	def __init__(self):
		super(MainScene, self).__init__()




	def get_selected_item(self):
		return self.grid.sprites()[self.selected_index]

	def set_selected_index(self, new_selected_index):
		num_menu_items = len(self.grid.sprites())

		if new_selected_index < 0:
			new_selected_index = 0
		elif new_selected_index >= num_menu_items:
			new_selected_index = num_menu_items - 1

		self.selected_index = new_selected_index
		#self.selection.clear(self.screen)
		self.selection.update(self.get_selected_item())
		self.draw_items()
		self.draw_selection()

	def draw_bg(self):
		self.screen.fill(self.cfg.options.background_color)

	def draw_header(self):
		# @TODO - how to prepare ahead of time:
		header = pygame.sprite.RenderPlain((self.header))
		header.draw(self.screen)

	def draw_ip_addr(self):
		if self.cfg.options.show_ip:
			try:
			    self.ip_addr = PMLabel(PMUtil.get_ip_addr(), self.cfg.options.font, self.cfg.options.text_color, self.cfg.options.item_color)
			except:
			    self.ip_addr = PMLabel("No Network Connection", self.cfg.options.font, self.cfg.options.text_color, self.cfg.options.item_color)
			label = pygame.sprite.RenderPlain((self.ip_addr))
			textpos = self.ip_addr.rect
			textpos.x = pygame.display.Info().current_w - textpos.width
			label.draw(self.screen)

	def draw_selection(self):
		selection = pygame.sprite.RenderPlain((self.selection))
		selection.draw(self.screen)

	def calc_num_items_per_page(self):
		padding = self.cfg.options.padding
		avail_height = pygame.display.Info().current_h - self.cfg.options.header_height - padding * 2
		item_height = self.cfg.options.item_height + padding
		num_rows = avail_height / item_height

		return num_rows * self.cfg.options.num_items_per_row

	def draw_items(self):
		padding = self.cfg.options.padding
		screen_width = pygame.display.Info().current_w
		item_width = ((screen_width - padding) / self.cfg.options.num_items_per_row) - padding

		x = padding
		y = self.header.rect.h + padding
		i = 1

		sprites = self.grid.sprites()
		for menu_item in sprites:
			menu_item.rect.x = x
			menu_item.rect.y = y

			if i % self.cfg.options.num_items_per_row == 0:
				x = padding
				y += self.cfg.options.item_height + padding
			else:
				x += item_width + padding

			i += 1

		# @TODO: make this background ahead of time!
		# @TODO: use this get_width() method everywhere instead of get_info()!
		background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
		background.fill(self.cfg.options.background_color)     # fill white
		self.grid.clear(self.screen, background)
		self.grid.draw(self.screen)


	def pre_render(self, screen):
		self.header = PMHeader(self.cfg.options)
		self.selection = PMSelection(self.cfg.options)
		self.grid = PMGrid(self.cfg.config['menu_items'], self.cfg.options)
		self.grid.set_num_items_per_page(self.calc_num_items_per_page())

		self.draw_bg()
		self.draw_header()
		self.draw_ip_addr()
		self.draw_items()
		#self.draw_selection()
		self.set_selected_index(0)

	def render(self, screen):
		pass

	def update(self):
		pass

	def handle_events(self, events):
		for event in events:

			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()

				# get all rects under cursor
				clicked_sprites = [s for s in self.grid if s.rect.collidepoint(pos)]

				if len(clicked_sprites) > 0:
					sprite = clicked_sprites[0]
					self.do_menu_item_action(sprite)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					self.set_selected_index(self.selected_index - 1)
				elif event.key == pygame.K_RIGHT:
					self.set_selected_index(self.selected_index + 1)
				elif event.key == pygame.K_UP:
					self.set_selected_index(self.selected_index - self.cfg.options.num_items_per_row)
				elif event.key == pygame.K_DOWN:
					self.set_selected_index(self.selected_index + self.cfg.options.num_items_per_row)
				elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
					self.do_menu_item_action(self.get_selected_item())
				elif event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
			elif event.type == pygame.JOYAXISMOTION:
				if event.dict['axis'] == 0 and event.dict['value'] < 0:
					self.set_selected_index(self.selected_index - 1)
				elif event.dict['axis'] == 0 and event.dict['value'] > 0:
					self.set_selected_index(self.selected_index + 1)
				elif event.dict['axis'] == 1 and event.dict['value'] < 0:
					self.set_selected_index(self.selected_index - self.cfg.options.num_items_per_row)
				elif event.dict['axis'] == 1 and event.dict['value'] > 0:
					self.set_selected_index(self.selected_index + self.cfg.options.num_items_per_row)
			elif event.type == pygame.JOYBUTTONDOWN:
				if event.button == 0:
					self.do_menu_item_action(self.get_selected_item())
				if event.button == 1:
					pygame.quit()
					sys.exit()

	#@TODO - change name:
	def do_menu_item_action(self, sprite):
		if sprite.type == PMMenuItem.ROM_LIST:
			self.manager.go_to(RomListScene(sprite.get_rom_list()))
		else:
			if sprite.command == PMMenuItem.PREV_PAGE:
				self.grid.prev_page()
			else:
				self.grid.next_page()
			#@TODO - Need to draw items here to the selection that
			#gets updated in set_selected_index is correctly positioned
			self.draw_items()
			self.set_selected_index(0)
