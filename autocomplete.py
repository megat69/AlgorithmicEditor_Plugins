import curses
from fast_autocomplete import AutoComplete

from plugin import Plugin


class AutocompletionPlugin(Plugin):
	def __init__(self, app):
		super().__init__(app)
		# Creating all the words which can be autocompleted
		self.words = self.load_words()
		# Initializing the autocomplete
		self.autocomplete = AutoComplete(words=self.words)

		# Creates an autocomplete variable
		self.ac = None

		# Determines the plugin translation
		self.translations = {
			"en": {
				"autocomplete_cmd": "Autocomplete Toggle Auto Add Space",
				"toggled_auto_add_space": "Toggled auto add space to {state} "
			},
			"fr": {
				"autocomplete_cmd": "Activer/Désactiver l'ajout d'espace post-autocomplétion",
				"toggled_auto_add_space": "Basculé l'ajout automatique d'espaces vers {state} "
			}
		}

		# Variable to determine whether to add a space after autocompletion or not
		self.auto_add_space = False
		self.add_option(self.translate("autocomplete_cmd"), lambda: self.auto_add_space, self.toggle_auto_add_space)


	def init(self):
		"""
		Gets the config for the plugin (creates it if non-existent).
		"""
		if "auto_add_space" in self.config:
			self.auto_add_space = self.config["auto_add_space"]
		else:
			self.config["auto_add_space"] = self.auto_add_space

		# Creating a curses color pair for the autocomplete if it doesn't exist
		if "autocomplete" not in self.app.color_pairs.keys():
			curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
			self.app.color_pairs["autocomplete"] = 6

	def update_on_keypress(self, key:str):
		"""
		Remembers the last pressed key by the user.
		"""
		# If the key is a tab, we remove it and add the autocompletion
		if self.ac is not None and key in ("KEY_STAB", "\t"):
			self.app.current_text = self.app.current_text[:self.app.current_index - 1] \
			                        + self.app.current_text[self.app.current_index:]
			self.app.current_index -= 1
			# Adding the autocompleted words to the text
			self.app.add_char_to_text(self.ac[0][0][len(self.ac[1]):] + " " * self.auto_add_space)

		# Updates the word list, in case any plugins adds syntax highlighting on the go
		for e in self.app.color_control_flow.values():
			for element in e:
				if element not in self.words.keys():
					self.words[element] = {}


	def update_on_syntax_highlight(self, line:str, splitted_line:list, i:int):
		"""
		Uses the update method to put the autocompletion on cursor position.
		"""
		# If the cursor exists and we are on the cursor line
		if self.app.cur != tuple() and self.app.cur[1] - (len(str(self.app.lines)) + 1) <= len(splitted_line[0]):
			self.ac = self.autocomplete.search(splitted_line[0], size=1)

			# If a word was autocompleted
			if len(self.ac) != 0:
				try:
					# Shows the autocomplete results on the screen
					self.app.stdscr.addstr(
						self.app.cur[0],
						self.app.cur[1],
						self.ac[0][0][len(splitted_line[0])-1:],
						curses.color_pair(self.app.color_pairs["autocomplete"]) | curses.A_ITALIC
					)
				except curses.error:
					self.ac = None
					return
				self.ac.append(splitted_line[0])
			else:
				self.ac = None


	def toggle_auto_add_space(self):
		"""
		Toggles whether to automatically add a space after the autocompletion.
		"""
		# Toggles the automatic addition of a space upon autocompletion
		self.auto_add_space = not self.auto_add_space
		# Shows a message to the user indicating the state of the variable
		self.app.stdscr.addstr(self.app.rows - 1, 4, self.translate(
			"toggled_auto_add_space",
			state=self.auto_add_space
		))
		# Saving the variable's contents in the config
		self.config["auto_add_space"] = self.auto_add_space


	def load_words(self):
		"""
		Loads all the words available for autocomplete.
		"""
		return {
			element: {} for e in self.app.color_control_flow.values() for element in e
		}


	def reload_autocomplete(self):
		"""
		Reloads the autocomplete.
		"""
		self.words = self.load_words()
		self.autocomplete = AutoComplete(words=self.words)


def init(app) -> AutocompletionPlugin:
	return AutocompletionPlugin(app)

