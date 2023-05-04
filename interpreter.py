"""
Allows for the code to be executed right in the algorithmic editor.
"""
from dataclasses import dataclass
from typing import Union, Optional

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
		self.code: str = code
		self.has_errored: bool = False
		self.error_message: Optional[str] = None


	def parse(self) -> Union[list, str]:
		"""
		Creates and returns a syntax tree of the given code.
		:return: Returns the AST as a list or the error message as a string.
		"""
		tree = []
		last_pointer = tree

		# Goes line by line to decode the code
		for i, line in enumerate(self.code.split("\n")):
			if self.has_errored: return self.error_message
			# Skips the line if empty
			if line == "": continue

			# Splits the line for analysis
			splitted_line = line.split(" ")

			# Tests if the line is a print statement
			if splitted_line[0] == "print":
				self._analyze_print(last_pointer, line, i)

			# If the keyword does not correspond to anything we know, we error out
			else:
				return self._error(i, "NameError", f"Unknown keyword : {repr(splitted_line[0])}.")

		return tree


	def _analyze_print(self, last_pointer: list, line: str, lineno: int):
		"""
		Adds the analysis of the print function to the AST.
		"""
		# Starts by creating a list of arguments for the print statement
		args_list = [None]

		# Analyzes each of the arguments one by one
		in_string = False
		for char in line[6:]: # Starting at 6 so we remove the "print" and the whitespace after it
			# Starts a new string if not in string but with a '"' character
			if not in_string and char == '"':
				in_string = True
				current_literal = StringLiteral("")

			# Ends the string if in string with a '"' character
			elif in_string and char == '"':
				in_string = False
				if args_list[-1] is not None:
					return self._error(lineno, "ArgumentError", "Missing argument separation in print statement")
				args_list[-1] = current_literal

			# Otherwise if in string, we just add the character to the string litteral
			elif in_string:
				current_literal.value += char

			# If we have another argument, we add to the list of arguments
			if not in_string:
				# Creating a new slot for an argument
				if char == '&':
					args_list.append(None)

			#TODO Ints, floats, and var lookups

		# Errors out if there is any NoneType in the list of arguments
		if any(arg is None for arg in args_list):
			return self._error(lineno, "ArgumentError", "Some arguments are not defined")

		# Adds a new print statement to the AST
		last_pointer.append(
			PrintStatement(args_list)
		)


	def _error(self, lineno: int, error_type: str, message: str = "") -> str:
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
		self.stdscr.refresh()
		self.stdscr.getch()
		self.stdscr.clear()
		self.has_errored = True
		self.error_message = message_str
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
		ast_parser = ASTParser(self.app.stdscr, self.app.current_text)
		tree = ast_parser.parse()
		print(tree)


def init(app):
	return InterpreterPlugin(app)