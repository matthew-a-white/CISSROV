import serial.tools.list_ports
import serial

ser = ""

ports = list(serial.tools.list_ports.comports())

for p in ports:
	print p