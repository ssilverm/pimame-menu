import pygame
import subprocess
import re
import sys
import time
from os import system, remove, close
from tempfile import mkstemp
from shutil import move

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
		system(command + " && python " + sys.argv[0])
		sys.exit()
	
	@staticmethod
	def replace(file_path, pattern, subst):
		#Create temp file
		file_number, abs_path = mkstemp()
		new_file = open(abs_path,'w')
		old_file = open(file_path)
		for line in old_file:
			line = line.replace(':"', ': "')
			new_file.write(line.replace(pattern, subst))
		#close temp file
		new_file.close()
		close(file_number)
		old_file.close()
		#Remove original file
		remove(file_path)
		#Move new file
		move(abs_path, file_path)
	
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
	
	@staticmethod
	def blurSurf(surface, amt):
		if amt < 1.0:
			raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s"%amt)
		scale = 1.0/float(amt)
		surf_size = surface.get_size()
		scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
		surf = pygame.transform.smoothscale(surface, scale_size)
		surf = pygame.transform.smoothscale(surf, surf_size)
		return surf
