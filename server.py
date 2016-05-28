import smbus
import time
import serial
import serial.tools.list_ports
from flask import Flask         #pip install Flask to install
from flask.ext import restful
from flask.ext.restful.utils import cors
from flask.ext.cors import CORS #pip install -U flask-cors to install
#pip install flask-restful


app = Flask(__name__)
api = restful.Api(app)
api.decorators=[cors.crossdomain(origin='*')]

serPort = ""
ports = list(serial.tools.list_ports.comports())

#for p in ports:
#    if "Arduino Mega" in p:
#	serPort = str(p)[0:12]
serPort = "/dev/ttyACM0"
serPort2 = "/dev/ttyUSB0"

baudRate = 9600
baudRate2 = 57600

ser = serial.Serial(serPort, baudRate)
ser2 = serial.Serial(serPort2, baudRate2)

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
	if value >= 0:
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

resultedParse0 = []
resultedParse1 = []

verticalThrust = 90
verticalThrustMax = 180
verticalThrustMin = 0
#------------------------
mainClawHold = 90
mainClawHoldMax = 140
mainClawHoldMin = 70
#------------------------
downClawHold = 20
downClawHoldMax = 60
downClawHoldMin = 20
#------------------------
mainClawSpinHold = 15
mainClawSpinHoldMax = 180
mainClawSpinHoldMin = 0
#------------------------
tempHold = 0
tempHoldMax = 90
tempHoldMin = 0

def parseC0(array):
	for i in parseNoHold1:
		axes = float(array[i])
		axes = errorFix(axes)
		if axes < 0:
			axes = translate(axes, -1, 0, 0, 90) 
		else:
			axes = translate(axes, 0, 1, 90, 180)
		resultedParse0.append(int(axes))

	axes2 = float(array[2])
	axes4 = float(array[4])
	
	global verticalThrust	

	if axes2 > -0.9 and axes4 > -0.9:
		verticalThrust = 90
	else:
		axes2 = breakpoint(axes2)
		if axes2 == 1 and verticalThrust < verticalThrustMax:
			verticalThrust += 1
 	
		axes4 = breakpoint(axes4)
		if axes4 == 1 and verticalThrust > verticalThrustMin:
			verticalThrust -= 1
	
	resultedParse0.append(verticalThrust)

def parseC1(array):
	global tempHold, mainClawHold, downClawHold, mainClawSpinHold

	axes0 = float(array[0])
	axes0 = errorFix(axes0)
	axes0 = roundTemp(axes0)
	if axes0 == 1 and tempHold < tempHoldMax:
		tempHold += 1 #changed from -axes0 	
	elif axes0 == -1 and tempHold > tempHoldMin:
		tempHold -= 1

	axes1 = float(array[1])
	axes2 = float(array[2])
	
	if axes1 > -0.9 and axes2 > -0.9:
		mainClawHold = 90
	else:
		axes1 = breakpoint(axes1)
		if axes1 == 1 and mainClawHold < mainClawHoldMax: 
			mainClawHold += 1

		axes2 = breakpoint(axes2)
		if axes2 == 1 and mainClawHold > mainClawHoldMin:
			mainClawHold -= 1

	button3 = int(array[3])
	button4 = int(array[4])

	if button3 == 1 and button4 == 1:
		downClawHold = 20
	else:
		if button3 == 1 and downClawHold < downClawHoldMax:
			downClawHold += 1
	
		if button4 == 1 and downClawHold > downClawHoldMin:
			downClawHold -= 1

	button5 = int(array[5])
	button6 = int(array[6])

	if button5 == 1 and button6 == 1:
		mainClawSpinHold = 15
	else:
		if button5 == 1 and mainClawSpinHold > mainClawSpinHoldMin: 
			mainClawSpinHold -= 1

		if button6 == 1 and mainClawSpinHold < mainClawSpinHoldMax:
			mainClawSpinHold += 1
	
	resultedParse1.append(tempHold)
	resultedParse1.append(mainClawHold)
	resultedParse1.append(downClawHold)
	resultedParse1.append(mainClawSpinHold)

#---------------------
finalData = ""

def formatData(controller0, controller1):
	global finalData

	finalData += "<"

	for i in controller0:
		finalData += str(i) + "|"
	for j in controller1:
		finalData += str(j) + "|"
	
	finalData = finalData[:-1]
	finalData += ">"


while True:
    conn, addr = s.accept()
    print "Got connection from", addr
    l = conn.recv(1024)
    conn.send("echo")

    @app.route('/depth', methods=['GET'])
	@cors.crossdomain(origin='*')
	def tempDepth():
		return ser.readline()

	@app.route('', methods=['GET'])
	@cors.crossdomain(origin='*')
	def gyro():
		return ser2.readline()

	if __name__ == '__main__':
			app.run( 
    		host="192.168.0.10",
    		port=int("3000")
			)

    while(l):
    #        print "==============================\n    CURRENTLY CONNECTED TO\n" + str(addr) + "\n      AND RECEIVING DATA" + "\n==============================\n\n\n\n\n\n" + l
            l = conn.recv(1024)
	listIt(l)
	#print data0
	#print data1
	#print "\n"
	#print "\n"
	parseC0(data1)
	parseC1(data0)
	formatData(resultedParse0, resultedParse1)
	print finalData
	print "\n"
	data0 = []
	data1 = []
	resultedParse0 = []
	resultedParse1 = []
	finalData = ""


	

	#try:
	#	ser.write(finalData)
	#except:
	#	pass
#	try:
#		ser.write(str(l))
#	except:
#		pass
#	#writeData(int(l))
	#print "RPI: Send data, ", l
#	#time.sleep(1)
	#print
	#print ser.readline()
	#ser.flushInput()
	#ser.flushOutput()

    #       conn.send("echo")
#print "\n\n\n==============================\n      DISCONNECTED FROM\n" + str(addr) + "\n    AND NOT RECEIVING DATA" + "\n=============================="
    conn.close()
