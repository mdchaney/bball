#!/usr/bin/env python

# Basketball game with two baskets

import RPi.GPIO as GPIO
import time

# IO pins to use
DataPin  = 11   # GPIO 17 (WiringPi pin num 0) header pin 11
ClockPin = 15   # GPIO 22 (WiringPi pin num 3) header pin 15
LoadPin  = 16   # GPIO 23 (WiringPi pin num 4) header pin 16

Basket1Pin = 36 # GPIO 27 (WiringPi pin num 27) header pin 36
Basket2Pin = 38 # GPIO 28 (WiringPi pin num 28) header pin 38

PowerPin   = 40 # GPIO 28 (WiringPi pin num 29) header pin 38

baskets = { '1': { 'pin': Basket1Pin, 'score': 0, 'display_offset': 1 }, '2': { 'pin': Basket2Pin, 'score': 0, 'display_offset': 4 } }

debounce_wait = 100

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
	global baskets

	GPIO.setmode(GPIO.BOARD)         # Numbers GPIOs by physical location

	GPIO.setup(DataPin, GPIO.OUT)    # Set pin modes to output
	GPIO.setup(ClockPin, GPIO.OUT)
	GPIO.setup(LoadPin, GPIO.OUT)

	GPIO.output(DataPin, GPIO.HIGH)  # Set pins high(+3.3V)
	GPIO.output(ClockPin, GPIO.HIGH)
	GPIO.output(LoadPin, GPIO.HIGH)

	GPIO.setup(Basket1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(Basket2Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(PowerPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	max7219_send(SetDecodeMode, 0x3F)
	max7219_send(SetDisplayTest, 0)
	max7219_send(SetIntensity, 1)
	max7219_send(SetScanLimit, 5)
	max7219_send(SetShutdown, 1)

	for basket_id, basket_info in baskets.items():
		GPIO.add_event_detect(basket_info['pin'], GPIO.FALLING, callback=made_basket, bouncetime = debounce_wait)
		update_score(basket_info['score'], basket_info['display_offset'])

	return

def setdown():
	max7219_send(SetShutdown, 0)
	GPIO.cleanup()
	return

def made_basket(pin=None):
	global baskets

	basket_id = None

	# Given the pin # get a basket_id
	for k, basket_info in baskets.items():
		if basket_info['pin'] == pin:
			basket_id = k
			break

	if basket_id:
		basket = baskets[k]
		basket['score'] += 2
		update_score(basket['score'], basket['display_offset'])
	else:
		print("Unknown pin: %d\n" % (pin))

	return

def update_score(score, offset):
	digit1 = score % 10
	digit2 = (score/10) % 10
	digit3 = (score/100) % 10
	if digit3 == 0 and digit2 == 0:
		digit2 = 15
	if digit3 == 0:
		digit3 = 15
	max7219_send(offset, digit1)
	max7219_send(offset+1, digit2)
	max7219_send(offset+2, digit3)

	return

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		time.sleep(60)
		setdown()
	except KeyboardInterrupt:
		# shut down if ctrl-c pressed
		setdown()

