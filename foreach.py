from plugin import Plugin
from algorithmic_compiler import AlgorithmicCompiler
from cpp_compiler import CppCompiler

# Tries to load the autocomplete plugin
try:
	from .autocomplete import AutocompletionPlugin
except ImportError:
	AUTOCOMPLETE_PLUGIN_LOADED = False
else:
	AUTOCOMPLETE_PLUGIN_LOADED = True


class ForeachAlgorithmicCompiler(AlgorithmicCompiler):
	"""
	Enhances the algorithmic compiler with grapic functions.
	"""
	def __init__(self, algo_compiler: AlgorithmicCompiler):
		try:
			super().__init__(
				algo_compiler.instruction_names,
				algo_compiler.var_types,
				algo_compiler.other_instructions,
				algo_compiler.stdscr,
				algo_compiler.translations,
				algo_compiler.translate_method,
				algo_compiler.tab_char
			)
		except TypeError:
			super().__init__(algo_compiler)
		self.instruction_names["foreach"] = "Pour Chaque"

	def analyze_foreach(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the foreach loop.
		"""
		self.instructions_stack.append("foreach")
		if len(instruction_params) != 3:
			self.error(f"{instruction_name} requires 3 params, got {len(instruction_params)}")
		else:
			# If the type is an array, we parse it correctly
			if instruction_params[0].startswith("arr"):
				vtype = f"Tableau[{']['.join(instruction_params[0].split('_')[2:])}] de " \
				              f"{self.var_types[instruction_params[0].split('_')[1]]}s"

			# If the type is a structure, we parse it correctly
			elif instruction_params[0].startswith("struct_"):
				vtype = f"Structure {instruction_params[0][7:]}"

			# If the param is NOT an array nor a structure
			else:
				# We add it to the params as the type, followed by the name, of whose we remove the
				# first char if it is '&' (no datar mode in algorithmic)
				vtype = self.var_types[instruction_params[0]]

			# Checks if the destination is in data/result mode
			if instruction_params[1][0] == "&":
				vname = f"{instruction_params[1][1:]} en donnée/résultat"
			else:
				vname = instruction_params[1]

			# Description of the for loop
			self.instructions_list[line_number] = f"Pour chaque élément de {instruction_params[2]} stockés dans " \
			                                      f"{vname} (type {vtype})"


class ForeachCppCompiler(CppCompiler):
	"""
	Enhances the algorithmic compiler with grapic functions.
	"""
	def __init__(self, cpp_compiler: CppCompiler):
		try:
			super().__init__(
				cpp_compiler.instruction_names,
				cpp_compiler.var_types,
				cpp_compiler.other_instructions,
				cpp_compiler.stdscr,
				cpp_compiler.app,
				cpp_compiler.use_struct_keyword
			)
		except TypeError:
			super().__init__(cpp_compiler)
		self.instruction_names = (*self.instruction_names, "foreach")


	def analyze_foreach(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the foreach loop.
		"""
		self.instructions_stack.append("foreach")
		if len(instruction_params) != 3:
			self.error(f"{instruction_name} requires 3 params, got {len(instruction_params)}")
		else:
			# If the type is an array, we parse it correctly
			if instruction_params[0].startswith("arr"):
				split_type = instruction_params[0].split("_")
				vtype = f"{self.var_types[split_type[1]]} {split_type[2]}[{']['.join(split_type[2:])}]"

			# If the type is a structure, we parse it correctly
			elif instruction_params[0].startswith("struct_"):
				vtype = "struct " * self.use_struct_keyword + f"{instruction_params[0][7:]}"

			# If the param is NOT an array nor a structure
			else:
				# We add it to the params as the type, followed by the name
				vtype = self.var_types[instruction_params[0]]

			# Description of the for loop
			self.instructions_list[line_number] = f"for ({vtype} {instruction_params[1]} : {instruction_params[2]})" + " {"


class GrapicPlugin(Plugin):
	def __init__(self, app):
		super().__init__(app)

		# Adds the foreach keyword to the instructions
		self.app.color_control_flow["statement"] = (
			*self.app.color_control_flow["statement"],
			"foreach"
		)

		# If the autocomplete plugin is loaded, we store it
		if AUTOCOMPLETE_PLUGIN_LOADED:
			self.autocomplete_plugin = AutocompletionPlugin(app)


	def init(self):
		"""
		Reloads the autocompletion if available, and adds everything to the compilers.
		"""
		# Inits the autocomplete plugin if necessary
		if AUTOCOMPLETE_PLUGIN_LOADED and not self.autocomplete_plugin.was_initialized:
			self.autocomplete_plugin.init()
			self.autocomplete_plugin.was_initialized = True

		# Tries to reload the autocomplete if it was loaded, we make sure those keywords are available to it
		if "autocomplete" in self.app.plugins:
			self.app.plugins["autocomplete"][-1].reload_autocomplete()

		# Adds all the foreach components to the compilers
		for compiler in self.app.compilers.values():
			compiler.other_instructions.append("foreach")

		# Changes the superclass from the compilers to be the current compiler class
		ForeachAlgorithmicCompiler.__bases__ = (self.app.compilers["algorithmic"].__class__,)
		ForeachCppCompiler.__bases__ = (self.app.compilers["C++"].__class__,)

		# Replaces the compilers with the enhanced compilers
		self.app.compilers["algorithmic"] = ForeachAlgorithmicCompiler(self.app.compilers["algorithmic"])
		self.app.compilers["C++"] = ForeachCppCompiler(self.app.compilers["C++"])

		# Adds the autocomplete to the plugin
		if AUTOCOMPLETE_PLUGIN_LOADED:
			self.autocomplete_plugin.documentation["foreach"] = "foreach <type> <destination_var> <source_array>"
			self.autocomplete_plugin.examples["foreach"] = ["foreach string fruit fruits"]


def init(app):
	return GrapicPlugin(app)
