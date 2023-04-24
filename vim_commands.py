from plugin import Plugin
from utils import input_text


class VimCommands(Plugin):
	"""
	Adds a bunch of commands taken straight from the Vim builtins for an easier time for Vim users out there.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("gg", self.navigate_start_of_file, "Navigate to start of file", True)
		self.add_command("g", self.select_line, "Navigate to line", True)


	def navigate_start_of_file(self):
		"""
		Navigates back to the start of file.
		"""
		self.app.current_index = 0


	def select_line(self):
		"""
		Asks the user to prompt a line to go to.
		"""
		msg_str = "Enter the line you wish to go to :"
		self.app.stdscr.addstr(
			self.app.rows // 2 - 1,
			self.app.cols // 2 - len(msg_str) // 2,
			msg_str
		)
		line = input_text(self.app.stdscr, self.app.cols // 2 - 1, self.app.rows // 2)

		# Tries to convert the given line into a number
		try:
			line = int(line) - 1
		except ValueError:
			return None

		# Clamps the line number to the existing lines
		text = self.app.current_text + "\n"
		indexes = tuple(index for index in range(len(text)) if text.startswith('\n', index))
		line = max(min(line, len(indexes) - 1), 0)

		# Gets the user to the given line
		self.app.current_index = indexes[line]



def init(app):
	return VimCommands(app)