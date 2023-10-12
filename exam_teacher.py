import curses
import sys
import socket
from functools import partial

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
				"start_server": "Start server"
			},
			"fr": {
				"exam_options": "-- Options des Examens --",
				"change_port": "Changer de port : [{port}]",
				"configure_stopwatch": "Modifier le temps donné pour l'examen : [{stopwatch}]",
				"start_server": "Lancer le serveur"
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


	def init(self):
		# Inits the Stopwatch plugin
		if self.stopwatch_plugin.was_initialized is False:
			self.stopwatch_plugin.init()
			self.stopwatch_plugin.was_initialized = True


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

		# TODO Now launch the socket server
		pass


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
