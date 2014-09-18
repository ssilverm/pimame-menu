import pygame
import yaml

class PMControls:
 #check out for key reference - http://www.pygame.org/docs/ref/key.html
	def __init__(self):
		pygame.key.set_repeat(300, 10)
		
		pygame.joystick.init()
		js_count = pygame.joystick.get_count()
		for i in range(js_count):
			js = pygame.joystick.Joystick(i)
			js.init()
		  
		
		#load config file, use open() rather than file(), file() is deprecated in python 3.
		stream = open('/home/pi/pimame/pimame-menu/controller.yaml', 'r')
		contr = yaml.safe_load(stream)
		stream.close()
		
		#keyboard = contr['KEYBOARD']
		#joystick = contr['JOYSTICK']
		#options = contr['OPTIONS']
			
		self.KEYBOARD = {}
		self.JOYSTICK = {}
		
		#add kickstarter key combo
		contr['KEYBOARD']['KICKSTARTER'] = ["[pygame.K_k, pygame.K_s]"]
		
		for key, value in contr['KEYBOARD'].iteritems():
			for entry in value:
				#convert string to pygame.key
				try:
					entry = "entry = " + entry
					exec entry
				except:
					print "INVALID CONTROLLER CONFIG: {!r}: {!r}".format(key, value)
					
				#generate list of 'unpressed' keys
				key_list = ([0] * len(pygame.key.get_pressed()))
				try:
					entry = entry + 1
					key_list[entry - 1] = 1
					
				except:
					return_string = ""
					for item in entry:
						key_list[item] = 1

				self.KEYBOARD[str(tuple(key_list))] = key
		
		for key, value in contr['JOYSTICK'].iteritems():
			if key == "RIGHT" or key == "LEFT":
				value = str(contr['JOYSTICK']['HORIZONTAL_AXIS']) + "|" + str(value)
			elif key == "UP" or key == "DOWN":
				value = str(contr['JOYSTICK']['VERTICAL_AXIS'])  + "|" + str(value)
			self.JOYSTICK[str(value).replace(' ','')] = key
		
		self.AXIAL_DRIFT = contr['OPTIONS']['AXIS_DRIFT_TOLERANCE']
	
	def get_action(self, input_test = [pygame.KEYDOWN, pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION], events = None):
		

		if not events: events = pygame.event.get(input_test)
		
		action = None
		joy_buttons = []
		
		
		
		for event in events:
			try:
			
				#KEYBOARD
				if event.type == pygame.KEYDOWN:
					action = self.KEYBOARD[str(pygame.key.get_pressed())]
					
				#JOYSTICK MOVEMENT
				elif event.type == pygame.JOYAXISMOTION:
					if event.dict['value'] <= -(self.AXIAL_DRIFT): event.dict['value'] = -1
					elif event.dict['value'] >= self.AXIAL_DRIFT: event.dict['value'] = 1
					action = self.JOYSTICK[str(event.dict['axis']) + "|" + str(event.dict['value'])]
			
				#JOYSTICK BUTTONS
				elif event.type == pygame.JOYBUTTONDOWN:
						joy_buttons.append(event.button)
						action = self.JOYSTICK[event.button]
				
				#MOUSE CLICK
				elif event.type == pygame.MOUSEBUTTONUP:
					action = "MOUSEUP"
				#MOUSE MOVE
				elif event.type == pygame.MOUSEMOTION:
					action = "MOUSEMOVE"
			except:
				pass
			
		if len(joy_buttons) > 1: 
			try: action = self.JOYSTICK[str(joy_buttons).replace(' ','')]
			except: pass
		return action
					
		#JOYSTICK

		#JOYSTICK MOVEMENt
		"""elif event.type == pygame.JOYAXISMOTION:
			if action_type['value'] < -(self.AXIAL_DRIFT): action_type['value'] = -1
			elif action_type['value'] > self.AXIAL_DRIFT: action_type['value'] = 1
			
			if (str(action_type['axis']) + "|" + str(action_type['value'])) in self.JOYSTICK:
				return self.JOYSTICK[str(action_type['axis']) + "|" + str(action_type['value'])]
			else:
				return None
				
		#JOYSTICK BUTTONS		
		elif if event.type == pygame.JOYBUTTONDOWN:
			if action_type in self.JOYSTICK:
				return self.JOYSTICK[action_type]
			else:
				return None
		else: return None
		
		elif event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()

			# get all rects under cursor
			clicked_sprites = [s for s in self.grid if s.rect.collidepoint(pos)]
			
			if len(clicked_sprites) > 0:
				sprite = clicked_sprites[0]
				self.do_menu_item_action(sprite)"""
