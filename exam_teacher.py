import curses
import sys
import socket
from functools import partial
from typing import List

from utils import display_menu
from plugin import Plugin

try:
	from .stopwatch import StopwatchPlugin
except ImportError:
	STOPWATCH_PLUGIN_INSTALLED = False
	print("You need to install the `stopwatch` plugin to use the exam plugin !")
else:
	STOPWATCH_PLUGIN_INSTALLED = True


class ExamTeacherPlugin(Plugin):
	def __init__(self, app):
		super().__init__(app)
		self.translations = {
			"en": {
				"exam_options": "-- Exam Options --",
				"change_port": "Change port : [{port}]",
				"configure_stopwatch": "Configure exam time : [{stopwatch}]",
				"start_server": "Start server",
				"ip": "IP : {ip}",
				"port": "Port : {port}",
				"server_online": "Server online !"
			},
			"fr": {
				"exam_options": "-- Options des Examens --",
				"change_port": "Changer de port : [{port}]",
				"configure_stopwatch": "Modifier le temps donné pour l'examen : [{stopwatch}]",
				"start_server": "Lancer le serveur",
				"ip": "IP : {ip}",
				"port": "Port : {port}",
				"server_online": "Serveur en ligne !"
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
		self.hostname = socket.gethostname()
		self.ip = socket.gethostbyname(self.hostname)
		self.port = 25565
		self.server_started = False
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients: List[socket] = []


	def init(self):
		# Inits the Stopwatch plugin
		if self.stopwatch_plugin.was_initialized is False:
			self.stopwatch_plugin.init()
			self.stopwatch_plugin.was_initialized = True

		# Shows a menu to change the port and the time left on the exam
		self.app.stdscr.clear()
		while not self.server_started:
			display_menu(
				self.app.stdscr,
				(
					(self.translate("change_port", port=self.port), partial(self.change_port, True)),
					(
						self.translate(
							"configure_stopwatch",
							stopwatch=self.stopwatch_plugin.stopwatch_str
						), self.stopwatch_plugin.enable_stopwatch
					),
					(self.translate("start_server"), partial(setattr, self, "server_started", True))
				),
				label=self.translate("exam_options"),
				clear=False
			)
			if self.stopwatch_plugin.enabled:
				self.stopwatch_plugin.enabled = False
			self.app.stdscr.clear()

		# Launches the socket server
		self.socket.bind((self.hostname, self.port))
		self.socket.listen(64)
		# Shows the IP and host to show the students to connect
		display_menu(
			self.app.stdscr,
			(
				(self.translate("ip", ip=self.ip), lambda: None),
				(self.translate("port", port=self.port), lambda: None)
			)
		)
		# TODO : Binds exactly one client for testing
		self.clients.append(self.socket.accept())
		print(self.clients[0])

	def change_port(self, in_init_display_menu: bool = False):
		"""
		Allows the user to change the port.
		"""
		# Awaits user input to change the port
		new_port = ""
		key = ''
		while key != '\n':
			# Adds a new digit if a number is inputted
			if key.isdigit():
				new_port += key

			# If the key is backspace, we remove the last unit
			elif key in ("\b", "\0"):
				new_port = new_port[:-1]

			# If the key is the delete key, we delete the whole port number
			elif key == "KEY_DC":
				new_port = ""

			# Makes the display
			translation = self.translate("change_port", port=new_port)
			self.app.stdscr.addstr(
				self.app.rows // 2,
				self.app.cols // 2 - len(translation) + len(new_port),
				translation + " " * 5
			)
			self.app.stdscr.addstr(
				self.app.rows // 2,
				self.app.cols // 2 - len(translation) + translation.find('[') + len(new_port),
				f"[{new_port}]",
				curses.A_REVERSE
			)

			# Awaits a new key input
			key = self.app.stdscr.getkey()

		# If the number is below 1024 or above 65535, we error out and launch the function again
		new_port_int = int(new_port)
		if new_port_int <= 1024 or new_port_int > 65535:
			self.change_port()
		else:
			self.port = new_port_int


	def update_on_keypress(self, key: str):
		# Shows the IP and port in the bottom right corner of the screen
		self.app.stdscr.addstr(
			self.app.rows - 4,
			self.app.cols - len(self.translate("port", port=self.port)),
			self.translate("port", port=self.port)
		)
		self.app.stdscr.addstr(
			self.app.rows - 5,
			self.app.cols - len(self.translate("ip", ip=self.ip)),
			self.translate("ip", ip=self.ip)
		)

		self.app.stdscr.addstr(
			self.app.rows - 6,
			self.app.cols - len(self.translate("server_online")),
			self.translate("server_online")
		)



class EmptyExamTeacherPlugin(Plugin):
	"""
	An empty plugin, so it doesn't affect anybody.
	"""
	def __init__(self, app):
		super().__init__(app)


def init(app):
	if "--examt" in sys.argv and STOPWATCH_PLUGIN_INSTALLED:
		return ExamTeacherPlugin(app)
	else:
		return EmptyExamTeacherPlugin(app)
