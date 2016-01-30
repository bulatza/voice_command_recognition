# GPIO settings
import RPi.GPIO as GPIO
import time

class Gpioled:
	def __init__(self, pin1, pin2, dt):
		self.pin1 = pin1 #green
		self.pin2 = pin2 #red
		self.dt = dt
			
		#import RPi.GPIO as GPIO
		#import time
	
		# setup GPIO. LED Indication
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin1, GPIO.OUT)
		GPIO.setup(pin2, GPIO.OUT) 

	def high(self):
		GPIO.output(self.pin1, GPIO.HIGH)
		GPIO.output(self.pin2, GPIO.HIGH)

	def low(self):
		GPIO.output(self.pin1, GPIO.LOW)
		GPIO.output(self.pin2, GPIO.LOW)

	def wait(self):
		GPIO.output(self.pin1, GPIO.HIGH)
		GPIO.output(self.pin2, GPIO.LOW)

	def rec(self):
		GPIO.output(self.pin1, GPIO.LOW)
		GPIO.output(self.pin2, GPIO.HIGH)

	def badStatus(self):
		GPIO.output(self.pin1, GPIO.LOW)
		
		GPIO.output(self.pin2, GPIO.HIGH)
		time.sleep(self.dt)
		GPIO.output(self.pin2, GPIO.LOW)
		time.sleep(self.dt)
		GPIO.output(self.pin2, GPIO.HIGH)
		time.sleep(self.dt)
		GPIO.output(self.pin2, GPIO.LOW)
                time.sleep(self.dt)
                GPIO.output(self.pin2, GPIO.HIGH)
                time.sleep(self.dt)
                GPIO.output(self.pin2, GPIO.LOW)

	def goodStatus(self):
		GPIO.output(self.pin2, GPIO.LOW)
		
		GPIO.output(self.pin1, GPIO.HIGH)
		time.sleep(self.dt)
		GPIO.output(self.pin1, GPIO.LOW)
		time.sleep(self.dt)
		GPIO.output(self.pin1, GPIO.HIGH)
		time.sleep(self.dt)
		GPIO.output(self.pin1, GPIO.LOW)
                time.sleep(self.dt)
                GPIO.output(self.pin1, GPIO.HIGH)
                time.sleep(self.dt)
                GPIO.output(self.pin1, GPIO.LOW)

	def errorStatus(self):
		self.low()
		while True:
			GPIO.output(self.pin1, GPIO.HIGH)
			time.sleep(self.dt)
			GPIO.output(self.pin1, GPIO.LOW)
			time.sleep(self.dt)
			GPIO.output(self.pin2, GPIO.HIGH)
			time.sleep(self.dt)
			GPIO.output(self.pin2, GPIO.LOW)
			time.sleep(self.dt)

