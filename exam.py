import sys
import socket
import time

from plugin import Plugin
from utils import display_menu, input_text

try:
	from .stopwatch import StopwatchPlugin
except ImportError:
	STOPWATCH_PLUGIN_INSTALLED = False
	print("You need to install the `stopwatch` plugin to use the exam plugin !")
else:
	STOPWATCH_PLUGIN_INSTALLED = True


class ExamPlugin(Plugin):
	__singleton = None

	def __new__(cls, *args, **kwargs):
		"""
		Creates a singleton of the class.
		"""
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)
		return cls.__singleton



	def __init__(self, app):
		super().__init__(app)
		self.translations = {
			"en": {
				"input_ip": "Input the IP",
				"input_port": "Input the port",
				"connection_error": "Couldn't connect to the server."
			},
			"fr": {
				"input_ip": "Entrez l'adresse IP",
				"input_port": "Entrez le numéro du port",
				"connection_error": "Impossible de se connecter au serveur."
			}
		}
		# Removes any stopwatch information from the CLI arguments
		if "--stopwatch" in sys.argv:
			idx = sys.argv.index("--stopwatch")
			sys.argv.pop(idx)
			sys.argv.pop(idx)  # Popping twice to remove the parameter
		# Adds the stopwatch plugin to this
		self.stopwatch_plugin = StopwatchPlugin(app)

		# Remembers the current network info
		self.server_ip = None
		self.server_port = None
		self.client_started = False
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Additional variables
		self.stopwatch_enabled = False


	def init(self):
		# Inits the Stopwatch plugin
		if self.stopwatch_plugin.was_initialized is False:
			self.stopwatch_plugin.init()
			self.stopwatch_plugin.was_initialized = True

		# Connects to the server
		# TODO: solid menu
		self.connect_to_server()
		print(f"Connected to server {self.server_ip} !")

		# Receives the stopwatch information from the server
		temp_stopwatch_info = self.receive_information()
		print(f"Stopwatch info is now {temp_stopwatch_info}")
		# Analyzes the stopwatch information to get the value of the stopwatch
		# The stopwatch information is a string like the following example : "01:23:45"
		stopwatch_value = [int(e) for e in temp_stopwatch_info.split(':')]
		# Sets the stopwatch value to be as such, and currently inactive
		self.stopwatch_plugin.stopwatch_value = stopwatch_value
		self.stopwatch_plugin.enabled = True

		# Removes input control from the user
		self.app.input_locked = True


	def connect_to_server(self):
		"""
		Tries to connect to the teacher's computer (server).
		"""
		retry = True
		while retry:
			# Makes the user input the IP then the port
			self.app.stdscr.clear()
			self.app.stdscr.addstr(self.app.rows // 2, 4, self.translate("input_ip") + " : ")
			self.server_ip = input_text(self.app.stdscr, 4 + len(self.translate("input_ip")) + 3, self.app.rows // 2)
			self.app.stdscr.addstr(self.app.rows // 2, 4, self.translate("input_port") + " : ")
			self.server_port = int(
				input_text(self.app.stdscr, 4 + len(self.translate("input_port")) + 3, self.app.rows // 2)
			)

			# Connects to the server
			try:
				self.socket.connect((self.server_ip, self.server_port))
			except ConnectionError:
				self.app.stdscr.addstr(self.app.rows // 2, 4, self.translate("connection_error"))
				self.app.stdscr.getch()
			else:
				retry = False


	def receive_information(self) -> str:
		"""
		Receives the amount of information required from the server.
			NOTE: It is recommended to run this function in a dedicated thread.
		:return: The data from the server as a string.
		"""
		# Reads a first two bytes of information : these contain the size of the message sent by the server
		message_size_bytes = self.socket.recv(2)
		message_size = int(message_size_bytes.decode("utf-8"))

		# Now reads from the server the amount of data to be received
		server_data = self.socket.recv(message_size)

		# Decodes the data into a utf-8 string
		decoded_data = server_data.decode("utf-8")

		# Returns the data
		return decoded_data


	def fixed_update(self):
		# While the clock stopwatch is disabled, we reset its time
		# self.stopwatch_plugin.fixed_update()
		if self.stopwatch_enabled is False:
			self.stopwatch_plugin.start_time = int(time.time())
			self.stopwatch_plugin.end_time = (
				int(time.time()) + self.stopwatch_plugin.stopwatch_value[2] +
				self.stopwatch_plugin.stopwatch_value[1] * 60 +
				self.stopwatch_plugin.stopwatch_value[0] * 3600
			)


class EmptyExamPlugin(Plugin):
	"""
	An empty plugin, so it doesn't affect anybody.
	"""
	def __init__(self, app):
		super().__init__(app)


def init(app):
	if "--exam" in sys.argv and STOPWATCH_PLUGIN_INSTALLED:
		return ExamPlugin(app)
	else:
		return EmptyExamPlugin(app)
