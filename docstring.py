from plugin import Plugin
from utils import input_text


class DocstringPlugin(Plugin):
	"""
	Plugin adding a command to add the full docstring to a function.
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
		self.docstring_components = ("precond", "data", "datar", "result", "desc", "vars")
		self.add_command("d", self.add_docstring, "Docstring")
		self.app.color_control_flow["instruction"] = (
			*self.app.color_control_flow["instruction"],
			*self.docstring_components
		)


	def init(self):
		"""
		Reloads the autocompletion if available.
		"""
		# Tries to reload the autocomplete if it was loaded, we make sure those keywords are available to it
		if "autocomplete" in self.app.plugins:
			self.app.plugins["autocomplete"][-1].reload_autocomplete()

	def add_docstring(self):
		"""
		Adds the docstring to the text.
		"""
		for component in self.docstring_components:
			if component != "vars":
				self.app.stdscr.addstr(self.app.rows - 3, 0, component + " " * 10)
				contents = input_text(self.app.stdscr)
				if contents != "":
					self.app.add_char_to_text(component + " " + contents + "\n")
			else:
				self.app.add_char_to_text(component + "\n")


	def update_on_syntax_highlight(self, line:str, splitted_line:list, i:int):
		"""
		Updates the highlighting of the docstring components.
		"""
		pass


def init(app):
	return DocstringPlugin(app)
