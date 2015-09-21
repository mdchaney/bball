#!/usr/bin/env python

# Demonstration of using Max7219 chip with raspberry pi
# and Python.  Program will count from 0-999 on first three digits
# and 999-0 on second three digits.  Includes code to setup,
# handle clock & latch, and send 16 bits at a time.

import RPi.GPIO as GPIO
import time

# IO pins to use
DataPin  = 11   # GPIO 17 (WiringPi pin num 0) header pin 11
ClockPin = 15   # GPIO 22 (WiringPi pin num 3) header pin 15
LoadPin  = 16   # GPIO 23 (WiringPi pin num 4) header pin 16

# Max7219 command set
SetDecodeMode  = 0x09    # data payload is bitmask for BCM digits
SetIntensity   = 0x0a    # intensity of LEDs (0 to 15)
SetScanLimit   = 0x0b    # set top digit to use (0 to 7)
SetShutdown    = 0x0c    # set to "1" to come out of shutdown, "0" to shutdown
SetDisplayTest = 0x0f    # set to "1" to test display (all segments on)

def send_16_bits(bits):
	mask = 0x8000
	for i in range(16):
		GPIO.output(ClockPin, GPIO.LOW)
		GPIO.output(DataPin, GPIO.HIGH if (bits & mask) else GPIO.LOW)
		GPIO.output(ClockPin, GPIO.HIGH)
		mask >>= 1

def max7219_send(register, data):
	GPIO.output(LoadPin, GPIO.LOW)
	send_16_bits(((register & 0xF) << 8) | (data & 0xFF))
	GPIO.output(LoadPin, GPIO.HIGH)
	GPIO.output(LoadPin, GPIO.LOW)

def setup():
	GPIO.setmode(GPIO.BOARD)         # Numbers GPIOs by physical location

	GPIO.setup(DataPin, GPIO.OUT)    # Set pin modes to output
	GPIO.setup(ClockPin, GPIO.OUT)
	GPIO.setup(LoadPin, GPIO.OUT)

	GPIO.output(DataPin, GPIO.HIGH)  # Set pins high(+3.3V)
	GPIO.output(ClockPin, GPIO.HIGH)
	GPIO.output(LoadPin, GPIO.HIGH)

	max7219_send(SetDecodeMode, 0x3F)
	max7219_send(SetDisplayTest, 0)
	max7219_send(SetIntensity, 1)
	max7219_send(SetShutdown, 1)

def setdown():
	max7219_send(SetShutdown, 0)
	GPIO.cleanup()

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		for i in range(1000):
			max7219_send(1, i % 10)
			max7219_send(2, (i/10) % 10)
			max7219_send(3, (i/100) % 10)
			max7219_send(4, ((999-i)) % 10)
			max7219_send(5, ((999-i)/10) % 10)
			max7219_send(6, ((999-i)/100) % 10)
			time.sleep(.01)
		time.sleep(2)
		setdown()
	except KeyboardInterrupt:
		# shut down if ctrl-c pressed
		setdown()

