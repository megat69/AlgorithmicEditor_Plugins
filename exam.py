import sys
import socket

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


	def init(self):
		# Inits the Stopwatch plugin
		if self.stopwatch_plugin.was_initialized is False:
			self.stopwatch_plugin.init()
			self.stopwatch_plugin.was_initialized = True

		# Connects to the server
		# TODO: solid menu
		self.connect_to_server()


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
