from plugin import Plugin
from utils import display_menu


class CommandPalette(Plugin):
	"""
	Lets the user search through each of the available commands and find the correct one for your needs.
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
				"command_palette": "Command palette"
			},
			"fr": {
				"command_palette": "Palette de commandes"
			}
		}
		self.add_command("cp", self.command_palette, self.translate("command_palette"), True)
		self.bind_control('p', "cp")  # Binds CTRL+P to open the command palette


	def command_palette(self):
		"""
		Pulls out the command palette.
		"""
		commands = [
			(f"{self.app.command_symbol}{key_name} - {name}", function)
			for i, (key_name, (function, name, hidden)) in enumerate(self.app.commands.items())
			if key_name != self.app.command_symbol and function != self.command_palette
		]
		commands.append((self.app.get_translation("cancel"), lambda: None))
		display_menu(
			self.app.stdscr,
			tuple(commands),
			label = self.translate("command_palette"),
			space_out_last_option = True,
			allow_key_input = True
		)


	def update_on_keypress(self, key: str):
		"""
		Binds the F3 key to the command palette.
		"""
		# Evaluates if the key is F3
		if key == "KEY_F(3)":
			# Opens the command palette
			self.command_palette()


def init(app):
	return CommandPalette(app)
