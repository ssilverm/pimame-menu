
import scraper_api
import urllib
import os
from os.path import isfile, join

#load gamesdb api
scraper = scraper_api.Gamesdb_API()



scrape_list = []
response = {'y': True, 'ye': True, 'yes': True, 'n': False, 'no': False}
scrape_all = ''
download_all = ''
#mame4all uses 0.37b5 -> faster
#advancemame uses 0.106 -> more roms
scrape_list = scraper.build_rom_list()
#scrape_list = scraper.build_rom_list('snes')

while not scrape_all in response:
	scrape_all = raw_input('scrape \033[94mALL\033[0m rom categories?: ').lower()
	
if response[scrape_all]:
	while not download_all in response:
		download_all = raw_input('download \033[94mALL\033[0m missing images?: ').lower()
else:
	download_all = 'no'

for category in scrape_list:
	answer = ''
	image_answer = ''
	if not response[scrape_all]:
		while not answer in response: answer = raw_input('scrape \033[94m%s\033[0m roms?: ' % category['platform']).lower()
	else:
		answer = 'yes'
	
	if response[answer] and not response[download_all]:
		while not image_answer in response: image_answer = raw_input('download \033[94m%s\033[0m missing images?: ' % category['platform']).lower()
	else:
		image_answer = 'yes'

	if response[answer]:
		rom_data = scraper.match_rom_to_db(category)
		if response[image_answer]:
			scraper.download_image(rom_data, image_type = 'thumb', overwrite_existing = False)
		scraper.build_cache_file(rom_data)
	

	
	


