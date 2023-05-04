"""
Allows for the code to be executed right in the algorithmic editor.
"""
from dataclasses import dataclass

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
		self.translations = {
			"en": {
				"run_command": "Run code"
			},
			"fr": {
				"run_command": "Exécuter le code"
			}
		}
		# Creates the interpretion command
		self.add_command("run", self.launch_interpreter, self.translate("run_command"))


	def launch_interpreter(self):
		"""
		Launches the interpretion.
		"""
		# Starts by building an AST of the code
		pass


def init(app):
	return InterpreterPlugin(app)