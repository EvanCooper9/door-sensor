import os
import sys
import signal
import config
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler
from mimetypes import types_map
from logger import CustomLogger
from omega import StoppableThread
from omega import GpioControl

class ThreadContainer:
	thread = StoppableThread()

class MyHandler(BaseHTTPRequestHandler):
	html = open('html/index.html', 'a+').read()

	validRequests = [
		'/help', 
		'/status', 
		'/disable', 
		'/enable', 
		'/clearLogs', 
		'/clearSensorLogs', 
		'/clearServerLogs'
	]

	validFileTypes = [
		'.js', 
		'.css', 
		'.woff2', 
		'.woff', 
		'.ttf', 
		'.json'
	]

	def log_message(self, format, *args):
		message = '[%s] %s\n' % (self.log_date_time_string(), format%args)
		CustomLogger.logFile(message, config.serverLogfile)

	def do_GET(self):
		fname, ext = os.path.splitext(self.path)

		if self.path in self.validRequests:
			if self.path == '/help':
				self.send_response(200)
				self.send_header('Cache-Control', 'no-cache')
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write('validRequests: %s' % (', '.join(validRequests)))

			elif self.path == '/status':
				self.send_response(200)
				self.send_header('Cache-Control', 'no-cache')
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				statusIcon = 'power_settings_new' if ThreadContainer.thread.stopped() else 'done'

				self.wfile.write(self.html % (statusIcon, CustomLogger.readLog(config.sensorLogfile), CustomLogger.readLog(config.serverLogfile)))

			else:
				if self.path == '/disable':
					if not ThreadContainer.thread.stopped():
						ThreadContainer.thread.stop()
						GpioControl.ledColor('blue')
				if self.path == '/enable':
					if ThreadContainer.thread.stopped():
						ThreadContainer.thread = StoppableThread()
						ThreadContainer.thread.start()
						GpioControl.ledColor('green')
				if self.path == '/clearLogs':
					CustomLogger.clearLogs(config.sensorLogfile)
					CustomLogger.clearLogs(config.serverLogfile)
				if self.path == '/clearSensorLogs':
					CustomLogger.clearLogs(config.sensorLogfile)
				if self.path == '/clearServerLogs':
					CustomLogger.clearLogs(config.serverLogfile)

				redirectAddress = 'http://%s/status' % config.serverAddress
				self.send_response(301)
				self.send_header('Cache-Control', 'no-cache')
				self.send_header('Location', redirectAddress)
				self.end_headers()

		elif ext in self.validFileTypes:
			realFileName = self.path[1:len(self.path)]

			with open(realFileName) as file:
				self.send_response(200)
				self.send_header('Cache-Control', 'no-cache')
				try:
					self.send_header('Content-type', types_map[ext])
				except KeyError:
					self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(file.read())

		else:
			self.send_error(404)

SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(('', config.PORT), MyHandler)

def termination_handler(message):
	ThreadContainer.thread.stop()
	GpioControl.ledColor('red')
	CustomLogger.logConsole(message)
	httpd.shutdown()
	sys.exit(0)

def signal_term_handler(signal, frame):
	termination_handler('$ Unexpected termination - %s' % signal)

def signal_usr1_handler(signal, frame):
	termination_handler('$ User termination - %s' % signal)

signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGUSR1, signal_usr1_handler)

try:
	ThreadContainer.thread.start()
	GpioControl.ledColor('green')
	CustomLogger.logConsole('> Serving at port %s' % config.PORT)
	CustomLogger.logConsole('> Ready')
	httpd.serve_forever()
except KeyboardInterrupt:
	os.kill(os.getpid(), signal.SIGUSR1)
