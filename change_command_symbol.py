from plugin import Plugin
from functools import partial


class ChangeCommandSymbol(Plugin):
	"""
	Allows the user to change the command symbol.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("?", self.change_command_symbol, "Change command symbol", True)


	def change_command_symbol(self):
		"""
		Changes the command symbol to whatever the user wants.
		"""
		message = "Type the new character to change to : "
		self.app.stdscr.addstr(self.app.rows - 1, 0, message)
		key = self.app.stdscr.getkey()
		if len(key) == 1 and key not in ("\n", "\b"):
			del self.app.commands[self.app.command_symbol]
			# Changes the command symbol
			self.app.command_symbol = key
			# Changes the command allowing the user to type the command symbol into the text
			self.app.commands[self.app.command_symbol] = (
				partial(
					self.app.add_char_to_text,
					self.app.command_symbol
				),
				self.app.command_symbol, True
			)
			# Tells the user about the change
			message2 = "Command character changed to : "
			self.app.stdscr.addstr(self.app.rows - 1, 0, message2 + key + (" " * (len(message) - len(message2))))
			self.app.stdscr.getch()


def init(app) -> ChangeCommandSymbol:
	return ChangeCommandSymbol(app)
