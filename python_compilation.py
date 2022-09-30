from plugin import Plugin


class CompileToPython(Plugin):
	"""
	Compiles the code to Python when using a command.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("y", self.compile_to_python, "Compile to Python")

	def compile_to_python(self):
		"""
		Compiles everything to python code ; might not always work.
		"""
		self.app.instructions_list = self.app.current_text.split("\n")
		instructions_stack = []
		names = ('for', 'if', 'while', 'switch', 'case', 'default', 'else', 'elif')
		ifsanitize = lambda s: s.replace('ET', 'and').replace('OU', 'or').replace('NON', 'not')
		var_types = {"int": "int", "float": "float", "string": "str", "bool": "bool", "char": "str"}
		fxtext = []
		last_elem = None

		for i, line in enumerate(self.app.instructions_list):
			line = line.split(" ")
			instruction_name = line[0]
			instruction_params = line[1:]

			if instruction_name in var_types.keys():
				var_type = var_types[instruction_name]
				for i in range(len(instruction_params)):
					self.app.instructions_list[i] = instruction_params[i] + " : " + var_type + " = None\n"

			elif instruction_name == "for":
				instructions_stack.append("for")
				self.app.instructions_list[i] = f"for {instruction_params[0]} in range({instruction_params[1]}, " +\
				                            instruction_params[2] + ("" if len(instruction_params) < 4 else f", {instruction_params[3]}") +\
				                            f"):"

			elif instruction_name == "end":
				last_elem = instructions_stack.pop()
				self.app.instructions_list[i] = ""

			elif instruction_name == "while":
				instructions_stack.append("while")
				self.app.instructions_list[i] = f"while {ifsanitize(' '.join(instruction_params))}:"

			elif instruction_name == "if":
				instructions_stack.append("if")
				self.app.instructions_list[i] = f"if {ifsanitize(' '.join(instruction_params))}:"

			elif instruction_name == "else":
				self.app.instructions_list[i] = "else:"

			elif instruction_name == "elif":
				self.app.instructions_list[i] = f"elif {ifsanitize(' '.join(instruction_params))}:"

			elif instruction_name == "switch":
				instructions_stack.append("switch")
				self.app.instructions_list[i] = f"match {' '.join(instruction_params)}:"

			elif instruction_name == "case":
				if "switch" not in instructions_stack:
					self.app.stdscr.clear()
					self.app.stdscr.addstr(0, 0, f"Error on line {i + 1} : 'case' statement outside of a 'match'.")
					self.app.stdscr.getch()
					return None
				instructions_stack.append("case")
				self.app.instructions_list[i] = f"case {' '.join(instruction_params)}:"

			elif instruction_name == "default":
				instructions_stack.append("default")
				self.app.instructions_list[i] = "case _:"

			elif instruction_name == "print":
				self.app.instructions_list[i] = f"print({' '.join(instruction_params).replace(' & ', ', ')}, end='', sep='')"

			elif instruction_name == "input":
				self.app.instructions_list[i] = f"{' '.join(instruction_params)} = input('')\n" +\
				                                self.app.tab_char * ((len(instructions_stack) + ('fx' not in instructions_stack))) +\
				                                "try:\n" +\
												self.app.tab_char * ((len(instructions_stack) + ('fx' not in instructions_stack)) + 1) +\
												f"{' '.join(instruction_params)} = eval({' '.join(instruction_params)})\n" +\
												self.app.tab_char * ((len(instructions_stack) + ('fx' not in instructions_stack))) +\
												f"except Exception: pass"


			elif instruction_name == "fx":
				while instruction_params[-1] == "": instruction_params.pop()
				instructions_stack.append("fx")
				try:
					params = tuple(f"{instruction_params[i + 1]} : {var_types[instruction_params[i]]}" for i in
					               range(2, len(instruction_params), 2))
					params = ", ".join(params)
					if instruction_params[0] != "void":
						self.app.instructions_list[i] = f"def {instruction_params[1]}({params}) -> {var_types[instruction_params[0]]}:"
					else:
						self.app.instructions_list[i] = f"def {instruction_params[1]}({params}) -> None:"
					del params
				except KeyError:
					pass

			elif instruction_name == "precond":
				self.app.instructions_list[i] = f"# Préconditions : {' '.join(instruction_params)}"
			elif instruction_name == "data":
				self.app.instructions_list[i] = f"# Données : {' '.join(instruction_params)}"
			elif instruction_name == "result":
				self.app.instructions_list[i] = f"# Résultats : {' '.join(instruction_params)}"
			elif instruction_name == "desc":
				self.app.instructions_list[i] = f"# Description : {' '.join(instruction_params)}"
			elif instruction_name == "vars":
				self.app.instructions_list[i] = f"# Variables locales : {' '.join(instruction_params)}"
			elif instruction_name == "fx_start":
				self.app.instructions_list[i] = ""
			elif instruction_name == "return":
				# Checks we're not in a procedure
				if "proc" in instructions_stack:
					self.app.stdscr.clear()
					self.app.stdscr.addstr(0, 0, f"Error on line {i + 1} : 'return' statement in a procedure.")
					self.app.stdscr.getch()
					return None
				# Checks we're inside a function
				elif "fx" not in instructions_stack:
					self.app.stdscr.clear()
					self.app.stdscr.addstr(0, 0, f"Error on line {i + 1} : 'return' statement outside of a function.")
					self.app.stdscr.getch()
					return None
				else:
					self.app.instructions_list[i] = f"return {' '.join(instruction_params)}"

			elif len(instruction_params) != 0:
				if instruction_params[0].endswith("="):
					self.app.instructions_list[i] = f"{instruction_name} {' '.join(instruction_params)}"

			self.app.instructions_list[i] = self.app.instructions_list[i].replace("puissance(", "pow(").replace("racine(",
			                                                                                            "sqrt(")
			self.app.instructions_list[i] = self.app.instructions_list[i].replace("aleatoire(", "random(")
			self.app.instructions_list[i] = self.app.instructions_list[i].replace("(ENDL)", "\\n")
			self.app.instructions_list[i] = self.app.tab_char * (
						len(instructions_stack) - (1 if instruction_name in (*names, "fx") else 0)) \
			                            + self.app.instructions_list[i]

			if "fx" in instructions_stack or (instruction_name == "end" and last_elem == "fx"):
				fxtext.append(self.app.instructions_list[i])
				if instruction_name == "end":
					fxtext[-1] += "\n"
				self.app.instructions_list[i] = ""

			if self.app.instructions_list[i].replace(self.app.tab_char, "").startswith("string"):
				self.app.instructions_list[i] = ""

		final_compiled_code = ("from random import random" if 'aleatoire(' in self.app.current_text else '') + "\n" + \
		                      "\n".join(fxtext) + "\n\nif __name__ == '__main__':\n" \
		                      + "".join(
			self.app.tab_char + instruction + "\n" for instruction in self.app.instructions_list if instruction != "" and instruction.split(" ")[0] not in var_types.keys())

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