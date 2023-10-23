import curses
import sys
import socket
import threading
import time
from functools import partial
from typing_extensions import Dict, Callable, Self
import string

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
	RECV_BASE_SIZE = (
		2
		if "--bytelen" not in sys.argv else
		int(sys.argv[sys.argv.index("--bytelen") + 1])
	)
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
				"connection_error": "Couldn't connect to the server.",
				"exam_started": "The exam has started !",
				"input_last_name": "Input your last name",
				"input_first_name": "Input your first name",
				"input_student_nbr": "Input your student number",
				"exam_over": "The exam is over ! ",
				"no_stopwatch": "Display the stopwatch"
			},
			"fr": {
				"input_ip": "Entrez l'adresse IP",
				"input_port": "Entrez le numéro du port",
				"connection_error": "Impossible de se connecter au serveur.",
				"exam_started": "L'examen a commencé !",
				"input_last_name": "Entrez votre nom de famille",
				"input_first_name": "Entrez votre prénom",
				"input_student_nbr": "Entrez votre numéro étudiant",
				"exam_over": "L'examen est terminé ! ",
				"no_stopwatch": "Afficher le compte à rebours"
			}
		}
		# Removes any stopwatch information from the CLI arguments
		if "--stopwatch" in sys.argv:
			idx = sys.argv.index("--stopwatch")
			sys.argv.pop(idx)
			sys.argv.pop(idx)  # Popping twice to remove the parameter
		# Adds the stopwatch plugin to this
		self.stopwatch_plugin = StopwatchPlugin(app)
		self._stopwatch_display_function = self.stopwatch_plugin.display

		# Remembers the current network info
		self.server_ip = None
		self.server_port = None
		self.client_started = False
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Thread-related info
		self.recv_thread_running = False
		self.recv_thread = threading.Thread(target=self.information_reception_loop)

		# Student information
		self.no_student_nbr = "--nostudent" in sys.argv
		self.student_last_name: str = ''
		self.student_first_name: str = ''
		self.student_nbr: str = ''

		# The functions handling all incoming requests
		self.received_info_functions: Dict[str, Callable[[Self, str], None]] = {
			"START_EXAM": self.handle_START_EXAM,
			"END_CONNECTION": self.handle_END_CONNECTION,
			"ADD_TO_STOPWATCH": self.handle_ADD_TO_STOPWATCH
		}

		# Additional variables
		self.show_stopwatch = True


	def init(self):
		# Inits the Stopwatch plugin
		if self.stopwatch_plugin.was_initialized is False:
			self.stopwatch_plugin.init()
			self.stopwatch_plugin.was_initialized = True
			self.stopwatch_plugin.prevent_key_input_on_stop = True

		# Removes the stopwatch option so that the student cannot change the time left
		for option in self.app.options_list.copy():
			if option[0] == self.stopwatch_plugin.translate("prevent_key_input_on_stop") or\
					option[0] == self.stopwatch_plugin.translate("enable_stopwatch"):
				self.app.options_list.remove(option)

		# Adds an option not to display the stopwatch
		self.show_stopwatch = self.get_config("show_stopwatch", True)
		self.add_option(self.translate("no_stopwatch"), lambda: self.show_stopwatch, self.toggle_stopwatch_display)
		if self.show_stopwatch is False:
			self.stopwatch_plugin.display = lambda n: None

		# Overloads the quit command to be able to close the sockets and threads in a clean manner
		self._app_default_quit = self.app.quit
		self.app.quit = self.overloaded_quit
		self.app.commands["q"] = (self.overloaded_quit, self.app.get_translation("commands", "q"), False)
		self.app.commands["q!"] = (partial(self.overloaded_quit, True), self.app.get_translation("commands"), True)
		self.app.commands["qs!"] = (partial(self.overloaded_quit, True, True), self.app.get_translation("commands", "qs!"), True)

		# Connects to the server
		self.get_student_info()
		# TODO: solid menu
		self.connect_to_server()
		print(f"Connected to server {self.server_ip} !")
		# Sends to the server the student information
		student_info_request = f"SET_STUDENT_INFO:{self.student_last_name}:{self.student_first_name}:"
		if self.no_student_nbr is False:
			student_info_request += str(self.student_nbr)
		else:
			student_info_request += "STUDENT_NBR_NONE"
		self.send_information(student_info_request.encode("utf-8"))

		# Receives the stopwatch information from the server
		temp_stopwatch_info = self.receive_information()
		print(f"Stopwatch info is now {temp_stopwatch_info}")
		# Analyzes the stopwatch information to get the value of the stopwatch
		# The stopwatch information is a string like the following example : "01:23:45"
		stopwatch_value = [int(e) for e in temp_stopwatch_info.split(':')]
		# Sets the stopwatch value to be as such, and currently inactive
		self.stopwatch_plugin.stopwatch_value = stopwatch_value
		self.stopwatch_plugin.enabled = False

		# Removes input control from the user
		self.app.input_locked = True

		# Creates a thread to receive information from the server
		self.recv_thread_running = True
		self.socket.settimeout(0.25)
		self.recv_thread.start()


	def connect_to_server(self):
		"""
		Tries to connect to the teacher's computer (server).
		"""
		menu_items = ["", "25565"]
		if "--ip" in sys.argv:
			menu_items[0] = sys.argv[sys.argv.index("--ip") + 1]
		if "--port" in sys.argv:
			menu_items[1] = sys.argv[sys.argv.index("--port") + 1]
		menu_translations = (
			self.translate("input_ip"),
			self.translate("input_port")
		)
		retry = True
		while retry:
			# Makes the user input the IP then the port
			self.app.stdscr.clear()
			key = ''
			selected_item = 0
			max_item = 2
			while key not in ('\n', "PADENTER", '\t') or selected_item != max_item:
				for i, val in enumerate(menu_items):
					self.app.stdscr.addstr(
						self.app.rows // 2 + i, 4,
						menu_translations[i] + " : " + str(menu_items[i]),
						curses.A_REVERSE if selected_item == i else curses.A_NORMAL
					)
				self.app.stdscr.addstr(
					self.app.rows // 2 + max_item, 4,
					"Done", curses.A_REVERSE if selected_item == max_item else curses.A_NORMAL
				)

				# Gets the new key
				key = self.app.stdscr.getkey()
				if key in ('\n', '\t', "PADENTER", "KEY_DOWN"):
					if (selected_item == max_item and key == "KEY_DOWN") or selected_item != max_item:
						selected_item += 1
						selected_item %= max_item + 1
				elif key == "KEY_UP":
					selected_item -= 1
					if selected_item < 0:
						selected_item = max_item
				elif key in ('\b', '\0', "KEY_BACKSPACE"):
					if selected_item != max_item:
						menu_items[selected_item] = menu_items[selected_item][:-1]
					self.app.stdscr.clear()
				elif selected_item != max_item:
					if key in string.digits + ('.' if selected_item == 0 else ''):
						menu_items[selected_item] += key


			# Validates the ip and continues to next iteration if it is not valid
			self.server_ip = menu_items[0]
			if self.server_ip.count('.') != 3 or any(len(e) > 3 or len(e) == 0 for e in self.server_ip.split('.')):
				continue
			try:
				self.server_port = int(menu_items[1])
			except ValueError:
				continue

			# Connects to the server
			try:
				self.socket.connect((self.server_ip, self.server_port))
			except ConnectionError:
				self.app.stdscr.addstr(self.app.rows // 2, 4, self.translate("connection_error"))
				self.app.stdscr.getch()
			except TimeoutError:
				self.app.stdscr.addstr(self.app.rows // 2, 4, self.translate("connection_error"))
				self.app.stdscr.getch()
			else:
				retry = False


	def get_student_info(self):
		"""
		Asks the user its student information.
		"""
		self.app.stdscr.clear()
		key = ''
		selected_item = 0
		max_menu_item = (2 + (not self.no_student_nbr))
		menu_items = [self.student_last_name, self.student_first_name, self.student_nbr]
		menu_translations = [
			self.translate("input_last_name"),
			self.translate("input_first_name"),
			self.translate("input_student_nbr")
		]
		while selected_item != max_menu_item or key not in ('\n', "PADENTER"):
			for i, val in enumerate(menu_translations):
				if self.no_student_nbr is False or i != 2:
					self.app.stdscr.addstr(
						self.app.rows // 2 + i, 4,
						val + " : " + menu_items[i],
						curses.A_REVERSE if selected_item == i else curses.A_NORMAL
					)
			self.app.stdscr.addstr(
				self.app.rows // 2 + max_menu_item, 4,
				"Done",
				curses.A_REVERSE if selected_item == max_menu_item else curses.A_NORMAL
			)

			# Gets the key input
			key = self.app.stdscr.getkey()
			if key in ('\n', '\t', "PADENTER", "KEY_DOWN"):
				if (selected_item == max_menu_item and key == "KEY_DOWN") or selected_item != max_menu_item:
					selected_item += 1
					selected_item %= max_menu_item + 1
			elif key == "KEY_UP":
				selected_item -= 1
				if selected_item < 0:
					selected_item = max_menu_item
			elif key in ('\b', '\0', "KEY_BACKSPACE"):
				if selected_item != max_menu_item:
					menu_items[selected_item] = menu_items[selected_item][:-1]
				self.app.stdscr.clear()
			elif key in string.ascii_uppercase + string.ascii_lowercase + string.digits + ' -/':
				if self.no_student_nbr is False or selected_item != 2:
					menu_items[selected_item] += key

		# Sets the student information
		self.student_last_name, self.student_first_name, self.student_nbr = menu_items


	def receive_information(self) -> str:
		"""
		Receives the amount of information required from the server.
			NOTE: It is recommended to run this function in a dedicated thread.
		:return: The data from the server as a string.
		"""
		# Reads a first two bytes of information : these contain the size of the message sent by the server
		message_size_bytes = self.socket.recv(ExamPlugin.RECV_BASE_SIZE)
		message_size = int(message_size_bytes.decode("utf-8"))

		# Now reads from the server the amount of data to be received
		server_data = self.socket.recv(message_size)

		# Decodes the data into a utf-8 string
		decoded_data = server_data.decode("utf-8")

		# Returns the data
		return decoded_data


	def send_information(self, data: bytes) -> bool:
		"""
		Sends two requests to the server : the first being 2 bytes long, and containing the amount of bytes
			contained by the second request ; the second being up to 65535 bytes long, and containing the data passed
			as parameter.
		:param data: The data to be sent to the client. Has to be UTF-8 encoded bytes !
		:return: Whether the operation was successful.
		"""
		# Sends the amount of info to the specified client
		bytes_to_send = str(len(data)).encode('utf-8')
		sent = self.socket.send(bytes_to_send)
		if sent == 0:  # If the connection didn't go through
			# Errors out
			return False

		# Sends the data to the client
		total_data_sent = 0
		while total_data_sent < len(data):
			sent = self.socket.send(data[total_data_sent:])
			if sent == 0:  # If the connection didn't go through
				# Errors out
				return False
			total_data_sent += sent

		# If this part is reached, it means that everything went well, so we return True
		return True


	def information_reception_loop(self):
		"""
		Accepts clients in a loop.
		"""
		while self.recv_thread_running:
			# Tries to receive an incoming connection from a client
			try:
				received_info = self.receive_information()

			# If no connection is established within the given timeout, we skip over to the next iteration.
			# This allows to kill the thread cleanly when the program terminates, rather than it being stuck forever.
			except socket.timeout:
				pass

			# If this condition is reached, a connection was established and we are sending the corresponding
			# information to the client.
			else:
				self.handle_received_information(received_info)

	def fixed_update(self):
		# While the clock stopwatch is disabled, we reset its time
		if self.stopwatch_plugin.enabled is False:
			self.stopwatch_plugin.start_time = int(time.time())
			self.stopwatch_plugin.end_time = (
				int(time.time()) + self.stopwatch_plugin.stopwatch_value[2] +
				self.stopwatch_plugin.stopwatch_value[1] * 60 +
				self.stopwatch_plugin.stopwatch_value[0] * 3600
			)
			self.stopwatch_plugin.display(1.0)
		elif all(value == 0 for value in self.stopwatch_plugin.stopwatch_value):
			self.stopwatch_plugin.display(1.0)
			self.app.stdscr.addstr(
				self.app.rows - 4,
				self.app.cols - 9 - len(self.translate("exam_over")),
				self.translate("exam_over"),
				curses.color_pair(self.stopwatch_plugin.low_time_left_color) | curses.A_REVERSE
			)



	def handle_received_information(self, received_info: str) -> None:
		"""
		Hands the information received from the server.
		:param received_info: Info received straight from the server.
		"""
		# Finds the header of the request and sets the body of the request
		request_header = received_info.split(':')[0]
		server_info = received_info[len(request_header)+1:]

		# Based on the request header, performs the correct operations
		try:
			self.received_info_functions[request_header](server_info)
		except KeyError:
			print(f"Unknown server request header '{request_header}'")


	def handle_START_EXAM(self, server_info: str):
		"""
		Starts the exam on this client.
		"""
		# Enables the stopwatch
		self.stopwatch_plugin.enabled = True
		# Unlocks the input and allows the user to type in the editor
		self.app.input_locked = False
		# Displays a message to warn the user that the exam is up
		self.app.stdscr.addstr(
			self.app.rows // 2,
			self.app.cols // 2 - len(self.translate("exam_started")) // 2,
			self.translate("exam_started"),
			curses.color_pair(self.stopwatch_plugin.low_time_left_color) | curses.A_REVERSE
		)


	def handle_END_CONNECTION(self, server_info: str):
		"""
		Ends the handshake with the server.
		"""
		self.send_information("END_CONNECTION:".encode("utf-8"))


	def handle_ADD_TO_STOPWATCH(self, server_info: str):
		"""
		Adds or subtracts to the stopwatch based on the server info.
		"""
		sign, hours_s, minutes_s, seconds_s = server_info.split(':')
		hours = int(hours_s)
		minutes = int(minutes_s)
		seconds = int(seconds_s)
		if sign == '+':
			multiplier = 1
		else:
			multiplier = -1
		self.stopwatch_plugin.stopwatch_value[0] += hours * multiplier
		self.stopwatch_plugin.stopwatch_value[1] += minutes * multiplier
		self.stopwatch_plugin.stopwatch_value[2] += seconds * multiplier
		self.stopwatch_plugin.end_time += (3600 * hours + 60 * minutes + seconds) * multiplier


	def overloaded_quit(self, *args, **kwargs) -> None:
		"""
		Overloads the quit command to exit the threads and sockets cleanly.
		"""
		self.recv_thread_running = False
		self.recv_thread.join()
		self.send_information("CLIENT_SHUTDOWN:".encode("utf-8"))
		self.socket.close()

		# Calls the base quit
		self._app_default_quit(*args, **kwargs)


	def toggle_stopwatch_display(self):
		self.show_stopwatch = not self.show_stopwatch
		self.config["show_stopwatch"] = self.show_stopwatch

		# Removes or adds the function of the plugin back on
		if self.show_stopwatch:
			self.stopwatch_plugin.display = self._stopwatch_display_function
		else:
			self.stopwatch_plugin.display = lambda n: None


class EmptyExamPlugin(Plugin):
	"""
	An empty plugin, so it doesn't affect anybody.
	"""
	def __init__(self, app):
		super().__init__(app, suppress_warnings=True)


def init(app):
	if "--exam" in sys.argv and STOPWATCH_PLUGIN_INSTALLED:
		return ExamPlugin(app)
	else:
		return EmptyExamPlugin(app)
