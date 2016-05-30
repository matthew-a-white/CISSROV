#import smbus
import time
import serial
import serial.tools.list_ports

serPort = ""
ports = list(serial.tools.list_ports.comports())

#for p in ports:
#    if "Arduino Mega" in p:
#	serPort = str(p)[0:12]
serPort = "/dev/ttyACM0"

baudRate = 9600
ser = serial.Serial(serPort, baudRate)

#Start setup section for Server
import socket
import sys

TCP_IP = ""
TCP_PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(5)

data0 = []
data1 = []
#End setup section for Server
def listIt(str):
	array = str.split(',')
	for i in array:
		if "0~" in i:
			data0.append(i[2:])
		elif "1~" in i:
			data1.append(i[2:])

def errorFix(value):
	if value < 0.075 and value > -0.075:
		return 0
	return value

def breakpoint(value):
	if value >= 0.1:
		return 1
	return 0 

def translate(value, leftMin, leftMax, rightMin, rightMax):
	# Figure out how 'wide' each range is
	leftSpan = leftMax - leftMin
	rightSpan = rightMax - rightMin

	# Convert the left range into a 0-1 range (float)
	valueScaled = float(value - leftMin) / float(leftSpan)

	# Convert the 0-1 range into a value in the right range.
	return rightMin + (valueScaled * rightSpan)

def roundTemp(num):
	if num < 0:
		return -1
	elif num > 0:
		return 1
	return 0 		

#DEFINE VALUES FOR PARSING
parseNoHold1 = [0, 1, 3]
parseHold1 = [2, 4]
#------------------------
resultedParse0 = []
resultedParse1 = []
#------------------------
verticalThrust = 90
verticalThrustMax = 150
verticalThrustMin = 40
#------------------------
mainClawHold = 70
mainClawHoldMax = 110
mainClawHoldMin = 50
#------------------------
downClawHold = 40
downClawHoldMax = 60
downClawHoldMin = 20
#------------------------
mainClawSpinHold = 15
mainClawSpinHoldMax = 180
mainClawSpinHoldMin = 0
#------------------------
tempHold = 20
tempHoldMax = 90
tempHoldMin = 15
#------------------------
#oldData = [90, 90, 90, 90, 70, 40, 0, 15] #used for error checking
#oldData = []
#------------------------
badData = False
verticalThrustFix = 0

def checkData(array):
	global badData
	
	#print "CHECKING DATA"

	for data in array:
		#print data
		#print "============		
		
		if not (data.replace('.','',1).replace('-','',1).isdigit()):
			#print "BAD DATA = " + str(data)
			badData = True
			return True
	
	return False

def parseC0(array):

	#print 1
	#print checkData(array)
	if checkData(array):
		#print array
		return

	#print 2

	for i in parseNoHold1:
		#catch0 = 0
		#try:
		axes = float(array[i])		
		#except:
			#catch0 = 1
			#pass	

		#if catch0 == 0:
		axes = errorFix(axes)
		
		if i != 0:
			axes = axes * -1
		
		if axes < 0:
			axes = translate(axes, -1, 0, 35, 90) 
		else:
			axes = translate(axes, 0, 1, 90, 145)
		#print "Axis: " + str(i) + " = " + str(axes)
		resultedParse0.append(int(axes))
		#oldData.append(int(axes))
	
	#catch1 = 0
	#try:
	axes2 = float(array[2])
	axes4 = float(array[4])
	#except:
	#	catch1 = 1
	#	pass

	global verticalThrust, verticalThrustFix
	
	verticalThrustFix += 1

	#print "Axes 2: " + str(axes2)
	#print "Axes 4: " + str(axes4)

	if axes2 > 0.5 and axes4 > 0.5:
		#print "VERTICAL THRUST RESET"
		verticalThrust = 90
	else:
		axes2 = breakpoint(axes2)
		if axes2 == 1 and verticalThrust < verticalThrustMax:
			verticalThrust += 1
 	
		axes4 = breakpoint(axes4)
		if axes4 == 1 and verticalThrust > verticalThrustMin:
			verticalThrust -= 1
	
	if checkData(array) and verticalThrust < verticalThrustMax:
		verticalThrust += 1
		verticalThrustFix = 0

	resultedParse0.append(verticalThrust)

def parseC1(array):
	global tempHold, mainClawHold, downClawHold, mainClawSpinHold, badData
	#catch2 = 0	

	#print 3
	#print checkData(array)
	if checkData(array):
		return

	#print 4

	#try: 
	axes0 = float(array[0])
	axes1 = float(array[1])
	axes2 = float(array[2])
	button3 = int(array[3])
	button4 = int(array[4])
	button5 = int(array[5])
	button6 = int(array[6])
	#except:
	#	catch2 = 1
	#	pass

	#if catch2 == 0:
	axes0 = errorFix(axes0)
	axes0 = roundTemp(axes0)
	if axes0 == 1 and tempHold < tempHoldMax:
		tempHold += 1 #changed from -axes0 	
	elif axes0 == -1 and tempHold > tempHoldMin:
		tempHold -= 1
	
	#axes1 = float(array[1])
	#axes2 = float(array[2])

	if axes1 > -0.9 and axes2 > -0.9:
		mainClawHold = 70
	else:
		axes1 = breakpoint(axes1)
		if axes1 == 1 and mainClawHold < mainClawHoldMax: 
			mainClawHold += 2

		axes2 = breakpoint(axes2)
		if axes2 == 1 and mainClawHold > mainClawHoldMin:
			mainClawHold -= 2

	#button3 = int(array[3])
	#button4 = int(array[4])

	if button3 == 1 and button4 == 1:
		downClawHold = 20
	else:
		if button3 == 1 and downClawHold < downClawHoldMax:
			downClawHold += 1
	
		if button4 == 1 and downClawHold > downClawHoldMin:
			downClawHold -= 1

	#button5 = int(array[5])
	#button6 = int(array[6])

	if button5 == 1 and button6 == 1:
		mainClawSpinHold = 15
	else:
		if button5 == 1 and mainClawSpinHold > mainClawSpinHoldMin: 
			mainClawSpinHold -= 1

		if button6 == 1 and mainClawSpinHold < mainClawSpinHoldMax:
			mainClawSpinHold += 1
	
	resultedParse1.append(mainClawHold)
	resultedParse1.append(downClawHold)
	resultedParse1.append(tempHold)
	resultedParse1.append(mainClawSpinHold)

#---------------------
finalData = ""

def formatData(controller0, controller1):
	global finalData
	
	#print 5
	
	finalData += "<"

	for i in controller0:
		finalData += str(i) + ","
	for j in controller1:
		finalData += str(j) + ","
	
	finalData = finalData[:-1]
	finalData += ">"

while True:

        conn, addr = s.accept()
        print "Got connection from", addr
        l = conn.recv(1024)
        conn.send("echo")
        while(l):
                #print "==============================\n    CURRENTLY CONNECTED TO\n" + str(addr) + "\n      AND RECEIVING DATA" + "\n==============================\n\n\n\n\n\n" + l
                l = conn.recv(1024)
		listIt(l)
		#print data0
		#print data1
		#print "\n"
		#print "\n"
		#print 1
		#----------------START BAD DATA FIX
		parseC0(data1)
		parseC1(data0)

		#print 6		

		#print 2
		#print badData
		if True: #not (badData):
			#print 3
			formatData(resultedParse0, resultedParse1)
			#print finalData
			#print "\n"
			#print 4
			#print 7

			try:
				ser.write(finalData + '\r\n')
				#print 8
			except:
				pass
		#print 6
		#print 9
		badData = False
		#print 7
		#----------------END BAD DATA FIX


		data0 = []
		data1 = []
		#finalData = finalData[1:len(finalData) - 1]
		#oldData = finalData.split("|")
		#print oldData
		#oldData = []
		resultedParse0 = []
		resultedParse1 = []
		finalData = ""
		#print 8
	#	try:
	#		ser.write(str(l))
	#	except:
	#		pass
	#	writeData(int(l))
	#	print "RPI: Send data, ", l
	#	time.sleep(0.1)
		
		try: 
			tempDepth = ser.readline()
		except:
			pass

		index = 0
		try:
			index = tempDepth.index("<String")		
		except:
			pass

		if index > 9 and index < 14:
			print tempDepth[0:index]
	
	#	print ser.readline()
	
		#print 10		

		ser.flushInput()
		ser.flushOutput()

		#print 11
		#print 9
        #       conn.send("echo")

	print "\n\n\n==============================\n      DISCONNECTED FROM\n" + str(addr) + "\n    AND NOT RECEIVING DATA" + "\n=============================="
        conn.close()
