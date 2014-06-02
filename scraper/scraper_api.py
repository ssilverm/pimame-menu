#install levenshtein for string compare - sudo apt-get install python-levenshtein
#Next get pip - [curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py]
#						[python get-pip.py]


import urllib, urllib2, yaml, zipfile, zlib, os, json, re, sys, shutil
import platform
from Levenshtein import ratio
from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as Tree

class Platform(object):

	def __init__(self, id, name, alias=None, console=None, controller=None, overview=None, developer=None,
						manufacturer=None, cpu=None, memory=None, graphics=None, sound=None, display=None,
						media=None, max_controllers=None, rating=None, consoleart=None, controllerart=None):

		self.id = id
		self.name = name
		self.alias = alias
		self.console = console
		self.controller = controller
		self.overview = overview
		self.developer = developer
		self.manufacturer = manufacturer
		self.cpu = cpu
		self.memory = memory
		self.graphics = graphics
		self.sound = sound
		self.display = display
		self.media = media
		self.max_controllers = max_controllers
		self.rating = rating
		self.consoleart = consoleart
		self.controllerart = controllerart
		
class Game(object):

		def __init__(self, id, title, ascii_title, platform=None, release_date=None, overview=None, esrb=None,
							genres=None, players=None, coop=None, youtube=None, publisher=None, developer=None,
							rating=None, clear_logo=None, box_thumb=None, box_art=None):
		
			self.id = id
			self.title = title
			self.ascii_title = ascii_title
			self.platform = platform
			self.release_date = release_date
			self.overview = overview
			self.esrb = esrb
			self.genres = genres
			self.players = players
			self.coop = coop
			self.youtube = youtube
			self.publisher = publisher
			self.developer = developer
			self.rating = rating
			self.clear_logo = clear_logo
			self.box_thumb = box_thumb
			self.box_art = box_art
			
def pcolor(color, string):
	ENDC = '\033[0m'
	colors = {'red': '\033[31m',
	'green': '\033[32m',
	'yellow': '\033[33m',
	'blue': '\033[34m',
	'fuschia': '\033[35m',
	'cyan': '\033[36m'}
	
	return colors[color.lower()] + string + ENDC


class APIException(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg
		
class Gamesdb_API(object):
	def __init__(self):
		self.OPT_SHOW_CLONES = True
		self.OPT_OVERWRITE_IMAGES = False

	def load_yaml(self, file):
		stream = open(file, 'r')
		config_query = yaml.safe_load(stream)
		stream.close()
		return config_query
	
	def removeNonAscii(a,s):
		return str("".join(i for i in s if ord(i)<128))
	
	
	#Piplay specific functions
	#---------------------------
	
	#Get Rom path + image path for each platform from /home/pi/pimame-menu/config.yaml
	def build_rom_list(self, search_platform='all'):
		rom_locations = []
		config_query = self.load_yaml('/home/pi/pimame/pimame-menu/config.yaml')
		
		if 'scraper_options' in config_query:
			if 'show_clones' in config_query['scraper_options']: self.OPT_SHOW_CLONES = config_query['scraper_options']['show_clones']
			if 'overwrite_images' in config_query['scraper_options']: self.OPT_OVERWRITE_IMAGES = config_query['scraper_options']['overwrite_images']

		for data_block in config_query['menu_items']:
			if 'roms' in data_block:
				if 'images' in data_block: image_path = data_block['images']
				else: image_path = data_block['roms'] + "images/"
				if search_platform == 'all':
					rom_locations.append({'rom_path': data_block['roms'], 'image_path': image_path, 'platform':data_block['label']})
				elif search_platform.lower() == data_block['label'].lower():
					rom_locations.append({'rom_path': data_block['roms'], 'image_path': image_path, 'platform':data_block['label']})
		return rom_locations
		
	#Return only files in directory, need to add whitelist of potential rom extensions (.nes, .bin, .zip)	
	def get_stored_roms(self, path):
		try:
			fname = [ f for f in listdir(path) if isfile(join(path,f)) and f != '.gitkeep' ]
			return sorted(fname)
		except:
			return []
	
	#Find the closest match to the specified platform. returns platform dictionary from PLATFORM.PY
	def match_platform(self, test_platform):
		test_platform = test_platform.lower()
		hi_score = 0
		best_match_platform = {}
		for current_platform in platform.full_list:
			Lratio = ratio(test_platform, current_platform['name'].lower())
			if ratio(test_platform, current_platform['shortcode'].lower()) > Lratio: Lratio = ratio(test_platform, current_platform['shortcode'].lower()) 
			if ratio(test_platform, current_platform['alias'].lower()) > Lratio: Lratio = ratio(test_platform, current_platform['alias'].lower())
			if Lratio > hi_score: 
				hi_score = Lratio
				best_match_platform = current_platform
		return best_match_platform
			

	def match_rom_to_db(self, input_data, compare_dat=True, min_match_ratio=.6):
		#Levenshtein check to get the alias for the platform to call API
		dat_list = {}
		real_platform = self.match_platform(input_data['platform'])
		print
		if real_platform['name'].lower() == 'arcade':
			arcade = self.match_mame_to_dat_file(input_data, real_platform['shortcode'].lower() + '.dat')
			return arcade
		else:
			if isfile('/home/pi/pimame/pimame-menu/assets/dat/' + real_platform['shortcode'].lower() + '.dat') and compare_dat:
				print "Found %s..." % (real_platform['shortcode'].lower() + '.dat')
				root = Tree.parse('/home/pi/pimame/pimame-menu/assets/dat/' + real_platform['shortcode'].lower() + '.dat').getroot()
				print 'Converting to dictionary...'
				dat_list = {}
				root_size = len(root)
				for index, game in enumerate(root):
					status = "Conversion: [%3.2f%%]" % (index * 100. / root_size)
					#status = status + chr(8)*(len(status)+1)
					sys.stdout.write('%s      \r' % (status))
					sys.stdout.flush()
					rom_element = {}
					if game.tag == 'game':
						for element in game:
							if element.tag == 'rom':
								#only add unique crc's
								if not 'merge' in element.attrib: 
									if 'crc' in element.attrib: rom_element[element.attrib['crc'].upper()] = element.attrib['crc']
							if element.tag == 'description':
								game_description = element.text
						dat_list[game_description] = rom_element
				dat_exists = True
				root.clear()
			else:
				dat_exists = False
				
		#load rom filenames, initialize rom_list to return matches
		print 'Fetching %s rom list...' % pcolor('cyan', input_data['platform'])
		roms = self.get_stored_roms(input_data['rom_path'])
		
		
		print 'Connecting to thegamesdb.net...'
		game_info = self.PlatformGames(real_platform['name'])
		rom_list = []
		for rom in roms:
			game = None
			if dat_exists:
				try:
					file = zipfile.ZipFile(os.path.join(input_data['rom_path'],rom), "r")
					for info in file.infolist():
						crc = "%08X" % info.CRC
						if crc != "00000000": 
							for key, value in dat_list.iteritems():
								if crc in value:
									game = key
									break
						if game is not None: break
				except: 
						crc = "%08X"%(zlib.crc32(open(os.path.join(input_data['rom_path'],rom),"rb").read()) & 0xFFFFFFFF)
						for key, value in dat_list.iteritems():
							if crc in value:
								game = key
								break
					
			hi_score = min_match_ratio
			best_match_game = -1
			rom_name = re.sub(r'( *)\([^)]*\)|( *)\[[^]]*\]', '', game if game is not None else os.path.splitext(rom)[0]).strip()
			for index, game_entry in enumerate(game_info):
				Lratio = ratio(rom_name, game_entry.ascii_title)
				if Lratio > hi_score:
					hi_score = Lratio
					best_match_game = index
			if best_match_game > -1:
				print 'closest match for %s is %s' % (pcolor('green', rom_name), pcolor('cyan', game_info[best_match_game].title))
				image_file = os.path.splitext(rom)[0] + os.path.splitext(game_info[best_match_game].box_art)[1]
				rom_list.append({
					'rom_path': input_data['rom_path'], 
					'image_path': input_data['image_path'], 
					'image_file': image_file, 
					'file': rom, 
					'real_name': rom_name if game is not None else game_info[best_match_game].title, 
					'art': game_info[best_match_game].box_art, 
					'logo': game_info[best_match_game].clear_logo, 
					'thumb': game_info[best_match_game].box_thumb, 
					'platform': input_data['platform']
					})
			else:
				print "No match found for %s" % pcolor('red', rom_name)
				rom_list.append({
					'rom_path': input_data['rom_path'], 
					'image_path': input_data['image_path'], 
					'image_file': '', 
					'file': rom, 
					'real_name': rom, 
					'art': '', 
					'logo': '', 
					'thumb': '',
					'platform': input_data['platform']
					})
			hi_score = min_match_ratio
			best_match_game = -1
		dat_list.clear()
		return rom_list
		
	def match_mame_to_dat_file(self, input_data, dat_file, CRC_check = False):
		print "show clones: %s" % self.OPT_SHOW_CLONES
		print "Loading %s..." % dat_file
		if dat_file == 'final burn.dat':
			dl_image_path = 'https://raw.githubusercontent.com/mholgatem/pi-scraper/master/images/FBA/'
		else:
			dl_image_path = 'https://raw.githubusercontent.com/mholgatem/pi-scraper/master/images/MAME/'
		
		root = Tree.parse('/home/pi/pimame/pimame-menu/assets/dat/' + dat_file).getroot()
				
		#load rom filenames, initialize rom_list to return matches
		roms = self.get_stored_roms(input_data['rom_path'])
		rom_list = []
		for rom in roms:
			if CRC_check:
				try:
					file = zipfile.ZipFile(os.path.join(input_data['rom_path'],rom), "r")
				except: continue
				crc_list = {}
				for info in file.infolist():
					crc = "%08x" % info.CRC
					crc_list[crc] = crc
			
			#find rom entry in dat file
			game = root.find("./game/[@name='" + os.path.splitext(rom)[0] + "']")
			missing_file = False
			if game is not None:
				if not self.OPT_SHOW_CLONES and 'cloneof' in game.attrib:
					missing_file = True
				else:
					if self.OPT_SHOW_CLONES or not 'cloneof' in game.attrib:
						for element in game:
							if element.tag == 'description':
								title = element.text
							if element.tag == 'rom' and CRC_check:
								if not 'merge' in element.attrib:
									if not element.attrib['crc'] in crc_list:
										missing_file = True
										print ("%12s - %s") % (rom, pcolor('red', rom + " -crc for file: " + element.attrib['name'] + " doesn't match"))
					
						
				if not missing_file:
						print ("%12s - %s")  % (rom, pcolor('green', 'Verified'))
						image_file = os.path.splitext(rom)[0] + '.png' if isfile(join(input_data['image_path'], os.path.splitext(rom)[0] + '.png')) else ''
						
						rom_list.append({
							'rom_path': input_data['rom_path'], 
							'image_path': input_data['image_path'], 
							'image_file': os.path.splitext(rom)[0] + '.png', 
							'file': rom, 
							'real_name': title,
							'art': dl_image_path + os.path.splitext(rom)[0] + '.png',
							'logo': dl_image_path + os.path.splitext(rom)[0] + '.png',
							'thumb': dl_image_path + os.path.splitext(rom)[0] + '.png',
							'platform': input_data['platform']
						})
		return rom_list
	
	#function not used, match images from image_path with same name as games in dat file then copy them to output folder
	def match_images_to_dat(self, image_path, dat_file, output_path = 'match to dat/', file_ext = '.png'):
		if not os.path.exists(join(image_path, output_path)): os.makedirs(join(image_path, output_path))
		
		print "Loading %s..." % dat_file
		root = Tree.parse('/home/pi/pimame/pimame-menu/assets/dat/' + dat_file).getroot()
		
		for game in root:
			if game.tag == 'game':
				game_name = (game.attrib['cloneof'] if 'cloneof' in game.attrib else game.attrib['name']) + file_ext
				src = join(image_path, game_name)
				dst = join(image_path, output_path)
				if isfile(src):
					shutil.copy(src, dst)
					print src
	
	def build_cache_file(self, rom_list):
		if not rom_list: 
			print 'No roms found...'
			return
		if not os.path.exists('/home/pi/pimame/pimame-menu/.cache/'): os.makedirs('/home/pi/pimame/pimame-menu/.cache/')
		with open('/home/pi/pimame/pimame-menu/.cache/' + rom_list[0]['platform'].lower() + '.cache' , 'w') as outfile:
			print '-----------------------------'
			cache_list = []
			list_size = len(rom_list)
			for index, rom in enumerate(rom_list):
				status = 'Writing cache file:' + r"[%3.2f%%]" % ((index+1) * 100. / list_size)
				status = status + chr(8)*(len(status)+1)
				print status,
				data = {'rom_path': rom['rom_path'], 'file': rom['file'], 'image_path': rom['image_path'], 'image_file': rom['image_file'], 'real_name': rom['real_name']}
				cache_list.append(data)
			json.dump(cache_list, outfile)
			outfile.close()
			print
			print
		romlist = None
	
		
	#Download images - image type can be art, logo, or thumb
	def download_image(self, rom_data, image_type = 'art'):
		
		if not rom_data: 
			return
			
		size = len(rom_data)
		print "Checking images for %s roms." % str(size)
		
		if not os.path.exists(rom_data[0]['image_path']): os.makedirs(rom_data[0]['image_path'])
		
		for index, rom in enumerate(rom_data):

			if rom['image_file'] != '':
			
				if image_type == 'logo': rom['image_file'] = os.path.splitext(rom['image_file'])[0] + '.png'
				
				if not isfile(join(rom['image_path'],rom['image_file'])) or self.OPT_OVERWRITE_IMAGES:
					api_url = urllib2.Request(rom[image_type], headers={'User-Agent' : "Pi-Scraper"})
					try:
						response = urllib2.urlopen(api_url)
						meta = response.info()
						
						#if not boxart - get meta response
						if not 'image' in meta.getheaders("Content-Type")[0] and image_type != 'art':
							api_url = urllib2.Request(rom['art'], headers={'User-Agent' : "Pi-Scraper"})
							response = urllib2.urlopen(api_url)
							meta = response.info()
						
						#open local file to write image to
						if 'image' in meta.getheaders("Content-Type")[0]:
							f = open(rom['image_path'] + rom['image_file'], 'wb')
							file_size = int(meta.getheaders("Content-Length")[0])
							print "Downloading: %s [%dkb]" % (pcolor('green',rom['image_file']), file_size/1000)

							file_size_dl = 0
							block_sz = 1024
							while True:
								buffer = response.read(block_sz)
								if not buffer:
									break

								file_size_dl += len(buffer)
								f.write(buffer)
								status = r"%10dkb/%dkb  [%3.2f%%]" % (file_size_dl/1000, file_size/1000, file_size_dl * 100. / file_size)
								status = status + chr(8)*(len(status)+1)
								sys.stdout.write('%s      \r' % (status))
								sys.stdout.flush()

							f.close()
						else:
							print "No image file found for: %s" % pcolor('red',rom['real_name'])
					except urllib2.HTTPError, e:
						print "No image file found for: %s" % pcolor('red',rom['real_name'])
				else:
					print "File already exists: %s" % pcolor('cyan',rom['image_file'])
		
	

	#GamesDB specific functions
	#--------------------------------
	
	@staticmethod
	def api_call(api_url, query_args=None):
		if query_args is not None:
			api_url = urllib2.Request(api_url, urllib.urlencode(query_args), headers={'User-Agent' : "Pi-Scraper"})
			response = urllib2.urlopen(api_url)
		else:
			api_url = urllib2.Request(api_url, headers={'User-Agent' : "Pi-Scraper"})
			response = urllib2.urlopen(api_url)
		page = response.read()
				
		# check for XML parser Error
		try:
			xml_code = Tree.fromstring(page)
		except Tree.ParseError:
			raise APIException(page)
		return  xml_code

	def GetPlatformsList(self):
		platforms_list = []
		API_URL = 'http://thegamesdb.net/api/GetPlatformsList.php'
		xml_code = self.api_call(API_URL)
		for element in xml_code.iter(tag="Platform"):
			for subelement in element:
				if subelement.tag == 'id':
					platform_id = subelement.text
				if subelement.tag == 'name':
					platform_name = subelement.text
				if subelement.tag == 'alias':
					platform_alias = subelement.text
			platforms_list.append(Platform(platform_id, platform_name, alias=platform_alias))

		return platforms_list
		
	def GetPlatform(self, id):
		# TODO Add support for fetching platform images under the <Images> element
		API_URL = 'http://thegamesdb.net/api/GetPlatform.php?'
		query_args = {'id': id}
		xml_code = self.api_call(API_URL, query_args)
		# TODO These are all optional fields.  There's probably a better way to handle this than setting them all to None.
		platform_id = None
		platform_name = None
		platform_console = None
		platform_controller = None
		platform_graphics = None
		platform_max_controllers = None
		platform_rating = None
		platform_display = None
		platform_manufacturer = None
		platform_cpu = None
		platform_memory = None
		platform_sound = None
		platform_media = None
		platform_developer = None
		platform_overview = None
		for element in xml_code.iter(tag="Platform"):
			for subelement in element:
				if subelement.tag == 'id':
					platform_id = subelement.text
				if subelement.tag == 'Platform':
					platform_name = subelement.text
				if subelement.tag == 'console':
					platform_console = subelement.text
				if subelement.tag == 'controller':
					platform_controller = subelement.text
				if subelement.tag == 'overview':
					platform_overview = subelement.text
				if subelement.tag == 'developer':
					platform_developer = subelement.text
				if subelement.tag == 'manufacturer':
					platform_manufacturer = subelement.text
				if subelement.tag == 'cpu':
					platform_cpu = subelement.text
				if subelement.tag == 'memory':
					platform_memory = subelement.text
				if subelement.tag == 'graphics':
					platform_graphics = subelement.text
				if subelement.tag == 'sound':
					platform_sound = subelement.text
				if subelement.tag == 'display':
					platform_display = subelement.text
				if subelement.tag == 'media':
					platform_media = subelement.text
				if subelement.tag == 'max_controllers':
					platform_max_controllers = subelement.text
				if subelement.tag == 'rating':
					platform_rating = subelement.text
		if (platform_id == None or platform_name == None):
			raise APIException("GetPlatform returned a result without required fields id or platform")
		return Platform(platform_id, platform_name, console=platform_console, controller=platform_controller,
						graphics=platform_graphics, max_controllers=platform_max_controllers, rating=platform_rating,
						display=platform_display, manufacturer=platform_manufacturer, cpu=platform_cpu,
						memory=platform_memory, sound=platform_sound, media=platform_media, developer=platform_developer,
						overview=platform_overview)

	def PlatformGames(self, platform_name):
		API_URL = 'http://thegamesdb.net/api/PlatformGames.php?'
		query_args = {'platform': platform_name}
		xml_code = self.api_call(API_URL, query_args)
		platform_games_list = []
		for element in xml_code.iter(tag="Game"):
			platform_games_list_release_date = None
			for subelement in element:
				if subelement.tag == 'id':
					platform_games_list_id = subelement.text
				if subelement.tag == 'GameTitle':
					game_title = subelement.text
					game_ascii_title = self.removeNonAscii(game_title)
				if subelement.tag == 'thumb':
					game_thumb_url = 'http://thegamesdb.net/banners/_gameviewcache/' + subelement.text
					game_art_url = 'http://thegamesdb.net/banners/' + subelement.text
					game_logo_url = 'http://thegamesdb.net/banners/clearlogo/' + platform_games_list_id +'.png'
			platform_games_list.append(Game(platform_games_list_id, game_title, game_ascii_title,
											box_thumb=game_thumb_url, box_art=game_art_url,clear_logo=game_logo_url))
		return platform_games_list

	def GetPlatformGames(self, platform_id):
		API_URL = 'http://thegamesdb.net/api/GetPlatformGames.php?'
		query_args = {'platform': platform_id}
		xml_code = self.api_call(API_URL, query_args)
		platform_games_list = []
		for element in xml_code.iter(tag="Game"):
			platform_games_list_release_date = None
			for subelement in element:
				if subelement.tag == 'id':
					platform_games_list_id = subelement.text
				if subelement.tag == 'GameTitle':
					game_title = subelement.text
					game_ascii_title = self.removeNonAscii(game_title)
				if subelement.tag == 'ReleaseDate':
					# platform_games_list_release_date = datetime.strptime(subelement.text, "%m/%d/%Y")
					# Omitting line above since date comes back in an inconsistent format, for example only %Y
					platform_games_list_release_date = subelement.text
			platform_games_list.append(Game(platform_games_list_id, game_title, game_ascii_title,
											release_date=platform_games_list_release_date))
		return platform_games_list

	def GetGame(self, id=None, name=None, platform=None):
		if id is not None and name is not None:  # Only one of these arguments must be passed
			name=None

		query_args = {}
		if id is not None:
			query_args['id'] = id
		if name is not None:
			query_args['name'] = name
		if platform is not None:
			query_args['platform'] = platform
			
		API_URL = 'http://thegamesdb.net/api/GetGame.php?'
		xml_code = self.api_call(API_URL, query_args)
		games_list = []
		game_base_img_url = None
		
		for element in xml_code.iter(tag="baseImgUrl"):
			game_base_img_url = element.text
		for element in xml_code.iter(tag="Game"):
			game_overview = None
			game_release_date = None
			game_esrb_rating = None
			game_youtube_url = None
			game_rating = None
			game_logo_url = None
			game_players = None
			game_coop = None
			game_genres = None
			game_publisher = None
			game_developer = None
			for subelement in element:
				if subelement.tag == 'id':
					game_id = subelement.text
				if subelement.tag == 'GameTitle':
					game_title = subelement.text
					game_ascii_title = self.removeNonAscii(game_title)
				if subelement.tag == 'Platform':
					game_platform = subelement.text
				if subelement.tag == 'ReleaseDate':
					# games_release_date = datetime.strptime(subelement.text, "%m/%d/%Y")
					game_release_date = subelement.text
				if subelement.tag == 'Overview':
					game_overview = subelement.text
				if subelement.tag == 'ESRB':
					game_esrb_rating = subelement.text
				if subelement.tag == 'Genres':
					game_genres = ''
					for genre_element in subelement.iter(tag="genre"):
						# TODO put elements in a more appropriate data structure
						game_genres += genre_element.text
				if subelement.tag == 'Players':
					game_players = subelement.text
				if subelement.tag == 'Co-op':
					if subelement.text == 'No':
						game_coop = False
					elif subelement.text == 'Yes':
						game_coop = True
				if subelement.tag == 'Youtube':
					game_youtube_url = subelement.text
				if subelement.tag == 'Publisher':
					game_publisher = subelement.text
				if subelement.tag == 'Developer':
					game_developer = subelement.text
				if subelement.tag == 'Rating':
					game_rating = subelement.text
				if subelement.tag == 'clearlogo':
					# TODO Capture image dimensions from API resposne
					game_logo_url = game_base_img_url + subelement.text
			games_list.append(Game(game_id, game_title, game_ascii_title, release_date=game_release_date, platform=game_platform,
							   overview=game_overview, esrb_rating=game_esrb_rating, genres=game_genres,
							   players=game_players, coop=game_coop, youtube_url=game_youtube_url,
							   publisher=game_publisher, developer=game_developer, rating=game_rating,
							   clear_logo=game_logo_url))

		if len(games_list) == 0:
			return None
		elif len(games_list) == 1:
			return games_list[0]
		else:
			return games_list

	def GetGamesList(self, name, platform=None, genre=None):
		query_args = {'name': name}
		if platform is not None:
			query_args['platform'] = platform
		if genre is not None:
			query_args['genre'] = genre
		games_list = []
		GET_GAMES_LIST_ENDPOINT = 'http://thegamesdb.net/api/GetGamesList.php?'
		xml_code = self.api_call(GET_GAMES_LIST_ENDPOINT, query_args)
		for element in xml_code.iter(tag="Game"):
			game_release_date = None
			game_platform = None
			for subelement in element:
				if subelement.tag == 'id':
					game_id = subelement.text
				if subelement.tag == 'GameTitle':
					game_title = subelement.text
					game_ascii_title = self.removeNonAscii(game_title)
				if subelement.tag == 'ReleaseDate':
					game_release_date = subelement.text
				if subelement.tag == 'Platform':
					game_platform = subelement.text
			games_list.append(Game(game_id, game_title, game_ascii_title, release_date=game_release_date, platform=game_platform))
		return games_list
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		