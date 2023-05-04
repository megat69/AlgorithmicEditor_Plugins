"""
Allows for the code to be executed right in the algorithmic editor.
"""
from dataclasses import dataclass
from typing import Union

from plugin import Plugin

############# LITERALS #############
@dataclass
class IntLiteral:
	value: int

@dataclass
class FloatLiteral:
	value: float

@dataclass
class StringLiteral:
	value: str

@dataclass
class VarLookup:  # When you need to look up a variable
	name: str


############# STATEMENTS #############
@dataclass
class PrintStatement:
	args: list  # All the arguments of the statement, being split by the '&' symbol



############# AST PARSER #############
class ASTParser:
	"""
	Creates an abstract syntax tree of the given code.
	"""
	def __init__(self, stdscr, code: str):
		"""
		:param code: A piece of algorithmic code.
		"""
		self.stdscr = stdscr
		self.code = code


	def parse(self) -> Union[list, str]:
		"""
		Creates and returns a syntax tree of the given code.
		:return: Returns the AST as a list or the error message as a string.
		"""
		tree = []
		last_pointer = tree

		# Goes line by line to decode the code
		for i, line in enumerate(self.code.split("\n")):
			# Skips the line if empty
			if line == "": continue

			# Splits the line for analysis
			splitted_line = line.split(" ")

			# Tests if the line is a print statement
			if splitted_line[0] == "print":
				pass

			# If the keyword does not correspond to anything we know, we error out
			else:
				return self.error(i, "NameError", f"Unknown keyword : {repr(splitted_line[0])}.")

		return tree


	def error(self, lineno: int, error_type: str, message: str = "") -> str:
		"""
		Errors out and kills the program.
		:param lineno: The line number where the error occurred.
		:param error_type: The error type.
		:param message: An optional message to describe the error.
		"""
		self.stdscr.clear()
		message_str = f"{error_type} on line {lineno + 1}"
		if message:
			message_str += f" : {message}"
		self.stdscr.addstr(0, 0, message_str)
		return message_str


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