
import scraper_api
from scraper_api import pcolor
import urllib
import os, sys, argparse, time
from os.path import isfile, join
from select import select


parser = argparse.ArgumentParser(description='PiScraper')
parser.add_argument("--platform", metavar="value", help="Which platform to scrape", type=str)
parser.add_argument("--local_images", metavar="value", help="Use local images.", type=str)
parser.add_argument("--match_ratio", metavar="value", help="Name Comparison match rate.    (0.6 = default/loose match, 1.0 = names must match exactly, 0.0 = throw caution to the wind.)", type=float)
args = parser.parse_args()



os.system('clear')

class GeneralRun():
	
	def raw_input_with_timeout(self, prompt, timeout=5.0, response = {'y': True, 'ye': True, 'yes': True, 't': True, 'n': False, 'no': False, 'f': False}):
		
		answer = ''
		sys.stdout.flush()
		while (not answer in response) and timeout >= 0:
			sys.stdout.write('\r[%ds] %s' % (timeout, prompt)),
			sys.stdout.flush()
			rlist, _, _ = select([sys.stdin], [], [], 1)
			if rlist:
				answer = sys.stdin.readline().replace('\n','').lower()
			timeout -= 1

		
		if not answer in response: print 'Y'
		print '\r' + ('  ' * 30) + '\r',
		answer = True if not answer in response else response[answer]
		return answer
	
	def __init__(self, platform = 'all', match_ratio = 0.6, local_images = None):
	
		#load gamesdb api
		scraper = scraper_api.Gamesdb_API()

		scrape_list = []
		local_data = None
		if platform == None: platform = 'all'
		
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
			roms_answer = True
			image_answer = True
			
			if not scrape_all_categories:
				roms_answer = self.raw_input_with_timeout('scrape %s roms?: ' % pcolor('cyan', category['platform']))

			if roms_answer and not download_all_category_images and not local_images:
				image_answer = self.raw_input_with_timeout('download %s missing images?: ' %  pcolor('cyan', category['platform']))

			if roms_answer:
				if not local_images:
					rom_data = scraper.match_rom_to_db(category, match_ratio)
				else:
					temp_data = scraper.match_rom_to_local(category, match_ratio)
					local_data = temp_data[0]
					remaining_answer = self.raw_input_with_timeout('Matched %s: Scrape remaining %s roms?: ' % (pcolor('cyan', str(len(local_data))), pcolor('cyan', str(len(temp_data[1])))), 10 )
					if remaining_answer:
						image_answer = self.raw_input_with_timeout('download %s missing images?: ' %  pcolor('cyan', category['platform']))
						rom_data = scraper.match_rom_to_db(category, match_ratio, temp_data[1])
					
				if image_answer:
						scraper.download_image(rom_data, image_type = 'thumb')
				
				if local_data: rom_data = rom_data + local_data
				
				scraper.build_cache_file(rom_data, len(os.listdir(category['rom_path'])) )

				
if not args.match_ratio: args.match_ratio = 0.6
GeneralRun(args.platform, args.match_ratio, args.local_images)
	

	
	


