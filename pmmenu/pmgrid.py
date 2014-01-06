from menuitem import *

class PMGrid(pygame.sprite.OrderedUpdates):
	#menu_items = []
	# menu_items_by_sprite = None
	options = None

	def __init__(self, menu_item_cfgs, opts):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.menu_items = []
		self.options = opts
		self.first_index = self.last_index = 0

		if self.options.sort_items_alphanum:
			print menu_item_cfgs
			menu_item_cfgs.sort(key=lambda x: x['label'])

		for menu_item in menu_item_cfgs:
			#print menu_item
			if menu_item['visible']:
				pm_menu_item = PMMenuItem(menu_item, opts)
				#self.add(pm_menu_item)
				self.menu_items.append(pm_menu_item)

		if self.options.sort_items_with_roms_first:
			self.menu_items.sort(key=lambda x: x.num_roms, reverse=True)

		if self.options.hide_items_without_roms:
			self.menu_items = [x for x in self.menu_items if x.num_roms > 0]



		self.set_num_items_per_page(10)
		self.set_page(0)
		print self.pages
		#for pm_menu_item in self.menu_items:
		#	self.add(pm_menu_item)


  # - label: SNES
  #   visible: Yes
  #   icon_file: snes.jpg
  #   roms: /home/pi/roms/snes/
  #   full_path: yes
  #   command: /home/pi/emulators/pisnes/snes9x #/home/emulators/dgen/dgen %rom



	def create_nav_menu_item(self, label, icon_file):
		item = {}
		item['label'] = label
		item['visible'] = True
		item['icon_file'] = icon_file
		item['command'] = ''
		item['roms'] = ''
		item['full_path'] = True

		menu_item = PMMenuItem(item, self.options)
		menu_item.type = PMMenuItem.NAVIGATION

		return menu_item

	def set_num_items_per_page(self, n):
		self.num_items_per_page = n

		# create pages
		self.pages = []

		# i = 0
		# first = 0
		# last = self.num_items_per_page - 1
		# while True:
		# 	self.pages[i] = []

		# 	if first != 0:
		# 		back = self.create_nav_menu_item('Back', '')
		# 		self.pages[i].insert(0, back)

		# 	if last >= len(self.menu_items) - 1:
		# 		self.pages[i] = self.menu_items[first:last]
		# 		break
		# 	else:
		# 		last -= 1
		# 		self.pages[i] = self.menu_items[first:last]
		# 		next = self.create_nav_menu_item('Next', '')
		# 		self.pages[i].append(next)

		num_menu_items = len(self.menu_items)
		if num_menu_items <= self.num_items_per_page:
			self.pages.append(self.menu_items[:])
		else:
			page = self.menu_items[:self.num_items_per_page - 1]
			next = self.create_nav_menu_item('Next', 'snes.jpg')
			next.command = PMMenuItem.NEXT_PAGE
			page.append(next)
			self.pages.append(page)
			r = range(self.num_items_per_page - 1, num_menu_items - self.num_items_per_page + 1, self.num_items_per_page - 2)
			for i in r:
				page = self.menu_items[i:i + self.num_items_per_page - 2]
				back = self.create_nav_menu_item('Back', 'snes.jpg')
				back.command = PMMenuItem.PREV_PAGE
				next = self.create_nav_menu_item('Next', 'snes.jpg')
				next.command = PMMenuItem.NEXT_PAGE
				page.insert(0, back)
				page.append(next)
				self.pages.append(page)
			last_page = self.menu_items[self.num_items_per_page - 1 + len(r) * (self.num_items_per_page - 2):]
			back = self.create_nav_menu_item('Back', 'snes.jpg')
			back.command = PMMenuItem.PREV_PAGE
			last_page.insert(0, back)
			self.pages.append(last_page)

	def set_page(self, page_index):
		self.page_index = page_index

		self.empty()
		self.add(self.pages[page_index])

	def next_page(self):
		self.set_page(self.page_index + 1)

	def prev_page(self):
		self.set_page(self.page_index - 1)

	def get_adjacent_item(self, item, direction):
		index = self.menu_items.index(item)
		adj_index = None

		if(direction == PMDirection.LEFT):
			adj_index = index - 1
		elif(direction == PMDirection.RIGHT):
			adj_index = index + 1
		elif(direction == PMDirection.TOP):
			adj_index = index - options.num_items_per_row
		elif(direction == PMDirection.BOTTOM):
			adj_index = index + options.num_items_per_row

		if adj_index == None:
			return None

		return self.menu_items[adj_index]

