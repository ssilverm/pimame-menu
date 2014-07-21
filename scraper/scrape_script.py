
import scraper_api
from scraper_api import pcolor
import urllib
import os, sys, argparse, time
from os.path import isfile, join
from select import select


parser = argparse.ArgumentParser(description='PiScraper')
parser.add_argument("--platform", metavar="value", help="Which platform to scrape", type=str)
parser.add_argument("--local_images", metavar="value", help="Use local images. Parent folder must contain child folder with system name", type=str)
args = parser.parse_args()



os.system('clear')

class GeneralRun():
	
	def raw_input_with_timeout(self, prompt, timeout=3.0, response = {'y': True, 'ye': True, 'yes': True, 't': True, 'n': False, 'no': False, 'f': False}):
		
		answer = ''
		while (not answer in response) and timeout >= 0:
			sys.stdout.write('\r[%ds] %s' % (timeout, prompt)),
			sys.stdout.flush()
			rlist, _, _ = select([sys.stdin], [], [], 1)
			if rlist:
				answer = sys.stdin.readline().replace('\n','').lower()
			timeout -= 1
			time.sleep(1)
		
		if not answer in response: print 'Y'
		print '\r' + ('  ' * 30) + '\r',
		answer = True if not answer in response else response[answer]
		return answer
	
	def __init__(self, platform = 'all', local_images = None):
	
		#load gamesdb api
		scraper = scraper_api.Gamesdb_API()

		scrape_list = []
		if platform == None: platform = 'all'
		response = {'y': True, 'ye': True, 'yes': True, 'n': False, 'no': False}
		scrape_all_categories = '' if platform == 'all' else 'no'
		download_all_category_images = '' if platform == 'all' else 'no'
		
		#mame4all uses 0.37b5 -> faster
		#advancemame uses 0.106 -> more roms
		
		scrape_list = scraper.build_rom_list(platform)
		#scrape_list = scraper.build_rom_list('snes')

		
		scrape_all_categories = self.raw_input_with_timeout('scrape %s rom categories?: ' % pcolor('cyan', 'ALL')) if platform == 'all' else False
		
			
		if scrape_all_categories and not local_images:
			download_all_category_images = self.raw_input_with_timeout('download %s missing images?: ' % pcolor('cyan', 'ALL'))
		else:
			download_all_category_images = False


		for category in scrape_list:
			roms_answer = ''
			image_answer = ''
			if not scrape_all_categories:
				roms_answer = self.raw_input_with_timeout('scrape %s roms?: ' % pcolor('cyan', category['platform']))
			else:
				roms_answer = True
			
			if roms_answer and not download_all_category_images and not local_images:
				image_answer = self.raw_input_with_timeout('download %s missing images?: ' %  pcolor('cyan', category['platform']))
			else:
				image_answer = True

			if roms_answer:
				if not local_images:
					rom_data = scraper.match_rom_to_db(category)
				else:
					rom_data = scraper.match_rom_to_local(category, local_images)
				if image_answer:
					if not local_images:
						scraper.download_image(rom_data, image_type = 'thumb')
				scraper.build_cache_file(rom_data, len(os.listdir(category['rom_path'])) )
				
				
				
	
				
if args.local_images:
	GeneralRun(args.platform, args.local_images)
else:
	GeneralRun(args.platform)
	

	
	


