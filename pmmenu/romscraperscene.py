import pygame
from pmcontrols import *
from pmpopup import *
from pmconfig import *
from pmheader import *
from pmselection import *
from pmlabel import *
from pmutil import *
import os
import sqlite3

class RomScraperScene(object):

	SCENE_NAME = 'romscraper'
	update_display = []
	
	selected_index = 0
	pre_rendered = False

	def __init__(self):
		super(MainScene, self).__init__()
		
	def draw_bg(self):
		self.screen.fill(self.cfg.options.background_color)
		self.screen.blit(self.cfg.options.pre_loaded_background, (0,0))
		
	def draw_items(self):
		pass

	def pre_render(self, screen, call_render):
		self.render(self.screen)
		
	def render(self, screen):
		self.draw_bg()
		self.draw_items()

	def update(self):
		pass
					

	def handle_events(self, action):
		pass