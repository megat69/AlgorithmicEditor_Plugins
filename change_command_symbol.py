from plugin import Plugin
from functools import partial


class ChangeCommandSymbol(Plugin):
	"""
	Allows the user to change the command symbol.
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

		# Sets up the translation
		self.translations = {
			"en": {
				"change_command_symbol": "Change command symbol",
				"type_new_char": "Type the new character to change to : ",
				"symbol_changed_to": "Command character changed to : "
			},
			"fr": {
				"change_command_symbol": "Changer le symbole de commande",
				"type_new_char": "Tapez le nouveau caractère vers lequel changer : ",
				"symbol_changed_to": "Caractère de commande modifié vers : "
			}
		}

		# Creates a command
		self.add_option(
			self.translate("change_command_symbol"),
			lambda: repr(self.app.command_symbol),
			self.change_command_symbol
		)


	def init(self):
		"""
		Loads the config and changes the command symbol to what it was last set.
		"""
		self.change_command_symbol(self.get_config("command_symbol", self.app.command_symbol))
		self.app.apply_stylings()


	def change_command_symbol(self, symbol:str=None):
		"""
		Changes the command symbol to whatever the user wants.
		"""
		if symbol is None:
			message = self.translate("type_new_char")
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
				message2 = self.translate("symbol_changed_to")
				self.app.stdscr.addstr(self.app.rows - 1, 0, message2 + key + (" " * (len(message) - len(message2))))
				self.app.stdscr.getch()
			# Saves the change into the config
			self.config["command_symbol"] = self.app.command_symbol


def init(app) -> ChangeCommandSymbol:
	return ChangeCommandSymbol(app)
