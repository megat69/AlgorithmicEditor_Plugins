import curses
import sys
import socket
import threading
import time
from functools import partial

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
				"connection_error": "Couldn't connect to the server.",
				"exam_started": "The exam has started !",
				"input_last_name": "Input your last name",
				"input_first_name": "Input your first name",
				"input_student_nbr": "Input your student number"
			},
			"fr": {
				"input_ip": "Entrez l'adresse IP",
				"input_port": "Entrez le numéro du port",
				"connection_error": "Impossible de se connecter au serveur.",
				"exam_started": "L'examen a commencé !",
				"input_last_name": "Entrez votre nom de famille",
				"input_first_name": "Entrez votre prénom",
				"input_student_nbr": "Entrez votre numéro étudiant"
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

		# Thread-related info
		self.recv_thread_running = False
		self.recv_thread = threading.Thread(target=self.information_reception_loop)

		# Student information
		self.no_student_nbr = "--nostudent" in sys.argv
		self.student_last_name: str = None
		self.student_first_name: str = None
		self.student_nbr: str = None


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
		self.send_information(
			student_info_request.encode("utf-8")
		)

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


	def get_student_info(self):
		"""
		Asks the user its student information.
		"""
		self.app.stdscr.clear()
		self.app.stdscr.addstr(self.app.rows // 2, 4, self.translate("input_last_name") + " : ")
		self.student_last_name = input_text(self.app.stdscr, 4 + len(self.translate("input_last_name")) + 3, self.app.rows // 2)
		self.app.stdscr.addstr(self.app.rows // 2 + 1, 4, self.translate("input_first_name") + " : ")
		self.student_first_name = input_text(self.app.stdscr, 4 + len(self.translate("input_first_name")) + 3, self.app.rows // 2 + 1)
		if self.no_student_nbr is False:
			self.app.stdscr.addstr(self.app.rows // 2 + 2, 4, self.translate("input_student_nbr") + " : ")
			self.student_nbr = input_text(self.app.stdscr, 4 + len(self.translate("input_student_nbr")) + 3, self.app.rows // 2 + 2)


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



	def handle_received_information(self, received_info: str) -> None:
		"""
		Hands the information received from the server.
		:param received_info: Info received straight from the server.
		"""
		# Finds the header of the request and sets the body of the request
		request_header = received_info.split(':')[0]
		server_info = received_info[len(request_header)+1:]

		# Based on the request header, performs the correct operations
		if request_header == "START_EXAM":  # Starts the exam
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

		elif request_header == "END_CONNECTION":  # Ends the connection with the server
			self.send_information("END_CONNECTION:".encode("utf-8"))

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
