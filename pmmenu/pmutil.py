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
		system(command + " && python " + sys.argv[0])
		sys.exit()