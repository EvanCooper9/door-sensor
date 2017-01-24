import os

class CustomLogger:
	@staticmethod
	def logFile(content, destination):
		data = open(destination, 'a+').read()
		sequence = (content, data)

		file = open(destination, 'w')
		file.write(''.join(sequence))
		file.close()

	@staticmethod
	def logConsole(content):
		print content

	@staticmethod
	def readLog(log):
		data = open(log, 'a+').read()
		return data

	@staticmethod
	def clearLogs(log):
		os.remove(log)