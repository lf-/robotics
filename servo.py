from RPIO.PWM import Servo as RServo

servo = RServo()

class Servo:

	def __init__(self, pin):
		self.pin = pin
		self._rate = None
		self._angle = None
	
	@property
	def rate(self):
		return self._rate

	@rate.setter
	def rate(self, ms):
		self.angle = (ms - 1000) * (9/50)
		self.rate = ms
		servo.set_servo(self.pin, self.rate)

	@property
	def angle(self):
		return self._angle

	@angle.setter
	def angle(self, angle):
		self.angle = angle
		self.rate = ((50/9.0)*angle) + 1000
		servo.set_servo(self.pin, self.rate)

	def stop(self):
		servo.stop_servo(self.pin)
		
