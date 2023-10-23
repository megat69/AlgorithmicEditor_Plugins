import curses
import sys
import socket
import time
from dataclasses import dataclass
from functools import partial
from typing_extensions import List, Optional, Tuple, Dict, Callable, Any, Self
import threading

from utils import display_menu
from plugin import Plugin

try:
	from .stopwatch import StopwatchPlugin
except ImportError:
	STOPWATCH_PLUGIN_INSTALLED = False
	print("You need to install the `stopwatch` plugin to use the exam plugin !")
else:
	STOPWATCH_PLUGIN_INSTALLED = True


@dataclass
class Student:
	last_name: Optional[str] = None
	first_name: Optional[str] = None
	student_nbr: Optional[str] = None


@dataclass
class OverwatchMode:
	is_in_overwatch: bool
	client_index: int
	data_received: Optional[dict] = None


@dataclass
class OverwatchMenuItem:
	position_y: int
	position_x: int
	text: str
	curses_formatting: int
	callback: Callable[[], Any]



class ExamTeacherPlugin(Plugin):
	SERVER_BIND = (
		"0.0.0.0"
			if "--netdeb" not in sys.argv else
		"127.0.0.1"
	)
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
				"exam_options": "-- Exam Options --",
				"change_port": "Change port : [{port}]",
				"configure_stopwatch": "Configure exam time : [{stopwatch}]",
				"start_server": "Start server",
				"ip": "IP : {ip}",
				"port": "Port : {port}",
				"server_online": "Server online !",
				"clients_connected": "({count} clients connected)",
				"open_exam_menu": "Open exam menu",
				"exam_menu": {
					"label": "Exam menu",
					"start_exam": "/!\\ Start Exam /!\\",
					"return_to_editor": "Return to editor",
					"manage_students": "Manage students"
				},
				"cancel": "Cancel",
				"client_shutdown": "{first_name} {last_name} has quit ! ({ip}, {port})",
				"client_join": "{first_name} {last_name} has joined ! ({ip}, {port})"
			},
			"fr": {
				"exam_options": "-- Options des Examens --",
				"change_port": "Changer de port : [{port}]",
				"configure_stopwatch": "Modifier le temps donné pour l'examen : [{stopwatch}]",
				"start_server": "Lancer le serveur",
				"ip": "IP : {ip}",
				"port": "Port : {port}",
				"server_online": "Serveur en ligne !",
				"clients_connected": "({count} clients connectés)",
				"open_exam_menu": "Ouvrir le menu examen",
				"exam_menu": {
					"label": "Menu Examen",
					"start_exam": "/!\\ Lancer l'examen /!\\",
					"return_to_editor": "Retourner à l'éditeur",
					"manage_students": "Gérer les étudiants"
				},
				"cancel": "Annuler",
				"client_shutdown": "{first_name} {last_name} a quitté ! ({ip}, {port})",
				"client_join": "{first_name} {last_name} a rejoint ! ({ip}, {port})"
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
		self.socket.settimeout(0.25)
		self.clients: List[Tuple[Tuple[socket, Tuple[str, int]], Student]] = []

		# Keeps in mind the server threads
		self.threads_running = True
		self.client_connection_thread = threading.Thread(target=self.accept_client_connections)
		self.client_recv_thread = threading.Thread(target=self.client_recv_all)

		# Creates the command to access the exam menu
		self.add_command("exam", self.open_exam_menu, self.translate("open_exam_menu"))

		# Additional variables
		self.exam_started = False
		self.student_overwatch_mode = OverwatchMode(False, 0, None)
		self._overwatch_menu_selected_index = 0

		# The functions handling all incoming requests
		self.received_info_functions: Dict[str, Callable[[Self, int, str, socket.socket, str, int, Student], None]] = {
			"SET_STUDENT_INFO": self.handle_SET_STUDENT_INFO,
			"CLIENT_SHUTDOWN": self.handle_CLIENT_SHUTDOWN,
			"SET_STOPWATCH": self.handle_SET_STOPWATCH,
			"END_CONNECTION": lambda *args: None
		}


	def init(self):
		# Inits the Stopwatch plugin
		if self.stopwatch_plugin.was_initialized is False:
			self.stopwatch_plugin.init()
			self.stopwatch_plugin.was_initialized = True

		# Overloads the quit command to be able to close the sockets and threads in a clean manner
		self._app_default_quit = self.app.quit
		self.app.quit = self.overloaded_quit
		self.app.commands["q"] = (self.overloaded_quit, self.app.get_translation("commands", "q"), False)
		self.app.commands["q!"] = (partial(self.overloaded_quit, True), self.app.get_translation("commands"), True)
		self.app.commands["qs!"] = (partial(self.overloaded_quit, True, True), self.app.get_translation("commands", "qs!"), True)

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
		self.socket.bind((ExamTeacherPlugin.SERVER_BIND, self.port))
		self.socket.listen(64)
		# Shows the IP and host to show the students to connect
		display_menu(
			self.app.stdscr,
			(
				(self.translate("ip", ip=self.ip), lambda: None),
				(self.translate("port", port=self.port), lambda: None)
			)
		)

		# Will start to accept clients in a loop
		self.client_connection_thread.start()
		# Will start to get client requests in a loop
		self.client_recv_thread.start()



	def accept_client_connections(self):
		"""
		Accepts clients in a loop.
		"""
		while self.threads_running:
			# Tries to receive an incoming connection from a client
			try:
				self.clients.append(
					(self.socket.accept(), Student())
				)

			# If no connection is established within the given timeout, we skip over to the next iteration.
			# This allows to kill the thread cleanly when the program terminates, rather than it being stuck forever.
			except socket.timeout:
				pass

			# If this condition is reached, a connection was established and we are sending the corresponding
			# information to the client.
			else:
				# Debug info
				print(f"Connected to a student ! IP is {self.clients[-1][0][1]}.")

				# Sending the stopwatch information to the client
				self.send_information(self.stopwatch_plugin.stopwatch_str.encode("utf-8"), len(self.clients) - 1)

				# Getting the student name info
				self.client_recv(len(self.clients) - 1)


	def client_recv_all(self):
		"""
		Receives information from each client in a loop.
		"""
		while self.threads_running:
			client_threads = [
				threading.Thread(
					target = partial(self.client_recv, i)
				)
				for i in range(len(self.clients))
			]
			for thread in client_threads:
				thread.start()
			for thread in client_threads:
				thread.join()


	def client_recv(self, client_id: int) -> None:
		"""
		Receives info from a specific client, then handles it using the appropriate function call.
		:param client_id: The index of the client in the list of clients.
		"""
		print("Running recv for", client_id)
		client_socket = self.clients[client_id][0][0]
		# Reads a first two bytes of information : these contain the size of the message sent by the server
		try:
			message_size_bytes = client_socket.recv(ExamTeacherPlugin.RECV_BASE_SIZE)
		except socket.timeout:
			return None
		message_size = int(message_size_bytes.decode("utf-8"))

		# Now reads from the server the amount of data to be received
		try:
			server_data = client_socket.recv(message_size)
		except socket.timeout:
			return None

		# Decodes the data into a utf-8 string
		decoded_data = server_data.decode("utf-8")

		# Handles the data
		self.handle_request(decoded_data, client_id)


	def handle_request(self, data: str, client_id: int) -> None:
		"""
		Acts upon the client's request.
		:param data: The data sent to the server.
		:param client_id: The index of the client in the list of clients.
		"""
		# Finds the header of the request and sets the body of the request, along with the client info
		request_header = data.split(':')[0]
		server_info = data[len(request_header)+1:]
		client_socket = self.clients[client_id][0][0]
		client_ip, client_port = self.clients[client_id][0][1]
		client_student_info = self.clients[client_id][1]

		# Hands the request
		try:
			self.received_info_functions[request_header](
				client_id, server_info, client_socket, client_ip, client_port, client_student_info
			)
		except KeyError as e:
			print(e)


	def change_port(self, in_init_display_menu: bool = False):
		"""
		Allows the user to change the port.
		"""
		# Awaits user input to change the port
		new_port = ""
		key = ''
		while key not in ('\n', "PADENTER"):
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


	def fixed_update(self):
		"""
		Updates the IP widget and student overwatch
		"""
		# Shows the IP and port in the bottom right corner of the screen
		self.ip_widget()

		# Updates based on the overwatch information
		if self.student_overwatch_mode.is_in_overwatch:
			self.send_information("GET_STOPWATCH:".encode("utf-8"))
			self.overwatch_menu()


	def ip_widget(self):
		""" Shows the IP and port in the bottom right corner of the screen """
		BASE_HEIGHT = self.app.rows - 5
		for i, msg in enumerate((
				self.translate("port", port=self.port),
				self.translate("ip", ip=self.ip),
				self.translate("clients_connected", count=len(self.clients)),
				self.translate("server_online")
		)):
			self.app.stdscr.addstr(
				BASE_HEIGHT - i,
				self.app.cols - len(msg),
				msg
			)


	def overloaded_quit(self, *args, **kwargs) -> None:
		"""
		Overloads the quit command to exit the threads and sockets cleanly.
		"""
		# Asks all the threads not to repeat running
		self.threads_running = False

		# Ends the thread accepting new clients
		self.client_connection_thread.join()

		# Tells all the clients that the connection is over
		self.send_information("END_CONNECTION:".encode("utf-8"))

		# Ends the thread accepting new requests
		self.client_recv_thread.join()

		# Closes the socket
		self.socket.close()

		# Calls the base quit
		self._app_default_quit(*args, **kwargs)


	def send_information(self, data: bytes, client_index: int = None) -> bool:
		"""
		Sends two requests to the client(s) : the first being 2 bytes long, and containing the amount of bytes
			contained by the second request ; the second being up to 65535 bytes long, and containing the data passed
			as parameter.
		:param data: The data to be sent to the client. Has to be UTF-8 encoded bytes !
		:param client_index: The index of the client to send the information to. If not specified or None,
			will send the information to EVERY connected client !
		:return: Whether the operation was successful. Be warned, this function CAN resize the
			list of connected clients !
		"""
		# Sends the info to all clients
		if client_index is None:
			all_went_well = True
			for i in range(len(self.clients)):
				all_went_well = all_went_well and self.send_information(data, i)
			return all_went_well

		# Finds the client
		client: socket.socket = self.clients[client_index][0][0]

		# Sends the amount of info to the specified client
		bytes_to_send = str(len(data)).encode('utf-8')
		sent = client.send(bytes_to_send)
		if sent == 0:  # If the connection didn't go through
			# Removes the client from the list of connected clients
			self.clients.pop(client_index)
			# Errors out
			return False

		# Sends the data to the client
		total_data_sent = 0
		while total_data_sent < len(data):
			try:
				sent = client.send(data[total_data_sent:])
			except ConnectionError:
				went_through = False
			else:
				went_through = True
			if sent == 0 or not went_through:  # If the connection didn't go through
				# Removes the client from the list of connected clients
				self.clients.pop(client_index)
				# Errors out
				return False
			total_data_sent += sent

		# If this part is reached, it means that everything went well, so we return True
		return True


	def open_exam_menu(self):
		"""
		Opens a menu with all the utilities for the exam.
		"""
		commands = []
		if self.exam_started is False:
			def start_exam():
				self.exam_started = True
				self.stopwatch_plugin.start_time = int(time.time())
				self.stopwatch_plugin.end_time = int(time.time()) + self.stopwatch_plugin.stopwatch_value[2] + \
						self.stopwatch_plugin.stopwatch_value[1] * 60 + self.stopwatch_plugin.stopwatch_value[0] * 3600
				self.stopwatch_plugin.enabled = True
				self.send_information("START_EXAM:".encode("utf-8"))
			commands.append(
				(
					self.translate("exam_menu", "start_exam"),
					start_exam
				)
			)
		commands.append(
			(
				self.translate("exam_menu", "manage_students"),
				self.manage_students
			)
		)
		commands.append(
			(
				self.translate("exam_menu", "return_to_editor"),
				lambda: None
			)
		)
		display_menu(
			self.app.stdscr,
			tuple(commands),
			label = self.translate("exam_menu", "label"),
			space_out_last_option = True,
			allow_key_input = True,
			highlight_indexes = (0,),
			highlight_pair = self.stopwatch_plugin.low_time_left_color
		)


	def get_student_name_str(self, student: Student):
		student_str = f"{student.last_name} {student.first_name}"
		if student.student_nbr is not None:
			student_str += ' ' + student.student_nbr
		return student_str


	def manage_students(self):
		"""
		Allows you to manage each student individually.
		"""
		commands = [
			(
				self.get_student_name_str(student),
				partial(self.manage_individual_student, i)
			)
			for i, (_, student) in enumerate(self.clients)
		]
		commands.append((self.translate("cancel"), lambda: None))
		display_menu(
			self.app.stdscr,
			tuple(commands),
			label = self.translate("exam_menu", "manage_students"),
			space_out_last_option = True,
			allow_key_input = True,
			align_left = True
		)


	def manage_individual_student(self, client_index: int):
		"""
		Allows to get info or change info from an individual student.
		:param client_index: The index of the client/student.
		"""
		# Asks the student for its information
		self.send_information("GET_FULL_OVERWATCH:".encode("utf-8"), client_index)

		# Keeps in mind that we are in student overwatch mode
		self.student_overwatch_mode.is_in_overwatch = True
		self.student_overwatch_mode.data_received = None
		self.student_overwatch_mode.client_index = client_index


	def overwatch_menu(self):
		"""
		Displays and updates a pretty menu for the overwatch.
		"""
		# Display config
		PADDING_TOP = 0.1
		PADDING_LEFT = 0.15

		# Base variables
		student_name = self.get_student_name_str(
			self.clients[self.student_overwatch_mode.client_index][1]
		)

		# Menu items
		menu_items: List[OverwatchMenuItem] = []
		if (self.student_overwatch_mode.data_received is not None and
				"stopwatch" in self.student_overwatch_mode.data_received):
			menu_items.append(OverwatchMenuItem(
				int(self.app.rows * PADDING_TOP) + 1,
				int(self.app.cols * PADDING_LEFT),
				self.student_overwatch_mode.data_received["stopwatch"],
				curses.A_NORMAL,
				lambda i: None
			))
		additional_stopwatch_len = 0
		for sign in "+-":
			for text, gain, pair in (
					("1 hr", [1, 0, 0], self.stopwatch_plugin.high_time_left_color),
					("1 mn", [0, 1, 0], self.stopwatch_plugin.medium_time_left_color),
					("15 sec", [0, 0, 15], self.stopwatch_plugin.low_time_left_color)
			):
				menu_items.append(OverwatchMenuItem(
					int(self.app.rows * PADDING_TOP) + 2,
					int(self.app.cols * PADDING_LEFT) + additional_stopwatch_len,
					sign + text,
					curses.color_pair(pair),
					partial(self.add_to_stopwatch, self.student_overwatch_mode.client_index, sign, gain)
				))
				additional_stopwatch_len += len(text) + 1
		menu_items.append(OverwatchMenuItem(
			int(self.app.rows * (1 - PADDING_TOP)),
			int(self.app.cols * PADDING_LEFT),
			self.translate("cancel"),
			curses.A_NORMAL,
			self.quit_overwatch
		))

		# Shows the name of the student
		self.app.stdscr.clear()
		self.app.stdscr.addstr(
			int(self.app.rows * PADDING_TOP),
			int(self.app.cols * PADDING_LEFT),
			student_name
		)

		# Displays every menu item
		for i, item in enumerate(menu_items):
			self.app.stdscr.addstr(
				item.position_y,
				item.position_x,
				item.text,
				item.curses_formatting | (curses.A_REVERSE * (i == self._overwatch_menu_selected_index))
			)

		# Gets the key
		try:
			key = self.app.stdscr.getkey()
		except curses.error:
			key = ''

		# Makes modifications based on the key
		if key in ('\n', "PADENTER"):
			menu_items[self._overwatch_menu_selected_index].callback()
		elif key in ("KEY_DOWN", "KEY_RIGHT"):
			self._overwatch_menu_selected_index += 1
			if self._overwatch_menu_selected_index > len(menu_items):
				self._overwatch_menu_selected_index -= len(menu_items)
		elif key in ("KEY_UP", "KEY_LEFT"):
			self._overwatch_menu_selected_index -= 1
			if self._overwatch_menu_selected_index < 0:
				self._overwatch_menu_selected_index += len(menu_items)


	def quit_overwatch(self):
		""" Stops overwatch """
		self.send_information("STOP_OVERWATCH".encode("utf-8"), self.student_overwatch_mode.client_index)
		self.student_overwatch_mode.is_in_overwatch = False
		self.student_overwatch_mode.data_received = None
		self.student_overwatch_mode.client_index = 0
		self._selected_index = 0


	def add_to_stopwatch(self, client_index:int, sign: str, gain: List[int]):
		"""
		Adds to the client stopwatch the given time.
		:param sign: Either '+' or '-', whether to add or subtract the gain.
		:param gain: How much to add to the stopwatch.
		"""
		self.send_information(f"ADD_TO_STOPWATCH:{sign}:{':'.join((str(e) for e in gain))}".encode("utf-8"), client_index)
		self.send_information("GET_STOPWATCH:".encode("utf-8"))


	def handle_SET_STUDENT_INFO(
			self, client_index: int, server_info: str, client_socket: socket.socket, client_ip: str,
			client_port: int, client_student_info: Student
	):
		"""
		Gets the student info from the client.
		"""
		student_info_data = server_info.split(":")
		client_student_info.last_name = student_info_data[0]
		client_student_info.first_name = student_info_data[1]
		if student_info_data[2] != "STUDENT_NBR_NONE":
			client_student_info.student_nbr = student_info_data[2]
		# Also warns the teacher a new student joined
		message = self.translate(
			"client_join",
			last_name=client_student_info.last_name,
			first_name=client_student_info.first_name,
			ip=client_ip,
			port=client_port
		)
		self.app.stdscr.addstr(
			self.app.rows // 2,
			self.app.cols // 2 - len(message) // 2,
			message,
			curses.color_pair(self.stopwatch_plugin.high_time_left_color)
		)

	def handle_SET_STOPWATCH(
			self, client_index: int, server_info: str, client_socket: socket.socket, client_ip: str,
			client_port: int, client_student_info: Student
	):
		"""
		Sets the stopwatch of the overwatch.
		"""
		if self.student_overwatch_mode.data_received is None:
			self.student_overwatch_mode.data_received = {}
		self.student_overwatch_mode.data_received["stopwatch"] = server_info


	def handle_CLIENT_SHUTDOWN(
			self, client_index: int, server_info: str, client_socket: socket.socket, client_ip: str,
			client_port: int, client_student_info: Student
	):
		"""
		When a client disconnects.
		"""
		message = self.translate(
			"client_shutdown",
			last_name=client_student_info.last_name,
			first_name=client_student_info.first_name,
			ip=client_ip,
			port=client_port
		)
		self.app.stdscr.addstr(
			self.app.rows // 2,
			self.app.cols // 2 - len(message) // 2,
			message,
			curses.color_pair(self.stopwatch_plugin.low_time_left_color) | curses.A_REVERSE
		)
		print(message)
		self.clients.pop(client_index)


class EmptyExamTeacherPlugin(Plugin):
	"""
	An empty plugin, so it doesn't affect anybody.
	"""
	def __init__(self, app):
		super().__init__(app, suppress_warnings=True)


def init(app):
	if "--examt" in sys.argv and STOPWATCH_PLUGIN_INSTALLED:
		return ExamTeacherPlugin(app)
	else:
		return EmptyExamTeacherPlugin(app)
