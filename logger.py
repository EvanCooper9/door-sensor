import os
import config
import datetime

class CustomLogger:
	@staticmethod
	def log_file(content, destination):
		data = open(destination, 'a+').read()
		sequence = (content, data)

		file = open(destination, 'w')
		file.write(''.join(sequence))
		file.close()

	@staticmethod
	def log_console(content):
		print content

	@staticmethod
	def read_log(log):
		data = open(log, 'a+').read()
		return data

	@staticmethod
	def clear_logs(log):
		# backup rather than delete
		time = str(datetime.datetime.now())[:-10].replace(' ', '_').replace(':', '-')
		dir_path = str(os.path.dirname(os.path.realpath(__file__)))
		path = dir_path + config.archive_log_prefix + time + '.txt'
		os.rename(log, path)