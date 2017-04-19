# to use the omega's hardware
# GpioControl control controls the omega's inputs and outputs
# StoppableThread creates a thread that can be easily stopped

import datetime
import threading
import onionGpio
import config
from logger import CustomLogger

class GpioControl:
	@staticmethod
	def _establish_pin(pin, direction, default):
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
	def read_sensor(gpioObj):
		value = gpioObj.getValue()
		if int(value) == 0:
			return True
		return False

	@staticmethod
	def led_color(color):
		valid_colors = [
			'red',
			'green',
			'blue',
			'yellow',
			'off'
		]

		if color not in valid_colors:
			return False
		else:
			pins = [15, 16, 17]

			if color == 'red':
				GpioControl._establish_pin(17, 1, 0)
				pins.remove(17)
			elif color == 'green':
				GpioControl._establish_pin(16, 1, 0)
				pins.remove(16)
			elif color == 'blue':
				GpioControl._establish_pin(15, 1, 0)
				pins.remove(15)
			elif color == 'yellow':
				GpioControl._establish_pin(16, 1, 0)
				GpioControl._establish_pin(17, 1, 0)
				pins.remove(16)
				pins.remove(17)

			for pin in pins:
				GpioControl._establish_pin(pin, 1, 1)

		return True

class StoppableThread(threading.Thread):
	def __init__(self):
		super(StoppableThread, self).__init__()
		self._stop = threading.Event()
		self._gpioObj = GpioControl._establish_pin(1, 0, 0)
		self._broken = False

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def run(self):
		while True:
			current_state = GpioControl.read_sensor(self._gpioObj)
			if current_state != self._broken:
				self._broken = current_state
				if current_state:
					time = str(datetime.datetime.now())[:-10]
					door_status = 'Closed' if config.door_open else 'Open'
					CustomLogger.log_file('* %s - %s\n' % (time, door_status), config.sensor_log_file)
					config.door_open = not config.door_open
			if self.stopped():
				self.stop()
				break
