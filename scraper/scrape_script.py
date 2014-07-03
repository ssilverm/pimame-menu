
import scraper_api
from scraper_api import pcolor
import urllib
import os, sys, argparse
from os.path import isfile, join


parser = argparse.ArgumentParser(description='PiScraper')
parser.add_argument("--platform", metavar="value", help="Which platform to scrape", type=str)
args = parser.parse_args()



os.system('clear')

class GeneralRun():
	def __init__(self, platform='all'):
	
		#load gamesdb api
		scraper = scraper_api.Gamesdb_API()

		scrape_list = []
		response = {'y': True, 'ye': True, 'yes': True, 'n': False, 'no': False}
		scrape_all = '' if platform == 'all' else 'no'
		download_all = '' if platform == 'all' else 'no'
		#mame4all uses 0.37b5 -> faster
		#advancemame uses 0.106 -> more roms
		scrape_list = scraper.build_rom_list(platform)
		#scrape_list = scraper.build_rom_list('snes')

		while not scrape_all in response:
			scrape_all = raw_input('scrape %s rom categories?: ' % pcolor('cyan', 'ALL')).lower()
			
		if response[scrape_all]:
			while not download_all in response:
				download_all = raw_input('download %s missing images?: ' % pcolor('cyan', 'ALL')).lower()
		else:
			download_all = 'no'

		for category in scrape_list:
			answer = ''
			image_answer = ''
			if not response[scrape_all]:
				while not answer in response: answer = raw_input('scrape %s roms?: ' % pcolor('cyan', category['platform'])).lower()
			else:
				answer = 'yes'
			
			if response[answer] and not response[download_all]:
				while not image_answer in response: image_answer = raw_input('download %s missing images?: ' %  pcolor('cyan', category['platform'])).lower()
			else:
				image_answer = 'yes'

			if response[answer]:
				rom_data = scraper.match_rom_to_db(category)
				if response[image_answer]:
					scraper.download_image(rom_data, image_type = 'thumb')
				scraper.build_cache_file(rom_data, len(os.listdir(category['rom_path'])) )
				

GeneralRun(args.platform)
	

	
	


