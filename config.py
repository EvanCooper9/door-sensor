server_address = 'server_ip'
domain_address = 'door.evancooper.tech'
PORT = 9920
archive_log_prefix = 'logs/archive/'
sensor_log_file = 'logs/sensor_log.txt'
server_log_file = 'logs/server_log.txt'
html_file = 'html/index.html'
users = {'usr':'psw'}
door_open = False

valid_requests = [
	'/',
	'/help', 
	'/status', 
	'/disable', 
	'/enable', 
	'/clearLogs', 
	'/clearSensorLogs', 
	'/clearServerLogs',
	'/authenticate',
	'/deauthenticate'
]

valid_file_types = [
	'.js', 
	'.css', 
	'.woff2', 
	'.woff', 
	'.ttf', 
	'.json'
]
