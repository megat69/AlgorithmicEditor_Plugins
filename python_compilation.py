from plugin import Plugin
from compiler import Compiler


class PythonCompiler(Compiler):
	def __init__(self, instruction_names:tuple, var_types:dict, other_instructions:tuple, stdscr, app):
		super().__init__(instruction_names, var_types, other_instructions, stdscr, app.tab_char)

		# Use vars
		self.app = app


	def ifsanitize(self, string:str) -> str:
		"""
		Sanitizes the conditions in an if statement.
		"""
		return string.replace('ET', 'and').replace('OU', 'or').replace('NON', 'not')


	def analyze_const(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes a constant """
		self.instructions_list[line_number] = "{} : {} {}  # Constant".format(
			instruction_params[1],
			instruction_params[0],
			' '.join(instruction_params[2:])
		)


	def define_var(self, instruction:list, line_number:int):
		""" Defines a variable """
		# Gets the type of the variable
		var_type = self.var_types[instruction[0]]

		# Gets the name of the variables
		variable_names = instruction[1:]

		# Creates the line, with None as many times as it exists variable names
		if len(variable_names) > 1:
			# We create multiple vars at once if there are multiple vars
			self.instructions_list[line_number] = ", ".join(variable_names) + " = " + ", ".join(
				"None" for _ in range(len(variable_names))
			)
		# Otherwise, we add the type to the variable
		else:
			self.instructions_list[line_number] = f"{variable_names[0]} : {var_type} = None"


	def analyze_for(self, instruction_name:str, instruction_params:list, line_number:int):
		""" for i in range(0, n, 1): """
		self.instructions_stack.append("for")
		# Creates the loop's body
		self.instructions_list[line_number] = "for {var} in range({min}, {max}{step}):".format(
			var = instruction_params[0],
			min = instruction_params[1],
			max = instruction_params[2],
			step = (", " + instruction_params[3] if len(instruction_params) > 3 else "")
		)


	def analyze_end(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes the end block """
		# Pops the element at the end of the stack and stores it in a variable
		last_elem = self.instructions_stack.pop()
		# And nothing more because it's Python, that's all we have to do
		self.instructions_list[line_number] = ""


	def analyze_while(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes the while loop """

		self.instructions_stack.append("while")
		# Rewrites the line for the while loop
		self.instructions_list[line_number] = f"while {self.ifsanitize(' '.join(instruction_params))}:"


	def analyze_if(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes the given if statement """
		self.instructions_stack.append("if")
		# Rewrites the line
		self.instructions_list[line_number] = f"if {self.ifsanitize(' '.join(instruction_params))}:"


	def analyze_else(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Else statement """
		self.instructions_list[line_number] = "else:"

	def analyze_elif(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Elif statement """
		self.instructions_list[line_number] = f"elif {self.ifsanitize(' '.join(instruction_params))}"


	def analyze_switch(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Switch statement """
		self.instructions_stack.append("switch")
		# Rewrites the line
		self.instructions_list[line_number] = f"match {' '.join(instruction_params)}:"


	def analyze_case(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Case statement """
		# If there is no switch in the instruction stack, we error out to the user
		if "switch" not in self.instructions_stack:
			self.error(f"Error on line {line_number + 1} : 'case' statement outside of a 'switch'.")

		# If there is no error, we continue
		else:
			self.instructions_stack.append("case")
			self.instructions_list[line_number] = f"case {' '.join(instruction_params)}:"


	def analyze_default(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Default statement """
		# If there is no switch in the instruction stack, we error out to the user
		if "switch" not in self.instructions_stack:
			self.error(f"Error on line {line_number + 1} : 'default' statement outside of a 'switch'.")

		# If there is no error, we continue
		else:
			self.instructions_stack.append("default")
			self.instructions_list[line_number] = "case _:"


	def analyze_print(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Print statement """
		# Creates the string to print
		string_to_print = ' '.join(instruction_params)

		# Turns all & into ,
		string_to_print = string_to_print.replace(' & ', ', ')

		# Rewrites the string
		self.instructions_list[line_number] = f"print({string_to_print}, sep='', end='')"


	def analyze_input(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Input statement """
		# Creates an input statement with a try except block and eval to get the correct value. Bad code, but it works.
		self.instructions_list[line_number] = f"{' '.join(instruction_params)} = input('')\n" +\
				                                self.app.tab_char * ((len(self.instructions_stack) + ('fx' not in self.instructions_stack))) +\
				                                "try:\n" +\
												self.app.tab_char * ((len(self.instructions_stack) + ('fx' not in self.instructions_stack)) + 1) +\
												f"{' '.join(instruction_params)} = eval({' '.join(instruction_params)})\n" +\
												self.app.tab_char * ((len(self.instructions_stack) + ('fx' not in self.instructions_stack))) +\
												f"except Exception: pass"


	def analyze_precond(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Préconditions : elements """
		self.instructions_list[line_number] = f"# Préconditions : {' '.join(instruction_params)}"


	def analyze_data(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Données : elements """
		self.instructions_list[line_number] = f"# Données : {' '.join(instruction_params)}"


	def analyze_datar(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Donnée/Résultat : elements """
		self.instructions_list[line_number] = f"# Donnée/Résultat : {' '.join(instruction_params)}"


	def analyze_result(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Résultat : elements """
		self.instructions_list[line_number] = f"# Résultat : {' '.join(instruction_params)}"


	def analyze_desc(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Description : elements """
		self.instructions_list[line_number] = f"# Description : {' '.join(instruction_params)}"


	def analyze_return(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Return statement """
		# Checks we're not in a procedure
		if "proc" in self.instructions_stack:
			self.error(f"Error on line {line_number + 1} : 'return' statement in a procedure.")

		# Checks we're inside a function
		elif "fx" not in self.instructions_stack:
			self.error(f"Error on line {line_number + 1} : 'return' statement outside of a function.")

		# Writes the line correctly
		else:
			self.instructions_list[line_number] = f"return {' '.join(instruction_params)}"


	def analyze_vars(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Removes it """
		self.instructions_list[line_number] = f"# Variables locales : {' '.join(instruction_params)}"


	def analyze_fx_start(self, instruction_name:str, instruction_params:list, line_number:int):
		""" fx_start statement """
		# Basically clears the line because not needed
		self.instructions_list[line_number] = ""


	def analyze_arr(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Arrays """
		try:
			# We construct the array size
			arr_sizes = "{}"
			for i in range(2, len(instruction_params)):
				arr_sizes = arr_sizes.format("[{}] * {SIZE}".format("{}", SIZE=instruction_params[i]))
			arr_sizes = arr_sizes.format("0")

			# Building the final line
			self.instructions_list[line_number] = f"{instruction_params[1]} = {arr_sizes}"

		# If the statement does not have all its parameters set
		except IndexError:
			self.error(f"Error on line {line_number + 1} : 'arr' statement does not have all its parameters set")


	def analyze_fx(self, instruction_name:str, instruction_params:list, line_number:int):
		""" Analyzes a function """
		# Prevents a crash when extra spaces are at the end of the line
		while instruction_params[-1] == "": instruction_params.pop()

		# Function to handle the parameters, whether they are arrays or standard variables
		def handle_params(instruction_params):
			# The list of parameters
			params = []

			# Fetches each parameter (going two by two, because each param goes <type> <name>)
			for i in range(2, len(instruction_params), 2):
				# Adds the parameter to the list of parameters
				params.append(f"{instruction_params[i + 1]}: ")

				# Try block in case there is an IndexError
				try:
					# If the param is NOT an array
					if not instruction_params[i].startswith("arr"):
						# We add it to the params as the type, followed by the name, of whose we remove the
						# first char if it is '&' (no datar mode in algorithmic)
						params[-1] += self.var_types[instruction_params[i]][instruction_params[i][0] == '&':]

					# If the param is an array, we parse it correctly
					else:
						params[-1] += "list"

				# If an IndexError is encountered, we remove the last param from the params list and continue
				except IndexError:
					params.pop()

			# We merge back the params and return them
			params = ", ".join(params)
			return params

		# Getting the parameters string
		params = handle_params(instruction_params)

		# Branching on whether it is a procedure or a function
		if instruction_params[0] != "void":
			self.instructions_stack.append("fx")
			# We write the line as a function
			self.instructions_list[line_number] = f"def {instruction_params[1]}({params}) -> {self.var_types[instruction_params[0]]}:"

		else:  # Procedure
			self.instructions_stack.append("proc")
			# We write the line as a procedure
			self.instructions_list[line_number] = f"def {instruction_params[1]}({params}) -> None:"


	def final_trim(self, instruction_name:str, line_number:int):
		""" Formats the line a bit more """
		# Adds the end of line
		self.instructions_list[line_number] = self.instructions_list[line_number].replace("(ENDL)", "\\n")

		# Adds the power, sqrt, and rand functions
		for algo_function, python_function in (
				("puissance(", "pow("),
				("racine(", "sqrt("),
				("aleatoire(", "rand(")
		):
			self.instructions_list[line_number] = self.instructions_list[line_number].replace(
				algo_function,
				python_function
			)

		# Adds the correct tabbing (amount of tabs is equal to amount of instructions in the instructions stack,
		# minus one if the current instruction is in the instruction names)
		tab_amount = len(self.instructions_stack)
		if instruction_name in (*self.instruction_names, "else", "elif", "proc"):
			tab_amount -= 1

		# Replaces double-slashes by # symbol for comments
		self.instructions_list[line_number] = self.instructions_list[line_number].replace("//", "#")

		# Writes the line
		self.instructions_list[line_number] = self.app.tab_char * tab_amount + self.instructions_list[line_number]


	def final_touches(self):
		""" Concatenates everything into one string """
		final_compiled_code = ""

		# If we use sqrt, we import math
		if "racine(" in self.app.current_text:
			final_compiled_code += "from math import sqrt\n"

		# If we use random, we import random.random
		if "racine(" in self.app.current_text:
			final_compiled_code += "from random import random\n"

		# Adding a newline
		if final_compiled_code != "":
			final_compiled_code += "\n"

		# Adds the main code into the compiled code
		final_compiled_code += "\n".join(self.instructions_list)

		# Adds a final blank line
		final_compiled_code += "\n"

		return final_compiled_code


class CompileToPython(Plugin):
	"""
	Compiles the code to Python when using a command.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.python_compiler = PythonCompiler(
			('for', 'if', 'while', 'switch', 'case', 'default', 'else', 'elif', 'fx'),
			{"int": "int", "float": "float", "string": "str", "bool": "bool", "char": "str"},
			("print", "input", "end", "elif", "else", "fx_start", "vars", "data", "datar", "result", "return", "desc", "const", "arr"),
			self.app.stdscr, self.app
		)
		self.add_command("y", self.compile_to_python, "Compile to Python")

	def compile_to_python(self):
		"""
		Compiles everything to python code ; might not always work.
		"""
		self.app.instructions_list = self.app.current_text.split("\n")

		final_compiled_code = self.python_compiler.compile(self.app.instructions_list)

		self.app.stdscr.clear()
		self.app.stdscr.refresh()
		self.app.stdscr.addstr(final_compiled_code)
		for plugin in self.app.plugins.values():
			if hasattr(plugin[1], "update_on_compilation"):
				plugin[1].update_on_compilation(final_compiled_code, "python")
		self.app.stdscr.getch()
		self.app.save(final_compiled_code)
		self.app.stdscr.clear()
		self.app.apply_stylings()
		self.app.stdscr.refresh()


def init(app):
	return CompileToPython(app)