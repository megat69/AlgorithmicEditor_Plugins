from plugin import Plugin


class InsertModePlugin(Plugin):
	"""
	Adds a command to toggle the insert mode.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.insert_mode_enabled = False
		self.add_command("i", self.toggle_insert_mode, "Insert")
		self._regular_add_char_to_text = self.app.add_char_to_text
		self.app.add_char_to_text = self._add_char_to_text


	def toggle_insert_mode(self):
		"""
		Toggles the insert mode.
		"""
		self.insert_mode_enabled = not self.insert_mode_enabled
		self.app.stdscr.addstr(self.app.rows - 1, 4, f"Toggled insert mode to {self.insert_mode_enabled} ")


	def _add_char_to_text(self, key:str):
		"""
		Adds the given character to the text if the insert mode is disabled, or inserts if enabled.
		:param key: The character to be inserted.
		"""
		if self.insert_mode_enabled is False:
			self._regular_add_char_to_text(key)
		else:
			for character in key:
				self.app.current_text = self.app.current_text[:self.app.current_index] + character + self.app.current_text[self.app.current_index+1:]
				self.app.current_index += 1


def init(app):
	return InsertModePlugin(app)