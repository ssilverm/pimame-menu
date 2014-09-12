from menuitem import *

class PMGrid(pygame.sprite.OrderedUpdates):
	#menu_items = []
	# menu_items_by_sprite = None
	options = None
	next_icon = 'nav_next.png'
	back_icon = 'nav_back.png'
	next_selected = 'nav_next-selected.png'
	back_selected = 'nav_back-selected.png'
	

	def __init__(self, menu_item_cfgs, opts):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.menu_items = []
		self.options = opts
		self.first_index = self.last_index = 0

		if self.options.sort_items_alphanum:
			menu_item_cfgs.sort(key=lambda x: x['label'])

		for menu_item in menu_item_cfgs:
			#print menu_item
			if menu_item['visible']:
				pm_menu_item = PMMenuItem(menu_item, opts)
				#self.add(pm_menu_item)
				self.menu_items.append(pm_menu_item)

		if self.options.sort_items_with_roms_first:
			self.menu_items.sort(key=lambda x: x.num_roms if x.num_roms else "0", reverse=True) #!! FIX THIS 
		
		#pull all utilities to end of list
		self.menu_items.sort(key=self.utility_sort)
	
		if self.options.hide_system_tools:
			self.menu_items = [x for x in self.menu_items if x.type != "UTILITY"]
			
	def utility_sort(self, custom):
		if custom.type == "UTILITY": return 1
		return 0


	def create_nav_menu_item(self, label, icon_file = False, icon_selected = False):
		item = {}
		item['label'] = '' if not self.options.display_navigation_labels else label
		item['visible'] = True
		item['icon_file'] = icon_file
		item['icon_selected'] = icon_selected
		item['command'] = ''
		item['roms'] = ''
		item['full_path'] = True

		menu_item = PMMenuItem(item, self.options, PMMenuItem.NAVIGATION)

		return menu_item

	def set_num_items_per_page(self, n):
		self.num_items_per_page = n

		# create pages
		self.pages = []

		num_menu_items = len(self.menu_items)
		#total_num_of_icons = num_menu_items/num_items_per_page - 1(page) * (2 navigation buttons per page) + num_menu_items + 2 navigation buttons for first and last pages
		total_num_of_icons = (int(num_menu_items/self.num_items_per_page) - 1) * 2 + num_menu_items + 2
		total_num_of_pages = int(total_num_of_icons/self.num_items_per_page) + 1 #+1 b/c int always rounds down
		
		if total_num_of_pages == 1:
			self.pages.append(self.menu_items[:])
		else:
			num_items_to_display = self.num_items_per_page - 1
			page = self.menu_items[:num_items_to_display]
			next = self.create_nav_menu_item('Next', self.next_icon, self.next_selected)
			next.command = PMMenuItem.NEXT_PAGE
			page.append(next)
			self.pages.append(page)
			r = xrange(1, total_num_of_pages)
			iteration = 0
			for i in r:
				iteration += num_items_to_display
				num_items_to_display = self.num_items_per_page - 2
					
				page = self.menu_items[iteration: iteration + num_items_to_display]
				back = self.create_nav_menu_item('Back', self.back_icon, self.back_selected)
				back.command = PMMenuItem.PREV_PAGE
				next = self.create_nav_menu_item('Next', self.next_icon, self.next_selected)
				next.command = PMMenuItem.NEXT_PAGE
				page.insert(0, back)
				if i != len(r): page.append(next)
				self.pages.append(page)
				
			last_page = self.menu_items[self.num_items_per_page - 1 + len(r) * (self.num_items_per_page - 2):]
			back = self.create_nav_menu_item('Back', self.back_icon, self.back_selected)
			back.command = PMMenuItem.PREV_PAGE
			last_page.insert(0, back)
			self.pages.append(last_page)

		self.set_page(0)

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

