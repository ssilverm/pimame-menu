#install levenshtein for string compare - sudo apt-get install python-levenshtein
#Next get pip - [curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py]
#						[python get-pip.py]


import zipfile, zlib, os, re, sys, sqlite3, glob, unicodedata, argparse
from Levenshtein import setratio
from os import listdir
from os.path import isfile, join
from select import select



parser = argparse.ArgumentParser(description='PiScraper')
parser.add_argument("--platform", default=None, metavar="value", help="Which platform to scrape", type=str)
parser.add_argument("--crc", default=True, metavar="value", help="use crc to find name", type=bool)
parser.add_argument("--match_rate", metavar="value", default=.85, help="Name Comparison match rate.    (0.58 = default match, 1.0 = names must match exactly, 0.0 = throw caution to the wind.)", type=float)
parser.add_argument("--verbose", metavar="value", default=True, help="Display Prompts (False= nothing, True=show progress, SEMI=Prompt on close matches, Full=Prompt+display every match)")
parser.add_argument("--clean_slate", metavar="value", default=False, help="Re-Scrape all roms (default=False)",type=bool)
parser.add_argument("--dont_match", metavar="value", default=False, help="just add roms to local database, don't try to match them", type=bool)

args = parser.parse_args()

os.system('clear')


class Game(object):

		def __init__(self, id=None, system=None, title=None, search_terms=None, parent=None, cloneof=None, release_date=None, overview=None, esrb=None,
							genres=None, players=None, coop=None, publisher=None, developer=None,
							rating=None, command = None, rom_file=None, rom_path=None, image_file=None, flags=None):
		
			self.id = id
			self.system = system
			self.title = title
			self.search_terms = search_terms
			self.parent = parent
			self.cloneof = cloneof
			self.release_date = release_date
			self.overview = overview
			self.esrb = esrb
			self.genres = genres
			self.players = players
			self.coop = coop
			self.publisher = publisher
			self.developer = developer
			self.rating = rating
			self.command = command
			self.rom_file = rom_file
			self.rom_path = rom_path
			self.image_file = image_file
			self.flags = flags
			
			
			
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
		
class API(object):
	def __init__(self):
		self.OPT_SHOW_CLONES = True
		self.OPT_OVERWRITE_IMAGES = False
		self.DATABASE_PATH = '/home/pi/pimame/pimame-menu/database/'
		self.GAMES = sqlite3.connect(self.DATABASE_PATH + 'games_master.db')
		self.GC = self.GAMES.cursor()
		self.CONFIG = sqlite3.connect(self.DATABASE_PATH + 'config.db')
		self.CC = self.CONFIG.cursor()
		self.LOCAL = sqlite3.connect(self.DATABASE_PATH + 'local.db')
		self.LC = self.LOCAL.cursor()
		
		#self.LC.execute('''PRAGMA journal_mode = OFF''')
		self.LC.execute('CREATE TABLE IF NOT EXISTS local_roms'  + 
		' (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, system INTEGER, title TEXT, search_terms TEXT, parent TEXT, cloneof TEXT, release_date TEXT, overview TEXT, esrb TEXT, genres TEXT,' +
		' players TEXT, coop TEXT, publisher TEXT, developer TEXT, rating REAL, command TEXT, rom_file TEXT, rom_path TEXT, image_file TEXT, number_of_runs INTEGER, flags TEXT)')
		self.LOCAL.commit()

		
	def raw_input_with_timeout(self, prompt, timeout=5.0, response = {'y': True, 'ye': True, 'yes': True, 't': True, 'n': False, 'no': False, 'f': False}):
		
		answer = ''
		sys.stdout.flush()
		os.system('setterm -cursor off')
		while (not answer in response) and timeout >= 0:
			sys.stdout.write('\r[%ds] %s ' % (timeout, prompt)),
			sys.stdout.flush()
			rlist, _, _ = select([sys.stdin], [], [], 1)
			if rlist:
				answer = sys.stdin.readline().replace('\n','').lower()
			timeout -= 1

		os.system('setterm -cursor on')
		if not answer in response: print 'Y'
		print '\r' + ('  ' * 30) + '\r',
		answer = True if not answer in response else response[answer]
		return answer
	
	
	def strip_accents(self, s):
		try:	s = unicode(s, 'utf-8')
		except: pass
		
		try:
			return ''.join(unicodedata.normalize('NFKD', i).encode('ascii', 'ignore') for i in s)
		except:
			return s

			
	def convertToLetters(self, s):
		return str("".join(i for i in s if ( (65 <= ord(i) <= 122) or (48 <= ord(i) <= 57)) ))
	
	
	def convert_roman_numerals(self, match):
		Rn = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000,
				'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
		#get values in reverse order
		values = [Rn[x] for x in match.group()[::-1]]
		answer = values[0]
		
		if len(values) <= 1: return str(answer)
		for index, x in enumerate(values[1:]):
			if x >= values[index]:
				answer += x
			else:
				answer -=x

		return str(answer)
		
		
	def normalize(self, s):
		s = self.strip_accents(s)
		s = s.replace('&', 'and').replace('+', 'and')
		
		#case insensitive - remove 'THE, OF, A, IN, ON, FOR' and all character excluding 'a-z', 'space' & '0-9'
		s = ' '.join(re.sub(r"(?i)(\b(THE|OF|A|IN|ON|FOR)\b)|([^A-Z 0-9])",'',s).split()).lower()
		
		roman_numerals = re.compile(r'(?i)(?<=.\b)(\b(?=[MDCLXVI]+\b)M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V|VI|V?I{2,3})\b)|(\b[I]+\b)$')
		return roman_numerals.sub(self.convert_roman_numerals, s)
		
		rom_locations = []
		config_query = self.load_yaml('/home/pi/pimame/pimame-menu/config.yaml')
		
		if 'scraper_options' in config_query:
			if 'show_clones' in config_query['scraper_options']: self.OPT_SHOW_CLONES = config_query['scraper_options']['show_clones']
			if 'overwrite_images' in config_query['scraper_options']: self.OPT_OVERWRITE_IMAGES = config_query['scraper_options']['overwrite_images']
		
		#assign append to keep rom_locations from being evaluated each iteration
		append = rom_locations.append
		for data_block in config_query['menu_items']:
			if 'roms' in data_block:
				if 'images' in data_block: image_path = data_block['images']
				else: image_path = join(data_block['roms'] ,"images/")
				if search_platform == 'all':
					append({'rom_path': data_block['roms'], 'image_path': image_path, 'platform':data_block['label']})
				elif search_platform.lower() == data_block['label'].lower():
					append({'rom_path': data_block['roms'], 'image_path': image_path, 'platform':data_block['label']})
		return rom_locations
		
		
	def get_stored_roms(self, path):
		#Return only files in directory, need to add whitelist of potential rom extensions (.nes, .bin, .zip)	
		try:
			fname = [ f for f in listdir(path) if isfile(join(path,f)) and f != '.gitkeep' ]
			return sorted(fname)
		except:
			return []
	
	
	def get_platform(self, menu_item_id=None, return_all_menu_items = False):
		
		query = 'SELECT id, label, command, rom_path, include_full_path, include_extension, scraper_id FROM menu_items WHERE %s' % (('id=' + str(menu_item_id)) if menu_item_id else '1=1')
		keys = ['id', 'label', 'command', 'rom_path', 'include_full_path', 'include_extension', 'scraper_id']

		values = self.CC.execute(query).fetchall()
		platforms = [dict(zip(keys, value)) for value in values]
		
		if not return_all_menu_items:
			platforms = [item for item in platforms if item['scraper_id']]
		
		for index, platform in enumerate(platforms):
			query = 'SELECT table_name FROM system_id WHERE id in (%s)' % (platform['scraper_id'] if platform['scraper_id'] else '')
			platforms[index]['table_name'] = [item[0] for item in self.GC.execute(query).fetchall()]
		
		return platforms
	
	
	def get_name(self, system_id, get_rom_name_with_crc=True, table='console'):
		
		while True:
			#wait for file
			file = yield 'ready'
			if get_rom_name_with_crc:
				
				if table == 'console':
					#get crc
					try:
						zip_file = zipfile.ZipFile(file, "r")
						for info in zip_file.infolist():
							crc = "%08X" % info.CRC
							if crc != "00000000" and crc != None:  
								break
							else: crc = None
					except:
						try:
							crc = "%08X"%(zlib.crc32(open(file,"rb").read()) & 0xFFFFFFFF)
						except:
							crc = None
							
					#generate query
					if crc:
						query = 'SELECT name FROM crc_console WHERE crc="' + crc.upper() + '" AND system in (?)'
						name = self.GC.execute(query,(system_id,)).fetchone()
					else:
						name = None
				elif table == 'arcade':
					query = 'SELECT name FROM crc_arcade WHERE system = {0} and rom = "{1}"'.format(system_id, os.path.splitext(file))
					name = self.GC.execute(query).fetchone()
					yield name[0]
					
				#if name found, return name
				if name:
					yield self.normalize(name[0])
				else:
					yield self.normalize(re.sub(r'( *)\([^)]*\)|( *)\[[^]]*\]', '', os.path.splitext(os.path.split(file)[-1])[0]).strip())
			else:
				yield self.normalize(re.sub(r'( *)\([^)]*\)|( *)\[[^]]*\]', '', os.path.splitext(os.path.split(file)[-1])[0]).strip())
		
		
	def match_rom_to_db(self, menu_item_id = None, get_rom_name_with_crc = True, default_match_rate = .85, VERBOSE = True, RUN_WHOLE_SYSTEM_FOLDER = False, dont_match = False):
		
		#Levenshtein check to get the alias for the platform to call API
		#if menu_item_id = None, return all platforms
		platforms = self.get_platform(menu_item_id)

		for platform in platforms:
			if platform['scraper_id']:
				if dont_match == False:
					platform['scrape_me'] = self.raw_input_with_timeout('Scrape roms for %s?' % pcolor('cyan', platform['label']))
				else:
					platform['scrape_me'] = True
		
		for platform in platforms:
			if platform['scraper_id'] and platform['scrape_me']:
					#platform['scraper_id'] = tuple([int(id) for id in platform['scraper_id'].split(',')])

					#check if arcade or console
					if platform['table_name']:
						if 'arcade' in platform['table_name']: self.arcade_match(platform, default_match_rate, VERBOSE, RUN_WHOLE_SYSTEM_FOLDER, dont_match)
						if 'console' in platform['table_name']: self.console_match(platform, get_rom_name_with_crc, default_match_rate, VERBOSE, RUN_WHOLE_SYSTEM_FOLDER, dont_match)
	
	
	def console_match(self, platform, get_rom_name_with_crc, default_match_rate, VERBOSE, RUN_WHOLE_SYSTEM_FOLDER, dont_match):
	
		column_names = [item[1] for item in self.GC.execute('PRAGMA table_info(console)').fetchall()]
						
		#prepare to get_name for non-arcade
		find_name = self.get_name(platform['scraper_id'], get_rom_name_with_crc)
		find_name.send(None)
			
		#load rom filenames, initialize rom_list to return matches
		print 'Fetching %s rom list...' % pcolor('cyan', platform['label'])
		roms = self.get_stored_roms(platform['rom_path'])
		
		#Create Temp table with only currently 
		print 'Connecting to PiPlay Database...'
		self.GC.execute('DROP TABLE IF EXISTS temp_system')
		self.GC.execute('CREATE TEMP TABLE temp_system AS SELECT * FROM console WHERE 0')
		query = 'INSERT INTO temp_system  SELECT * FROM console WHERE system in (%s)' % platform['scraper_id'] 
		self.GC.execute(query)
		self.GAMES.commit()
		
		if RUN_WHOLE_SYSTEM_FOLDER:
			#delete all entries for system
			query = 'DELETE FROM local_roms WHERE system = {platform_id}'.format(platform_id = platform['id'])
			self.LC.execute(query)
		else:
			if dont_match == False:
				#delete all entries that no longer have roms + previously unmatched entries
				query_roms = tuple([x.encode('UTF8') for x in roms]) if len(roms) != 1 else ("('" + roms[0].encode('UTF8') + "')")
				query = 'DELETE FROM local_roms WHERE system = {0} and (rom_file not in {1} or flags like "%no_match%")'.format( platform['id'], query_roms )
				self.LC.execute(query)
			
			#remove any remaining entries from list of roms
			query = 'SELECT rom_file FROM local_roms WHERE system = {platform_id}'.format( platform_id = platform['id'])
			roms = list( set(roms) - set(item[0] for item in self.LC.execute(query).fetchall()) )
			
		self.LOCAL.commit()

		if roms:
			#assign append to keep rom_list from being evaluated each iteration
			rom_list = []
			rom_list_append = rom_list.append
			
			for index, rom in enumerate(roms):
				
				#get rom name
				current_file_search_terms = find_name.send(os.path.join(platform['rom_path'], rom))
				find_name.send('get_ready')
				
				#create run command
				if platform['include_extension']: 
					build_command = rom
				else:
					build_command = os.path.splitext(rom)[0]
				
				if platform['include_full_path']:
					build_command = os.path.join(platform['rom_path'], build_command)
				
				game_command = platform['command'] + ' "' + build_command + '"'
				
				#update what is already known about current entry
				game_info = Game(title = rom, system = platform['id'], search_terms = current_file_search_terms, command = game_command, rom_path = platform['rom_path'], rom_file = rom)

				#set minimum match ratio
				hi_score = default_match_rate
				best_match_game = None
				
				if dont_match == False:
					#build search query
					#we are grabbing any entry that has at least 1 matching search term
					search_query = '%" OR search_terms LIKE "%'.join(unicode(current_file_search_terms).split())
					for entry in self.GC.execute('SELECT id, search_terms, title, system FROM temp_system WHERE (search_terms LIKE "%' + search_query + '%")').fetchall():
						
						Lratio = setratio( unicode(current_file_search_terms).split(), entry[1].split() )
						if Lratio > hi_score:
						
							#check if check to make sure sequels don't get matched to originals
							if [x for x in current_file_search_terms if x.isdigit()] == [y for y in entry[1] if y.isdigit()]:
								hi_score = Lratio
								best_match_game = entry
					
					#if no satisfactory match found, do second pass comparing each letter separately
					if not best_match_game:
						for entry in self.GC.execute('SELECT id, search_terms, title, system FROM temp_system WHERE (search_terms LIKE "%' + search_query + '%")').fetchall():
						
							Lratio = setratio( map(unicode,current_file_search_terms), map(unicode, entry[1]) )
							if Lratio > hi_score:
							
								#check if check to make sure sequels don't get matched to originals
								if [x for x in current_file_search_terms if x.isdigit()] == [y for y in entry[1] if y.isdigit()]:
									hi_score = Lratio
									best_match_game = entry
								
								
					#in verbose mode: ask if game matches
					if (VERBOSE == "SEMI" or VERBOSE == "FULL") and hi_score < .94 and best_match_game:
						best_match_game = best_match_game if self.raw_input_with_timeout('Does %s match %s - %s' % (pcolor('cyan', "["+ rom +"]"), 
																																								pcolor('cyan', "["+ best_match_game[2] +"]"),
																																								pcolor('yellow', "["+"{0:.0f}%".format(float(hi_score) * 100)+"]")), timeout = 10.0) else None
					if VERBOSE == "FULL":
						if best_match_game:
							print 'Closest match for %s is %s - %s' % (pcolor('green', "["+ rom +"]"), pcolor('green', "["+ best_match_game[2] +"]"), pcolor('yellow', "["+"{0:.0f}%".format(float(hi_score) * 100)+"]"))
						else:
							print 'No match found for %s' % (pcolor('red', "[" + rom + "]"))
							
				#Let user know current progress
				if VERBOSE:
					status = r"%10d/%d roms  [%3.2f%%]" % (index+1, len(roms), (index+1) * 100. / len(roms))
					status = status + chr(8)*(len(status)+1)
					sys.stdout.write('%s      \r' % (status))
					sys.stdout.flush()
				
				
				#If a suitable match was found, pull info
				if best_match_game:
					temp_game_info = dict(zip(column_names, self.GC.execute('SELECT * from temp_system where id=?', (best_match_game[0],)).fetchone()))
					
					game_info.title = temp_game_info['title']
					game_info.search_terms = temp_game_info['search_terms']
					game_info.release_date = temp_game_info['release_date']
					game_info.overview = temp_game_info['overview']
					game_info.esrb = temp_game_info['esrb']
					game_info.genres = temp_game_info['genres']
					game_info.players = temp_game_info['players']
					game_info.coop = temp_game_info['coop']
					game_info.publisher = temp_game_info['publisher']
					game_info.developer = temp_game_info['developer']
					game_info.rating = temp_game_info['rating']
				else:
					game_info.flags = 'no_match,'
				
				#if name contains brackets [] with a minus '-' inside, glob will error out
				if dont_match == False:
					try:
						#prefer (user added) image, named same as rom + any extension
						temp_image_path = glob.glob( os.path.join( os.path.join(platform['rom_path'], 'images/'), os.path.splitext(rom)[0] ) + '.*')
						game_info.image_file = temp_image_path[0]
					except:
						try:
							#if no rom named image, then find title named image
							if not game_info.image_file:
							
								image_search = self.GC.execute('SELECT image_file FROM image_match WHERE system=? and id=?', (best_match_game[0], best_match_game[3])).fetchone()[0]
								if image_search: image_search =  [os.path.join(platform['rom_path'], 'images/') + image_search + '.*',
																				os.path.join( os.path.join(platform['rom_path'], 'images/'), self.strip_accents(temp_game_info['title']) + '.*')]
								for image in image_search:
									temp_image_path.extend( glob.glob( image ) )
								game_info.image_file = temp_image_path[0]
						except:
							#if no image found, default to rom name with '.jpg' extension, in case user adds image later.
							game_info.image_file = os.path.join( os.path.join(platform['rom_path'], 'images/'), os.path.splitext(rom)[0] ) + '.jpg'
				else:
					game_info.image_file = os.path.join( os.path.join(platform['rom_path'], 'images/'), os.path.splitext(rom)[0] ) + '.jpg'
				
				
				rom_list_append((game_info.id, game_info.system,
										game_info.title, game_info.search_terms,
										None, None, #parent, cloneof -> for arcade
										game_info.release_date, game_info.overview,
										game_info.esrb, game_info.genres,
										game_info.players, game_info.coop,
										game_info.publisher, game_info.developer,
										game_info.rating, game_info.command,
										game_info.rom_file, game_info.rom_path,
										game_info.image_file, 0, game_info.flags))
			
			self.LC.executemany('INSERT INTO local_roms '  + 
				'(id, system, title, search_terms, parent, cloneof, release_date, overview, esrb, genres, ' +
				'players, coop, publisher, developer, rating, command, rom_file, rom_path, image_file, number_of_runs, flags) ' +
				'VALUES (' + ('?,' * 21)[:-1] + ')', rom_list)
			self.LOCAL.commit()
			print	
	
	
	def image_match(self, id, image_path, default_match_rate=.79, VERBOSE='SEMI'):
	
		#assign append to keep rom_list from being evaluated each iteration
		rom_list = []
		missing_list = []
		
		rom_list_append = rom_list.append
		missing_append = missing_list.append
		
		roms = [os.path.split(os.path.splitext(item)[0])[-1] for item in glob.glob( image_path + '*.*')]
		
		print
		print id, image_path
		print
		
		for index, rom in enumerate(roms):
	
			#set minimum match ratio
			hi_score = default_match_rate
			best_match_game = None
			
			#build search query
			#we are grabbing any entry that has at least 1 matching search term
			current_file_search_terms = unicode(self.normalize(rom))
			search_query = '%" OR search_terms LIKE "%'.join(current_file_search_terms.split())
			for entry in self.GC.execute('SELECT id, search_terms, title FROM image_match WHERE system=' + str(id) + ' AND (search_terms LIKE "%' + search_query + '%")').fetchall():
				
				Lratio = setratio( unicode(current_file_search_terms).split(), entry[1].split() )
				if Lratio > hi_score:
				
					#check if check to make sure sequels don't get mat5hed to originals
					if [x for x in current_file_search_terms if x.isdigit()] == [y for y in entry[1] if y.isdigit()]:
						hi_score = Lratio
						best_match_game = entry
			
			#Let user know current progress
			if VERBOSE:
				status = r"%10d/%d roms  [%3.2f%%]" % (index+1, len(roms), (index+1) * 100. / len(roms))
				status = status + chr(8)*(len(status)+1)
				sys.stdout.write('%s      \r' % (status))
				sys.stdout.flush()
			
			#in verbose mode: ask if game matches
			if (VERBOSE == "SEMI" or VERBOSE == "FULL") and hi_score < .94 and best_match_game:
				best_match_game = best_match_game if self.raw_input_with_timeout('Does %s match %s - %s' % (pcolor('cyan', "["+ rom +"]"), 
																																						pcolor('cyan', "["+ best_match_game[2] +"]"),
																																						pcolor('yellow', "["+"{0:.0f}%".format(float(hi_score) * 100)+"]")), timeout = 10.0) else None
			if VERBOSE == 'FULL':
				try:
					if best_match_game:
						print 'Closest match for %s is %s - %s' % (pcolor('green', "["+ rom +"]"), pcolor('green', "["+ best_match_game[2] +"]"), pcolor('yellow', "["+"{0:.0f}%".format(float(hi_score) * 100)+"]"))
					else:
						print 'No match found for %s' % (pcolor('red', "[" + rom + "]"))
				except:
					pass
			
			
			#If a suitable match was found, pull info
			if best_match_game:
				rom_list_append(( rom, best_match_game[0] ))
			else:
				missing_append(( id, rom ))


		
		self.GC.executemany('UPDATE image_match SET image_file=? WHERE id=?', rom_list)
		self.GC.executemany('INSERT INTO missing_entries (system, title) VALUES (?, ?)', missing_list)
		self.GAMES.commit()
		print


	def arcade_match(self, platform, default_match_rate, VERBOSE, RUN_WHOLE_SYSTEM_FOLDER, dont_match):
						
		column_names = [item[1] for item in self.GC.execute('PRAGMA table_info(arcade)').fetchall()]
			
		#load rom filenames, initialize rom_list to return matches
		print 'Fetching %s rom list...' % pcolor('cyan', platform['label'])
		roms = self.get_stored_roms(platform['rom_path'])
		
		if roms:
			#Create Temp table with only currently 
			print 'Connecting to PiPlay Database...'

			if RUN_WHOLE_SYSTEM_FOLDER:
				#delete all entries for system
				query = 'DELETE FROM local_roms WHERE system = {platform_id}'.format(platform_id = platform['id'])
				self.LC.execute(query)
			else:
				#delete all entries that no longer have roms + previously unmatched entries
				query_roms = tuple([x.encode('UTF8') for x in roms]) if len(roms) != 1 else ("('" + roms[0].encode('UTF8') + "')")
				query = 'DELETE FROM local_roms WHERE system ={0} and (rom_file not in {1} or flags like "%no_match%")'.format( platform['id'], query_roms )
				self.LC.execute(query)
				
				#remove any remaining entries from list of roms
				query = 'SELECT rom_file FROM local_roms WHERE system = {platform_id}'.format( platform_id = platform['id'])
				roms = list( set(roms) - set(item[0] for item in self.LC.execute(query).fetchall()) )
				
			self.LOCAL.commit()
			
			if roms:
				select_roms = tuple(os.path.splitext(rom)[0].encode('UTF8') for rom in roms) if len(roms)>1 else ('("' + roms[0] + '")')
				rom_dict = dict(zip(select_roms, roms))

				#assign append to keep rom_list from being evaluated each iteration
				rom_list = []
				rom_list_append = rom_list.append
				index = 0
				
				query = 'SELECT * FROM arcade WHERE id in {0}'.format(select_roms)
				for value in self.GC.execute(query).fetchall():
					index += 1
					temp_game_info = dict(zip(column_names, value))
				
					rom = rom_dict[temp_game_info['id']]
					
					del rom_dict[temp_game_info['id']]
					
					if dont_match == False:
						#create run command
						if platform['include_extension']: 
							build_command = rom
						else:
							build_command = os.path.splitext(rom)[0]
						
						if platform['include_full_path']:
							build_command = os.path.join(platform['rom_path'], build_command)
						
						game_command = platform['command'] + ' "' + build_command + '"'
						
						
						#Let user know current progress
						if VERBOSE:
							status = r"%10d/%d roms  [%3.2f%%]" % (index, len(roms), (index) * 100. / len(roms))
							status = status + chr(8)*(len(status)+1)
							sys.stdout.write('%s      \r' % (status))
							sys.stdout.flush()
							
						
						if VERBOSE == 'SEMI' or VERBOSE == 'FULL':
							if best_match_game:
								print 'Closest match for %s is %s' % (pcolor('green', "["+ rom +"]"), pcolor('green', "["+ temp_game_info['title'] +"]"))
						
						
						#If a suitable match was found, pull info
						if temp_game_info:
							game_info= Game(title = temp_game_info['title'],
													system = platform['id'],
													parent = temp_game_info['parent'],
													search_terms = temp_game_info['search_terms'],
													release_date = temp_game_info['release_date'],
													overview = temp_game_info['overview'],
													esrb = temp_game_info['esrb'],
													genres = temp_game_info['genres'],
													players = temp_game_info['players'],
													coop = temp_game_info['coop'],
													publisher = temp_game_info['publisher'],
													developer = temp_game_info['developer'],
													rating = temp_game_info['rating'],
													command = game_command,
													rom_path = platform['rom_path'],
													rom_file = rom)
						
						#if name contains brackets [] with a minus '-' inside, glob will error out
						try:
							#named same as rom + any extension
							game_info.image_file = glob.glob( os.path.join( os.path.join(platform['rom_path'], 'images/'), os.path.splitext(rom)[0] ) + '.*')[0]
						except:
							game_info.image_file = os.path.join( os.path.join(platform['rom_path'], 'images/'), os.path.splitext(rom)[0] ) + '.jpg'
						
						rom_list_append((game_info.id, game_info.system,
												game_info.title, game_info.search_terms,
												game_info.parent, game_info.cloneof, #parent, cloneof -> for arcade items
												game_info.release_date, game_info.overview,
												game_info.esrb, game_info.genres,
												game_info.players, game_info.coop,
												game_info.publisher, game_info.developer,
												game_info.rating, game_info.command,
												game_info.rom_file, game_info.rom_path,
												game_info.image_file, 0, game_info.flags))
				
				#roms not found in database
				for key, value in rom_dict.iteritems():
					index += 1
					if VERBOSE == 'SEMI' or VERBOSE == 'FULL':
						print 'No match found for %s' % (pcolor('red', "[" + value + "]"))

					#Let user know current progress
					if not VERBOSE:
						status = r"%10d/%d roms  [%3.2f%%]" % (index, len(roms), (index) * 100. / len(roms))
						status = status + chr(8)*(len(status)+1)
						sys.stdout.write('%s      \r' % (status))
						sys.stdout.flush()
						
					#create run command
					if platform['include_extension']: 
						build_command = value
					else:
						build_command = os.path.splitext(value)[0]
					
					if platform['include_full_path']:
						build_command = os.path.join(platform['rom_path'], build_command)
					
					game_command = platform['command'] + ' "' + build_command + '"'
					
					try:
						#named same as rom + any extension
						image_file = glob.glob( os.path.join( os.path.join(platform['rom_path'], 'images/'), os.path.splitext(rom)[0] ) + '.*')[0]
					except:
						image_file = os.path.join( os.path.join(platform['rom_path'], 'images/'), os.path.splitext(rom)[0] ) + '.jpg'
					
					rom_list_append((None, platform['id'], 			#id, system
											value, key,							#title, search_terms
											None, None,							#parent file
											None, None, 						#release_date, overview
											None, None, 						#esrb, genres
											None, None,						# players, coop
											None, None, 						#publisher, developer
											None, game_command, 		#rating, command
											value, platform['rom_path'], 	#rom_file, rom_path
											image_file, 0, 'no_match,')) 		#image_file, flags
				
			
				self.LC.executemany('INSERT INTO local_roms '  + 
					'(id, system, title, search_terms, parent, cloneof, release_date, overview, esrb, genres, ' +
					'players, coop, publisher, developer, rating, command, rom_file, rom_path, image_file, flags) ' +
					'VALUES (' + ('?,' * 21)[:-1] + ')', rom_list)
				self.LOCAL.commit()
				print
	
api = API()

api.match_rom_to_db(menu_item_id = args.platform, get_rom_name_with_crc = args.crc, default_match_rate = args.match_rate, VERBOSE = args.verbose, RUN_WHOLE_SYSTEM_FOLDER = args.clean_slate, dont_match = args.dont_match)




