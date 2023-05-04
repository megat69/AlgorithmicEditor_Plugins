"""
Allows for the code to be executed right in the algorithmic editor.
"""
from plugin import Plugin


class InterpreterPlugin(Plugin):
	"""
	Interpreter plugin. Executes the current code of the editor.
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


def init(app):
	return InterpreterPlugin(app)