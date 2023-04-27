from plugin import Plugin
from utils import input_text


class VimCommands(Plugin):
	"""
	Adds a bunch of commands taken straight from the Vim builtins for an easier time for Vim users out there.
	"""
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
				"commands": {
					"gg": {
						"name": "Navigate to start of file"
					},
					"g": {
						"name": "Navigate to line",
						"input": "Enter the line you wish to go to :"
					}
				}
			},
			"fr": {
				"commands": {
					"gg": {
						"name": "Aller au début du fichier"
					},
					"g": {
						"name": "Aller à la ligne n°...",
						"input": "Entrez le numéro de la ligne où naviguer :"
					}
				}
			}
		}
		self.add_command("gg", self.navigate_start_of_file, self.translate("commands", "gg", "name"), True)
		self.add_command("g", self.select_line, self.translate("commands", "g", "name"), True)


	def navigate_start_of_file(self):
		"""
		Navigates back to the start of file.
		"""
		self.app.current_index = 0


	def select_line(self):
		"""
		Asks the user to prompt a line to go to.
		"""
		msg_str = self.translate("commands", "gg", "input")
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