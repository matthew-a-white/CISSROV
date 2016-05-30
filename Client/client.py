import pygame
import time
import socket

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

sendData = True

TCP_IP = "192.168.0.10"
TCP_PORT = 5005

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputing the
# information.
class TextPrint:
	def __init__(self):
		self.reset()
		self.font = pygame.font.Font(None, 16)

	def printf(self, screen, textString):
		textBitmap = self.font.render(textString, True, BLACK)
		screen.blit(textBitmap, [self.x, self.y])
		self.y += self.line_height
		
	def reset(self):
		self.x = 10
		self.y = 10
		self.line_height = 15
		
	def indent(self):
		self.x += 10
		
	def unindent(self):
		self.x -= 10
	

pygame.init()
 
# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Joystick Testing")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
	
# Get ready to print
textPrint = TextPrint()

# Setup socket
if sendData:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))

# -------- Main Program Loop -----------
while done==False:
	# EVENT PROCESSING STEP
	for event in pygame.event.get(): # User did something
		if event.type == pygame.QUIT: # If user clicked close
			done=True # Flag that we are done so we exit this loop
		
		# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
		#if event.type == pygame.JOYBUTTONDOWN:
		#	print ("Joystick button pressed.")
		#if event.type == pygame.JOYBUTTONUP:
		#	print ("Joystick button released.")
			
 
	# DRAWING STEP
	# First, clear the screen to white. Don't put other drawing commands
	# above this, or they will be erased with this command.
	screen.fill(WHITE)
	textPrint.reset()

	# Get count of joysticks
	joystick_count = pygame.joystick.get_count()

	textPrint.printf(screen, "Number of joysticks: {}".format(joystick_count) )
	textPrint.indent()
	
	# Usable count of joysticks for for loop
	count = 0
	randomVariable = 0
	delimeters = 11
	axesData = ""
	comma = True	

	# For each joystick:
	for i in range(joystick_count):
		# Increase joystick number
		count += 1
		
		joystick = pygame.joystick.Joystick(i)
		joystick.init()
	
		textPrint.printf(screen, "Joystick {}".format(i) )
		textPrint.indent()
	
		# Get the name from the OS for the controller/joystick
		name = joystick.get_name()
		textPrint.printf(screen, "Joystick name: {}".format(name) )
		joystickString = "Joystick Name: " + str(name)
		
		# Usually axis run in pairs, up/down for one, and left/right for
		# the other.
		axes = joystick.get_numaxes()
		textPrint.printf(screen, "Number of axes: {}".format(axes) )
		axesCountString = "Number of Axes: " + str(axes)
		textPrint.indent()
		
		#axesString = "Axes Values:\n\t"      UNCOMMENT THIS FOR SENDING
		axesString = "<"
		#axesString += str(i) + ","			
		count2 = 0

		#for i in range( axes ):              UNCOMMENT THIS LATER
		#	count2 += 1
		#	axis = joystick.get_axis( i )
		#	textPrint.printf(screen, "Axis {} value: {:>6.3f}".format(i, axis) )
		#	axesString += "\tAxis " + str(count2) + ": " + str(round(axis, 4))

		listAxes1 = [0,1,2,4,5]
		listAxes2 = [1,2,5]
		listButtons2 = [0,1,4,5]

		if i == 1:
			for j in listAxes1:        #change range sometime 
				axis = joystick.get_axis(j)
				axesData += str(i) + "~" + str(round(axis, 4))  #changed from axesString
				textPrint.printf(screen, "Axis {} value: {:>6.3f}".format(j, axis) )
				if randomVariable < delimeters:  #number of entries - 1 for < number
					axesData += ","			
				randomVariable += 1
		else:
			for j in listAxes2:
				axis = joystick.get_axis(j)
				axesData += str(i) + "~" + str(round(axis, 4))
				textPrint.printf(screen, "Axis {} value: {:>6.3f}".format(j, axis) )
				if randomVariable < delimeters:
					axesData += ","
				randomVariable += 1
			for j in listButtons2:
				button = joystick.get_button(j)
				axesData += str(i) + "~" + str(button)
				if randomVariable < delimeters:
					axesData += ","
				randomVariable += 1
				textPrint.printf(screen, "Button {:>2} value: {}".format(i,button) )
				

		#axesString += ">"		

		textPrint.unindent()
			
		buttons = joystick.get_numbuttons()
		textPrint.printf(screen, "Number of buttons: {}".format(buttons) )
		buttonCountString = "Number of Buttons: " + str(buttons)
		textPrint.indent()
		
		buttonString = "Button Values:\n\t"
		buttonOptimized = ""

		#for i in range( buttons ):                     
 		#	button = joystick.get_button( i )
		#	textPrint.printf(screen, "Button {:>2} value: {}".format(i,button) )
		#	buttonString += "\t" + str(button)
		#	buttonOptimized = str(button)
		#textPrint.unindent()
			
		# Hat switch. All or nothing for direction, not like joysticks.
		# Value comes back in an array.
		hats = joystick.get_numhats()
		textPrint.printf(screen, "Number of hats: {}".format(hats) )
		hatCountString = "Number of Hats: " + str(hats)
		textPrint.indent()

		hatString = "Hat Values:\n\t"

		count3 = 0

		for i in range( hats ):
			count3 += 1
			hat = joystick.get_hat( i )
			textPrint.printf(screen, "Hat {} value: {}".format(i, str(hat)) )
			hatString += "\tHat " + str(count3) + ": " + str(hat)
		textPrint.unindent()
		
		textPrint.unindent()
		
		#if comma:
		#	axesData += ","
		#	comma = False
		# s.send("Joystick " + str(count) + ":\n\t" + joystickString + "\n\n\t" + axesCountString + "\n\t" + axesString + "\n\n\t" + buttonCountString + "\n\t" + buttonString + "\n\n\t" + hatCountString + "\n\t" + hatString + "\n\n\n")
		# s.send(buttonOptimized)
                #s.send(axesString)
	# ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
	#axesData += ">"
	print axesData + "\n"
	if sendData:
		s.send(axesData)
	# Go ahead and update the screen with what we've drawn.
	pygame.display.flip()

	# Limit to 10 frames per second
	clock.tick(50)

#	l = s.recv(1024)
#	print l
	
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
