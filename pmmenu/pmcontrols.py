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
		
		keyboard = contr['KEYBOARD']
		joystick = contr['JOYSTICK']
		options = contr['OPTIONS']
			
		self.KEYBOARD = {}
		self.JOYSTICK = {}

		for key, value in contr['KEYBOARD'].iteritems():
			for entry in value:
				#convert string to pygame.key
				try:
					entry = "entry = " + entry
					exec entry
				except:
					print "INVALID CONTROLLER CONFIG: {!r}: {!r}".format(key, value)
				self.KEYBOARD[entry] = key
		
		for key, value in contr['JOYSTICK'].iteritems():
			if key == "RIGHT" or key == "LEFT":
				value = str(contr['JOYSTICK']['HORIZONTAL_AXIS']) + "|" + str(value)
			elif key == "UP" or key == "DOWN":
				value = str(contr['JOYSTICK']['VERTICAL_AXIS'])  + "|" + str(value)
			self.JOYSTICK[value] = key
		
		self.AXIAL_DRIFT = options['AXIS_DRIFT_TOLERANCE']
	
	def get_action(self, controller_source, action_type):
		
		#KEYBOARD
		if controller_source == 'keyboard':
			if action_type in self.KEYBOARD:
				return self.KEYBOARD[action_type]
			else:
				return None
				
		#JOYSTICK
		elif controller_source == 'joystick':
			
			#JOYSTICK MOVEMENT
			if isinstance(action_type, dict):
				if action_type['value'] < -(self.AXIAL_DRIFT): action_type['value'] = -1
				elif action_type['value'] > self.AXIAL_DRIFT: action_type['value'] = 1
				
				if (str(action_type['axis']) + "|" + str(action_type['value'])) in self.JOYSTICK:
					return self.JOYSTICK[str(action_type['axis']) + "|" + str(action_type['value'])]
				else:
					return None
					
			#JOYSTICK BUTTONS		
			else:
				if action_type in self.JOYSTICK:
					return self.JOYSTICK[action_type]
				else:
					return None
		else: return None
