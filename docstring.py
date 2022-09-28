from plugin import Plugin


class DocstringPlugin(Plugin):
	"""
	Plugin adding a command to add the full docstring to a function.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("d", self.add_docstring, "Docstring")


	def add_docstring(self):
		"""
		Adds the docstring to the command.
		:return:
		"""
		self.app.add_char_to_text(" \n".join(("precond", "data", "result", "desc", "vars")))


def init(app):
	return DocstringPlugin(app)
