import datetime
import threading
import onionGpio
import config
from logger import CustomLogger

class GpioControl:
	@staticmethod
	def establishPin(pin, direction, default):
		print '> Initializing gpio pin %d'%(pin)
		gpioObj = onionGpio.OnionGpio(pin)

		if direction == 0:
			print '> Setting gpio pin %d to input'%(pin)
			status = gpioObj.setInputDirection()
		elif direction == 1:
			print '> Setting gpio pin %d to output'%(pin)
			status = gpioObj.setOutputDirection(default)

		print '> Pin established'
		
		return gpioObj

	@staticmethod
	def readSensor(gpioObj):
		value = gpioObj.getValue()
		if int(value) == 0:
			return True
		return False

	@staticmethod
	def ledColor(color):
		pins = [15, 16, 17]

		if color == 'red':
			GpioControl.establishPin(17, 1, 0)
			pins.remove(17)
		elif color == 'green':
			GpioControl.establishPin(16, 1, 0)
			pins.remove(16)
		elif color == 'blue':
			GpioControl.establishPin(15, 1, 0)
			pins.remove(15)
		elif color == 'yellow':
			GpioControl.establishPin(16, 1, 0)
			GpioControl.establishPin(17, 1, 0)
			pins.remove(16)
			pins.remove(17)
		else:
			return False

		for pin in pins:
			GpioControl.establishPin(pin, 1, 1)

		return True

class StoppableThread(threading.Thread):
	def __init__(self):
		super(StoppableThread, self).__init__()
		self._stop = threading.Event()
		self.gpioObj = GpioControl.establishPin(1, 0, 0)
		self.broken = False

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def run(self):
		while True:
			currentState = GpioControl.readSensor(self.gpioObj)
			if currentState != self.broken:
				self.broken = currentState
				if currentState:
					time = datetime.datetime.now()
					CustomLogger.logFile('* %s - Sensor broken\n' % time, config.sensorLogfile)
			if self.stopped():
				self.stop()
				break
