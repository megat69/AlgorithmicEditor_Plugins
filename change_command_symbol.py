from plugin import Plugin
from functools import partial


class ChangeCommandSymbol(Plugin):
	"""
	Allows the user to change the command symbol.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("?", self.change_command_symbol, "Change command symbol", True)


	def init(self):
		"""
		Loads the config and changes the command symbol to what it was last set.
		"""
		if "command_symbol" in self.config.keys():
			self.change_command_symbol(self.config["command_symbol"])
			self.app.apply_stylings()
		else:
			self.config["command_symbol"] = self.app.command_symbol


	def change_command_symbol(self, symbol:str=None):
		"""
		Changes the command symbol to whatever the user wants.
		"""
		if symbol is None:
			message = "Type the new character to change to : "
			self.app.stdscr.addstr(self.app.rows - 1, 0, message)
			key = self.app.stdscr.getkey()
		else:
			key = symbol
		if len(key) == 1 and key not in ("\n", "\b"):
			# Regenerates a whole new dict for the commands
			new_commands = {}
			for ckey, value in self.app.commands.items():
				if ckey != key:
					new_commands[ckey] = value
				else:
					new_commands[key] = (
						partial(
							self.app.add_char_to_text,
							self.app.command_symbol
						),
						self.app.command_symbol, True
					)
			self.app.commands = new_commands

			# Changes the command symbol
			self.app.command_symbol = key


			# Tells the user about the change
			if symbol is None:
				message2 = "Command character changed to : "
				self.app.stdscr.addstr(self.app.rows - 1, 0, message2 + key + (" " * (len(message) - len(message2))))
				self.app.stdscr.getch()
			# Saves the change into the config
			self.config["command_symbol"] = self.app.command_symbol


def init(app) -> ChangeCommandSymbol:
	return ChangeCommandSymbol(app)
