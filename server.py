import os
import sys
import base64
import signal
import config
import SocketServer
import getopt
from BaseHTTPServer import BaseHTTPRequestHandler
from mimetypes import types_map
from logger import CustomLogger
from omega import StoppableThread
from omega import GpioControl

class ThreadContainer:
	thread = StoppableThread()

class MyHandler(BaseHTTPRequestHandler):
	keys = {}
	sessions = {}

	def log_message(self, format, *args):
		message = '[%s] %s\n' % (self.log_date_time_string(), format%args)
		CustomLogger.log_file(message, config.server_log_file)

	def do_AUTHHEAD(self):
		self.send_response(401)
		self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def get_authenticated_user(self):
		try:
			return self.keys[self.headers.getheader('Authorization')]
		except KeyError:
			return 'Guest'

	def get_user_login_status(self):
		if self.get_authenticated_user() == 'Guest':
			return '/authenticate'
		return '/deauthenticate'

	def generate_keys(self):
		for user in config.users:
			user_key = base64.b64encode('%s:%s' % (user, config.users[user]))
			self.keys['Basic %s' % user_key] = user

	def clear_keys(self):
		self.keys = {}

	def redirect_main(self):
		redirect_address = 'http://%s' % config.domain_address
		self.send_response(301)
		self.send_header('Cache-Control', 'no-cache')
		self.send_header('Location', redirect_address)
		self.end_headers()

	def do_GET(self):
		f_name, ext = os.path.splitext(self.path)

		if self.keys == {}:
			self.generate_keys()

		if self.path in config.valid_requests:
			if self.path == '/status':
				self.send_response(200)
				self.send_header('Cache-Control', 'no-cache')
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				status_icon = 'power_settings_new' if ThreadContainer.thread.stopped() else 'done'
				html = open(config.html_file, 'a+').read()

				self.wfile.write(html % (
					self.get_user_login_status(), 
					self.get_authenticated_user(), 
					status_icon, 
					CustomLogger.read_log(config.sensor_log_file), 
					CustomLogger.read_log(config.server_log_file))
				)

			elif self.path == '/authenticate':
				if self.headers.getheader('Authorization') == None:
					self.do_AUTHHEAD()
				else:
					self.redirect_main()

			elif self.path == '/deauthenticate':
				self.clear_keys()
				self.redirect_main()

			else:
				if self.get_authenticated_user() != 'Guest':
					if self.path == '/disable':
						if not ThreadContainer.thread.stopped():
							ThreadContainer.thread.stop()
							GpioControl.led_color('blue')
					if self.path == '/enable':
						if ThreadContainer.thread.stopped():
							ThreadContainer.thread = StoppableThread()
							ThreadContainer.thread.start()
							GpioControl.led_color('off')
					if self.path == '/clearLogs':
						CustomLogger.clear_logs(config.sensor_log_file)
						CustomLogger.clear_logs(config.server_log_file)
					if self.path == '/clearSensorLogs':
						CustomLogger.clear_logs(config.sensor_log_file)
					if self.path == '/clearServerLogs':
						CustomLogger.clear_logs(config.server_log_file)

				self.redirect_main()

		elif ext in config.valid_file_types:
			real_file_name = self.path[1:len(self.path)]

			with open(real_file_name) as file:
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
http_d = SocketServer.TCPServer(('', config.PORT), MyHandler)

def termination_handler(message):
	ThreadContainer.thread.stop()
	GpioControl.led_color('red')
	CustomLogger.log_console(message)
	http_d.shutdown()
	sys.exit(0)

def signal_term_handler(signal, frame):
	termination_handler('$ Unexpected termination - %s' % signal)

def signal_usr1_handler(signal, frame):
	termination_handler('$ User termination - %s' % signal)

signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGUSR1, signal_usr1_handler)

options_passed = True

try:
	opt_list, args = getopt.getopt(sys.argv[1:], '', ['status='])
	if len(opt_list) == 0:
		options_passed = False
except getopt.GetoptError as err:
	options_passed = False

for o, a in opt_list:
	if (o == '-s') or (o == '--status'):
		if a in ['open', 'closed']:
			config.door_open = True if (a == 'open') else False
		else:
			options_passed = False
	else:
		options_passed = False

if options_passed:
	try:
		ThreadContainer.thread.start()
		GpioControl.led_color('off')
		CustomLogger.log_console('> Serving at port %s' % config.PORT)
		CustomLogger.log_console('> Ready')
		http_d.serve_forever()
	except KeyboardInterrupt:
		os.kill(os.getpid(), signal.SIGUSR1)
else:
	print 'options not passed'
