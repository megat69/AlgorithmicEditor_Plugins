import curses
from fast_autocomplete import AutoComplete

from plugin import Plugin


class AutocompletionPlugin(Plugin):
	"""
	Adds autocompletion capabilities to the editor.
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
				"toggled_auto_add_space": "Toggled auto add space to {state} ",
				"documentation_enabled": "Autocomplete documentation",
				"examples_enabled": "Autocomplete examples",
				"examples": "Examples(s) :"
			},
			"fr": {
				"autocomplete_cmd": "Activer/Désactiver l'ajout d'espace post-autocomplétion",
				"toggled_auto_add_space": "Basculé l'ajout automatique d'espaces vers {state} ",
				"documentation_enabled": "Documentation d'autocomplétion",
				"examples_enabled": "Examples d'autocomplétion",
				"examples": "Exemples(s) :"
			}
		}

		# Initializes documentations for each of the base types
		self.documentation = {}

		# Creates option to toggle documentation
		self.documentation_enabled = True
		self.add_option(
			self.translate("documentation_enabled"),
			lambda: self.documentation_enabled,
			self.toggle_documentation_enabled
		)

		# Initializes examples for each of the base types
		self.examples = {}

		# Creates an option to toggle examples
		self.examples_enabled = True
		self.add_option(
			self.translate("examples_enabled"),
			lambda: self.examples_enabled,
			self.toggle_examples_enabled
		)

		# Variable to determine whether to add a space after autocompletion or not
		self.auto_add_space = False
		self.add_option(self.translate("autocomplete_cmd"), lambda: self.auto_add_space, self.toggle_auto_add_space)


	def init(self):
		"""
		Gets the config for the plugin (creates it if non-existent).
		"""
		self.auto_add_space = self.get_config("auto_add_space", self.auto_add_space)

		# Defining as color pair for the autocomplete the default curses color
		self.app.color_pairs["autocomplete"] = 255

		# Creates documentations for each of the base types
		self.documentation = {
			"fx": "fx <type|void> <name> [[type1] [arg1]] [[type2] [arg2]] [...]",
			"arr": "arr <type> <name> <dimension1> [dimension2] [dimension3] [...]",
			"print": "print <variables or constants separated by '&' symbols>",
			"input": "input <var1>",
			"for": "for <var> <min> <max> [step=1]",
			"while": "while <condition>",
			"if": "if <condition>",
			"elif": "elif <condition>",
			"else": "else",
			"CODE_RETOUR": "CODE_RETOUR <return_code>",
			"switch": "switch <char|int>",
			"case": "case <char|int>",
			"struct": "struct <name> [[attr_type1] [attr_name1]] [[attr_type2] [attr_name2]] [...]",
			"init": "init <struct_name> <var_name> [[arg_name1] [arg_val1]] [[arg_name2] [arg_val2]] [...]",
			"return": "return <value|expression|variable>",
			**{
				var_type: f"{var_type} <name1> [[= <value>] OR [[name2] [name3] [...]]"
				for var_type in self.app.compilers["C++"].var_types
			}
		}

		self.documentation_enabled = self.get_config("documentation_enabled", self.documentation_enabled)

		# Creates the examples for each of the base types
		self.examples = {
			"fx": [
				"fx void greet string name",
				"fx int sum int a int b"
			],
			"arr": [
				"arr string fruits 5",
				"arr int grid 3 3"
			],
			"print": ["print \"Hello \" & name & \" !(ENDL)\""],
			"input": ["input name"],
			"for": [
				"for i 1 10",
				"for odds 1 20 2"
			],
			"while": [
				"while !finished"
			],
			"if": [
				"if i % 2 == 0"
			],
			"elif": [
				"elif tests > 15"
			],
			"else": ["else"],
			"CODE_RETOUR": [
				"CODE_RETOUR 0",
				"CODE_RETOUR -1",
			],
			"switch": [
				"switch color"
			],
			"case": [
				"case 0",
				"case 'b'"
			],
			"struct": [
				"struct Flower int price string name"
			],
			"init": [
				"init Flower flower price 5 name \"Rose\""
			],
			"return": [
				"return val",
				"return 0",
				"return a + b"
			],
			**{
				var_type: [
					f"{var_type} a b c d",
					f"{var_type} a = RR"
				]
				for var_type in self.app.compilers["C++"].var_types
			}
		}

		self.examples_enabled = self.get_config("examples_enabled", self.examples_enabled)


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
		if self.app.cur[1] - self.app.get_lineno_length() <= len(splitted_line[0]):
			self.ac = self.autocomplete.search(splitted_line[0], size=1)

			# If a word was autocompleted
			if len(self.ac) != 0:
				try:
					# Shows the autocomplete results on the screen
					try:
						self.app.stdscr.addstr(
							self.app.cur[0],
							self.app.cur[1],
							self.ac[0][0][len(splitted_line[0])-1:]
								if self.documentation_enabled is False
								or self.documentation.get(self.ac[0][0]) is None
								else
							self.documentation[self.ac[0][0]][len(splitted_line[0])-1:],
							curses.color_pair(self.app.color_pairs["autocomplete"]) | curses.A_ITALIC
						)

						# If the examples are enabled, shows each example
						if self.examples_enabled and self.examples.get(self.ac[0][0]) is not None:
							self.app.stdscr.addstr(
								self.app.cur[0] + 1,
								self.app.cur[1] + 1,
								self.translate("examples"),
								curses.A_ITALIC
							)
							for i, example in enumerate(self.examples[self.ac[0][0]]):
								self.app.stdscr.addstr(
									self.app.cur[0] + 2 + i,
									self.app.cur[1] + 1,
									example,
									curses.A_ITALIC
								)
					except KeyError: pass
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


	def toggle_documentation_enabled(self):
		"""
		Toggles whether the documentation should be enabled when autocompleting.
		"""
		self.documentation_enabled = not self.documentation_enabled


	def toggle_examples_enabled(self):
		"""
		Toggles whether the documentation examples should be enabled when autocompleting.
		"""
		self.examples_enabled = not self.examples_enabled


def init(app) -> AutocompletionPlugin:
	return AutocompletionPlugin(app)

