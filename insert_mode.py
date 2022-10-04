from plugin import Plugin


class InsertModePlugin(Plugin):
	"""
	Adds a command to toggle the insert mode.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.insert_mode_enabled = False
		self.add_command("i", self.toggle_insert_mode, "Insert")


	def toggle_insert_mode(self):
		"""
		Toggles the insert mode.
		"""
		self.insert_mode_enabled = not self.insert_mode_enabled
		self.app.stdscr.addstr(self.app.rows - 1, 4, f"Toggled insert mode to {self.insert_mode_enabled} ")


def init(app):
	return InsertModePlugin(app)