import curses

from plugin import Plugin


class InsertModePlugin(Plugin):
	"""
	Adds a command to toggle the insert mode.
	"""
	def __init__(self, app):
		super().__init__(app)

		# Sets up the translations
		self.translations = {
			"en": {
				"insert": "Insert",
				"toggled_insert_mode": "Toggled insert mode to {state} "
			},
			"fr": {
				"insert": "Insérer",
				"toggled_insert_mode": "Bascule du mode d'insertion sur {state} "
			}
		}

		# Initializes the variable indicating whether the insert mode is enabled
		self.insert_mode_enabled = False
		# Adds the command to toggle the insert mode
		self.add_command("i", self.toggle_insert_mode, self.translate("insert"))

		# Assigns the regular add_char_to_text function to a variable
		self._regular_add_char_to_text = self.app.add_char_to_text
		# Replaces the add_char_to_text function with a custom one
		self.app.add_char_to_text = self._add_char_to_text

		# Assigns the regular display_text function to a variable
		self._regular_display_text = self.app.display_text
		# Replaces the display_text function with a custom one
		self.app.display_text = self._display_text


	def toggle_insert_mode(self):
		"""
		Toggles the insert mode.
		"""
		# Toggles insert mode
		self.insert_mode_enabled = not self.insert_mode_enabled
		# Shows a message to the user indicating the current state of the variable
		self.app.stdscr.addstr(self.app.rows - 1, 4, self.translate(
			"toggled_insert_mode",
			state = self.insert_mode_enabled
		))


	def _add_char_to_text(self, key:str):
		"""
		Adds the given character to the text if the insert mode is disabled, or inserts if enabled.
		:param key: The character to be inserted.
		"""
		# If insert mode is disabled, we just use the regular function
		if self.insert_mode_enabled is False:
			self._regular_add_char_to_text(key)

		# If insert mode is enabled, we fetch each character from 'key' and replace the current one with this new character
		else:
			for character in key:
				self.app.current_text = self.app.current_text[:self.app.current_index] + character + self.app.current_text[self.app.current_index+1:]
				self.app.current_index += 1


	def _display_text(self):
		"""
		Highlights the cursor in red if we are in insert mode.
		"""
		# Displays the text
		self._regular_display_text()

		# If insert mode is enabled, displays the cursor in red
		if self.insert_mode_enabled and self.app.cur is not None:
			try:
				self.app.stdscr.addstr(*self.app.cur, curses.A_REVERSE | curses.color_pair(1))
			except curses.error:
				pass


def init(app):
	return InsertModePlugin(app)