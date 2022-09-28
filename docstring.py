from plugin import Plugin


class DocstringPlugin(Plugin):
	"""
	Plugin adding a command to add the full docstring to a function.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.docstring_components = ("precond", "data", "result", "desc", "vars")
		self.add_command("d", self.add_docstring, "Docstring")
		self.app.color_control_flow["instruction"] = (
			*self.app.color_control_flow["instruction"],
			*self.docstring_components
		)

	def add_docstring(self):
		"""
		Adds the docstring to the text.
		"""
		self.app.add_char_to_text(" \n".join(self.docstring_components))

	def update_on_syntax_highlight(self, line:str, splitted_line:list, i:int):
		"""
		Updates the highlighting of the docstring components.
		"""
		pass


def init(app):
	return DocstringPlugin(app)
