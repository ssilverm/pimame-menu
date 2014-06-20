import pygame
import subprocess
import re
import sys
import time
from os import system

class PMUtil:
	@staticmethod
	def get_ip_addr():
		wlan = subprocess.check_output("/sbin/ifconfig wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True)
		ether = subprocess.check_output("/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'", shell=True)

		myip = ''
		if wlan != '':
			myip += wlan
		if ether != '':
			myip += ' ' + ether

		m = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", myip)
		myip = m.group(0)

		return myip

	@staticmethod
	def run_command_and_continue(command):
		pygame.quit()
		time.sleep(1)
		system(command + " && export LD_LIBRARY_PATH= &&  python " + sys.argv[0])
		sys.exit()
	
	@staticmethod
	def fade_out(self):
		background = pygame.Surface([self.screen.get_width(), self.screen.get_height()], pygame.SRCALPHA, 32).convert_alpha()
		background.fill((0,0,0,51))
		for x in xrange(1,6):
			self.screen.blit(background, (0,0))
			pygame.display.update()
		return
		
	@staticmethod
	def fade_in(self):
		backup = pygame.Surface.copy(self.screen).convert()
		self.screen.fill((0,0,0))
		backup.set_alpha(80)
		for x in xrange(1,6):
			self.screen.blit(backup, (0,0))
			pygame.display.update()
		backup.set_alpha(255)
		self.screen.blit(backup, (0,0))
		pygame.display.update()
		return
		
	@staticmethod
	def fade_into(self, prev_screen):
		backup = pygame.Surface.copy(self.screen).convert()
		self.screen.blit(prev_screen, (0,0))
		backup.set_alpha(80)
		for x in xrange(1,6):
			self.screen.blit(backup, (0,0))
			pygame.display.update()
		backup.set_alpha(255)
		self.screen.blit(backup, (0,0))
		pygame.display.update()
		return
