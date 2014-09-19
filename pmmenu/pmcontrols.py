import pygame
import yaml

class PMControls:
	#check out for key reference - http://www.pygame.org/docs/ref/key.html
	JOY_PAD = None
	KEYBOARD = {}
	JOYSTICK = {}
	
	KEY_EVENT = [pygame.KEYDOWN, pygame.KEYUP]
	JOY_BUTTON_EVENT = [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]
	MOUSE_BUTTON_EVENT = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]
	
	def __init__(self):
		pygame.key.set_repeat(150, 20)
		
		pygame.joystick.init()
		js_count = pygame.joystick.get_count()
		for i in range(js_count):
			js = pygame.joystick.Joystick(i)
			js.init()
		
		
		if js_count: self.JOY_PAD = pygame.joystick.Joystick(0)
		
		#load config file, use open() rather than file(), file() is deprecated in python 3.
		stream = open('/home/pi/pimame/pimame-menu/controller.yaml', 'r')
		contr = yaml.safe_load(stream)
		stream.close()
		
		#KICKSTARTER COMBO
		contr['KEYBOARD']['KICKSTARTER'] = ["[pygame.K_k, pygame.K_s]"]
		
		
		#KEYBOARD CONFIG
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
					test = entry + 1
					key_list[entry] = 1
					
				except:
					for item in entry:
						key_list[item] = 1

				self.KEYBOARD[str(tuple(key_list))] = key
		
		#JOYSTICK CONFIG
		
		#AXIS CONFIG
		for key, value in contr['JOYSTICK']['DIRECTIONAL'].iteritems():
			if key == "RIGHT" or key == "LEFT":
				value = str(contr['JOYSTICK']['HORIZONTAL_AXIS']) + "|" + str(value)
			elif key == "UP" or key == "DOWN":
				value = str(contr['JOYSTICK']['VERTICAL_AXIS'])  + "|" + str(value)
				
			self.JOYSTICK[str(value)] = key
		
		#BUTTON CONFIG
		for key, value in contr['JOYSTICK']['BUTTONS'].iteritems():
			button_count = 100
			button_list = ([0] * button_count)
			
			try:
				test = value + 1
				button_list[value] = 1
				
			except:
				for item in value:
					button_list[item] = 1
					
			value = button_list
			self.JOYSTICK[str(value)] = key
		
		self.AXIAL_DRIFT = contr['OPTIONS']['AXIS_DRIFT_TOLERANCE']
		
	
	def get_action(self, input_test = [pygame.KEYDOWN, pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION], events = None):
		

		if not events: events = pygame.event.get(input_test)
		
		action = None
		
		

		for event in events:
			try:
			
				#KEYBOARD
				if event.type in self.KEY_EVENT:
					action = self.KEYBOARD[str(pygame.key.get_pressed())]
					break
					
				#JOYSTICK MOVEMENT
				elif event.type == pygame.JOYAXISMOTION:
					if event.dict['value'] <= -(self.AXIAL_DRIFT): event.dict['value'] = -1
					elif event.dict['value'] >= self.AXIAL_DRIFT: event.dict['value'] = 1
					action = self.JOYSTICK[str(event.dict['axis']) + "|" + str(event.dict['value'])]
			
				#JOYSTICK BUTTONS
				elif event.type in self.JOY_BUTTON_EVENT:
					if self.JOY_PAD:
						joy_buttons = ([0] * 100)
						for i in xrange(0,self.JOY_PAD.get_numbuttons()):
							button = self.JOY_PAD.get_button( i )
							if button: joy_buttons[ i ] = 1
						action = self.JOYSTICK[str(joy_buttons)]
				
				#MOUSE CLICK
				elif event.type in self.MOUSE_BUTTON_EVENT:
					action = "MOUSEBUTTON"
					
				#MOUSE MOVE
				elif event.type == pygame.MOUSEMOTION:
					action = "MOUSEMOVE"
			except:
				pass
		

		return action
