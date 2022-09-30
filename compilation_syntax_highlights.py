import curses
import string

from plugin import Plugin


class CompilationSyntaxHighlights(Plugin):
	"""
	Creates a syntax highlighting during compilation.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.color_control_flow = {
			"statement": ("if", "else", "for", "while", "do"),
			"function": ("return", 'void', "using"),
			"variable": ('int', 'float', 'string', 'bool', 'char', 'std::string'),
			"instruction": ("cout", "std::cout", "cin", "std::cin")
		}


	def update_on_compilation(self, final_compiled_code:str, compilation_type:str):
		"""
		Adds a syntax highlighting during compilation.
		"""
		if "magenta" not in self.app.color_pairs:
			curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
			self.app.color_pairs["magenta"] = 7

		if compilation_type == "cpp":
			for i, line in enumerate(final_compiled_code.split("\n")):
				# Highlights for #include and preprocessor directives
				if line.startswith("#"):
					self.display(i, 0, line, curses.A_REVERSE)
					continue

				# Splits the line, and checks the first member
				splitted_line = line.split(" ")
				start_statement = splitted_line[0].replace(self.app.tab_char, "")
				if start_statement in tuple(sum(self.color_control_flow.values(), tuple())):
					if start_statement in self.color_control_flow["statement"]:
						c_pair = "statement"
					elif start_statement in self.color_control_flow["function"]:
						c_pair = "function"
					elif start_statement in self.color_control_flow["instruction"]:
						c_pair = "instruction"
					else:
						c_pair = "variable"
					self.display(i, 0, splitted_line[0], curses.color_pair(self.app.color_pairs[c_pair]))


				# Highlights the equals signs and binary operators
				for j, element in enumerate(splitted_line[1:]):
					if "=" in element or "<" in element or ">" in element:
						tab_count = line.count(self.app.tab_char)
						self.display(
							i,
							len(
								((self.app.tab_char
								if self.app.tab_char != "\t" else
								"        ") * tab_count)[:-tab_count] + \
								" ".join(splitted_line[:j+1])
							) + 1,
							element,
							curses.color_pair(self.app.color_pairs["statement"])
						)


				# Fetches individual characters
				for j, char in enumerate(line):
					if self.app.tab_char == "\t":
						j += len("       ") * line.count(self.app.tab_char)
					# Highlights curly brackets
					if char in "{};":
						self.display(i, j, char, curses.color_pair(self.app.color_pairs["statement"]))
					# Highlights parentheses
					elif char in "()":
						self.display(i, j, char, curses.color_pair(self.app.color_pairs["magenta"]))
					# Highlights digits
					elif char in string.digits:
						self.display(i, j, char, curses.color_pair(5))
					# Highlights comments
					elif char == "/":
						if line[j+1] == "/" or (self.app.tab_char == "\t"
								and line[j+1-len("       ") * line.count(self.app.tab_char)] == "/"):
							self.display(i, j, line[j-(len("       ") * line.count(self.app.tab_char)
								if self.app.tab_char == "\t" else 0):], curses.A_REVERSE)

				# Finds all quotes and highlights them in the corresponding color
				quotes_indexes = tuple(i for i, ltr in enumerate(line) if ltr == "\"")
				for j, index in enumerate(quotes_indexes):
					if j % 2 == 0:
						try:
							self.app.stdscr.addstr(
								i,
								index + (len("       ") * line.count(self.app.tab_char)
								if self.app.tab_char == "\t" else 0), line[index:quotes_indexes[j + 1] + 1],
								curses.color_pair(self.app.color_pairs["strings"] if not "=" in splitted_line[1] else 5)
							)
						except IndexError:
							if len(splitted_line) > 1:
								self.app.stdscr.addstr(
									i,
									index + (len("       ") * line.count(self.app.tab_char)
									if self.app.tab_char == "\t" else 0), line[index:],
									curses.color_pair(self.app.color_pairs["strings"] if not "=" in splitted_line[1] else 5)
								)

		elif compilation_type == "algo":
			pass


	def display(self, y, x, text, color):
		self.app.stdscr.addstr(y, x, text, color)


def init(app) -> CompilationSyntaxHighlights:
	return CompilationSyntaxHighlights(app)