import RPIO.PWM.Servo as RServo

class Servo:

	servo = RServo()
	
	def __init__(self, pin):
		self.pin = pin
	
	@property
	def rate(self):
		return self.rate

	@rate.setter
	def rate(self, ms):
		self.angle = (ms - 1000) * (9/50)
		self.rate = ms
		self.servo.set_servo(self.pin, self.rate)

	@property
	def angle(self):
		return self.angle

	@angle.setter
	def angle(self, angle):
		self.angle = angle
		self.rate = ((50/9.0)*angle) + 1000
		self.servo.set_servo(self.pin, self.rate)

	def stop(self):
		servo.stop_servo(self.pin)
		
