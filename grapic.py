from typing_extensions import Callable

from plugin import Plugin
from algorithmic_compiler import AlgorithmicCompiler
from cpp_compiler import CppCompiler


translations = {
	"en": {
		"error": {
			"param_number": "Error on line {line_number} : {instruction_name} method requires {nb_params} params, got {given_params_nb}",
			"no_winit": "Error on line {line_number} : Called {instruction_name} method before winit.",
			"winit_finished_string": "Error on line {line_number} : expected finished string as winit first param"
		}
	},
	"fr": {
		"error": {
			"param_number": "Erreur à la ligne {line_number} : la fonction {instruction_name} requiert {nb_params} paramètres, n'en a reçu que {given_params_nb}",
			"no_winit": "Erreur à la ligne {line_number} : la fonction {instruction_name} a été apprelée avant winit.",
			"winit_finished_string": "Erreur à la ligne {line_number} : une chaîne de caractères finie était attendue comme premier paramètre de winit"
		}
	}
}




class GrapicAlgorithmicCompiler(AlgorithmicCompiler):
	"""
	Enhances the algorithmic compiler with grapic functions.
	"""
	def __init__(self, algo_compiler: AlgorithmicCompiler, tr_method: Callable):
		try:
			super().__init__(
				algo_compiler.instruction_names,
				{**algo_compiler.var_types, "image": "Image"},
				algo_compiler.other_instructions,
				algo_compiler.stdscr,
				algo_compiler.translations,
				algo_compiler.translate_method,
				algo_compiler.app,
				algo_compiler.tab_char
			)
		except TypeError:
			super().__init__(algo_compiler)
		# Keeps track of whether we initialized the window already (cannot use any other function prior to this)
		self.did_winit = False
		# Keeps in mind the translate method
		self.translate = tr_method


	def prepare_new_compilation(self):
		super().prepare_new_compilation()
		self.did_winit = False




	def final_trim(self, instruction_name:str, line_number:int):
		super().final_trim(instruction_name, line_number)
		for algo_function, equivalent in (
			("wdisplay(", "AfficherFenêtre("),
			("etime(", "TempsÉcoulé("),
		):
			self.instructions_list[line_number] = self.instructions_list[line_number].replace(algo_function, equivalent)


	def analyze_winit(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winInit method.
		"""
		# Puts the string back together
		if instruction_params[0].startswith("\""):
			try:
				while not instruction_params[0].endswith("\""):
					instruction_params[0] += " " + instruction_params.pop(1)
			except IndexError:
				self.error(self.translate("error", "winit_finished_string", line_number=line_number+1))

		# Creates the function compilation
		if len(instruction_params) != 3:
			self.error(
				self.translate("error", "param_number", line_number=line_number+1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
			)
			#self.error(f"Error on line {line_number + 1} : winit method requires 3 params, got {len(instruction_params)}")
		else:
			self.instructions_list[line_number] = f"Initialisation de la fenêtre avec pour nom {instruction_params[0]}," \
			                                      f" largeur {instruction_params[1]}, et hauteur {instruction_params[2]}"
			self.did_winit = True


	def analyze_wclear(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winClear method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number+1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "Effaçage de la fenêtre"


	def analyze_wdisplay(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winDisplay method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "Affichage de la fenêtre"


	def analyze_wquit(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winQuit method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "Fermeture de la fenêtre"


	def analyze_color(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the color method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Changement de la couleur vers ({', '.join(instruction_params)})"


	def analyze_bcolor(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the backgroundColor method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Changement de la couleur d'arrière plan vers ({', '.join(instruction_params)})"


	def analyze_pspace(self, instruction_name: str, instruction_params: list, line_number: int):
		"""
		Analyzes the pressSpace method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "Attente d'un appui sur Espace de l'utilisateur"


	def analyze_circle(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the circle method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Trace un cercle de centre ({instruction_params[0]}, " \
				                                      f"{instruction_params[1]}) et de rayon {instruction_params[2]}"


	def analyze_circlef(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the circleFill method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Trace un cercle REMPLI de centre ({instruction_params[0]}, " \
				                                      f"{instruction_params[1]}) et de rayon {instruction_params[2]}"


	def analyze_line(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the line method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 4:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=4, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Trace une ligne de ({', '.join(instruction_params[:2])}) à ({', '.join(instruction_params[2:])})"


	def analyze_rect(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the rectangle method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 4:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=4, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Trace un rectangle de ({', '.join(instruction_params[:2])}) à ({', '.join(instruction_params[2:])})"


	def analyze_rectf(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the rectangleFill method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 4:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=4, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Trace un rectangle REMPLI de ({', '.join(instruction_params[:2])}) à ({', '.join(instruction_params[2:])})"

	def analyze_ppixel(self, instruction_name: str, instruction_params: list, line_number: int):
		"""
		Analyzes the put_pixel method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) < 5 or len(instruction_params) > 6:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params="5/6", given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Pose un pixel sur la fenêtre aux coordonnées " \
				                                      f"({', '.join(instruction_params[:2])}) avec une couleur" \
				                                      f" ({', '.join(instruction_params[2:])})"


	def analyze_delay(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the delay method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 1:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=1, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"Attendre {instruction_params[0]} ms"


	def analyze_img(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the image method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) > 2 and instruction_params[-2]  in ("->", "<-"):
				self.instructions_list[line_number] = f"Charge l'image au chemin {' '.join(instruction_params[:-2])} dans la variable {instruction_params[-1]}"
			else:
				self.instructions_list[line_number] = f"Charge l'image au chemin {' '.join(instruction_params)}"


class GrapicCppCompiler(CppCompiler):
	"""
	Enhances the algorithmic compiler with grapic functions.
	"""
	def __init__(self, cpp_compiler: CppCompiler, tr_method: Callable):
		try:
			super().__init__(
				cpp_compiler.instruction_names,
				{**cpp_compiler.var_types, "image": "Image"},
				cpp_compiler.other_instructions,
				cpp_compiler.stdscr,
				cpp_compiler.app,
				cpp_compiler.use_struct_keyword
			)
		except TypeError:
			super().__init__(cpp_compiler)
		# Keeps track of whether we initialized the window already (cannot use any other function prior to this)
		self.did_winit = False
		# Keeps in mind the translation function
		self.translate = tr_method


	def prepare_new_compilation(self):
		super().prepare_new_compilation()
		self.did_winit = False


	def final_trim(self, instruction_name:str, line_number:int):
		super().final_trim(instruction_name, line_number)
		for algo_function, cpp_equivalent in (
			("wdisplay(", "winDisplay("),
			("etime(", "elapsedTime("),
		):
			self.instructions_list[line_number] = self.instructions_list[line_number].replace(algo_function, cpp_equivalent)



	def final_touches(self):
		"""
		Adds the grapic import and namespace before iostream.
		"""
		final_compiled_code = super().final_touches()
		if self.did_winit:
			final_compiled_code = "#include <Grapic.h>\nusing namespace grapic;\n" + final_compiled_code
		return final_compiled_code


	def analyze_winit(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winInit method.
		"""
		# Puts the string back together
		if instruction_params[0].startswith("\""):
			try:
				while not instruction_params[0].endswith("\""):
					instruction_params[0] += " " + instruction_params.pop(1)
			except IndexError:
				self.error(self.translate("error", "winit_finished_string", line_number=line_number+1))

		# Creates the function compilation
		if len(instruction_params) != 3:
			self.error(
				self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
			)
		else:
			self.instructions_list[line_number] = f"winInit({', '.join(instruction_params)})"
			self.did_winit = True


	def analyze_wclear(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winClear method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "winClear()"


	def analyze_wdisplay(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winDisplay method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "winDisplay()"


	def analyze_wquit(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the winQuit method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "winQuit()"


	def analyze_color(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the color method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"color({', '.join(instruction_params)})"


	def analyze_bcolor(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the backgroundColor method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"backgroundColor({', '.join(instruction_params)})"


	def analyze_pspace(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the pressSpace method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			self.instructions_list[line_number] = "pressSpace()"


	def analyze_circle(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the circle method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"circle({', '.join(instruction_params)})"


	def analyze_circlef(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the circleFill method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 3:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=3, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"circleFill({', '.join(instruction_params)})"


	def analyze_line(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the line method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 4:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=4, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"line({', '.join(instruction_params)})"


	def analyze_rect(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the rectangle method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 4:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=4, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"rectangle({', '.join(instruction_params)})"


	def analyze_rectf(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the rectangleFill method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 4:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=4, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"rectangleFill({', '.join(instruction_params)})"


	def analyze_ppixel(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the put_pixel method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) < 5 or len(instruction_params) > 6:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params="5/6", given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"put_pixel({', '.join(instruction_params)})"


	def analyze_delay(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the delay method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) != 1:
				self.error(
					self.translate("error", "param_number", line_number=line_number + 1, instruction_name=instruction_name, nb_params=1, given_params_nb=len(instruction_params))
				)
			else:
				self.instructions_list[line_number] = f"delay({instruction_params[0]})"


	def analyze_img(self, instruction_name:str, instruction_params:list, line_number:int):
		"""
		Analyzes the image method.
		"""
		# Checks if we can call this function
		if not self.did_winit:
			self.error(
				self.translate("error", "no_winit", line_number=line_number + 1, instruction_name=instruction_name)
			)

		# Creates the function compilation
		else:
			if len(instruction_params) > 2 and instruction_params[-2] in ("->", "<-"):
				self.instructions_list[line_number] = f"Image {instruction_params[-1]} = image({' '.join(instruction_params[:-2])})"
			else:
				self.instructions_list[line_number] = f"image({' '.join(instruction_params)})"


class GrapicPlugin(Plugin):
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

		# Adds all the grapic keywords to the instructions
		self.grapic_components = (
			"winit",     # winInit(str name, int width, int height)
			"wclear",    # winClear()
			"wdisplay",  # winDisplay()
			"wquit",     # winQuit()
			"color",     # color(unsigned char r, unsigned char g, unsigned char b)
			"bcolor",    # backgroundColor(unsigned char r, unsigned char g, unsigned char b)
			"pspace",    # pressSpace()
			"circle",    # circle(int xc, int yc, int radius)
			"circlef",   # circleFill(int xc, int yc, int radius)
			"line",      # line(int x1, int y1, int x2, int y2)
			"rect",      # rectangle(int x1, int y1, int x2, int y2)
			"rectf",     # rectangleFill(int x1, int y1, int x2, int y2)
			"ppixel",    # putPixel(int x, int y, unsigned char r, unsigned char g, unsigned char b, unsigned char a=255)
			"delay",     # delay(int duration)
			"img",       # image(str filename)
		)
		self.app.color_control_flow["instruction"] = (
			*self.app.color_control_flow["instruction"],
			*self.grapic_components
		)


	def init(self):
		"""
		Reloads the autocompletion if available, and adds everything to the compilers.
		"""
		# Tries to reload the autocomplete if it was loaded, we make sure those keywords are available to it
		if "autocomplete" in self.app.plugins:
			self.app.plugins["autocomplete"][-1].reload_autocomplete()

		# Also sets up the translation
		self.translations = translations

		# Adds all the grapic components to the compilers
		for compiler in self.app.compilers.values():
			for component in self.grapic_components:
				compiler.other_instructions.append(component)

		# Changes the superclass from the compilers to be the current compiler class
		GrapicAlgorithmicCompiler.__bases__ = (self.app.compilers["algorithmic"].__class__,)
		GrapicCppCompiler.__bases__ = (self.app.compilers["C++"].__class__,)

		# Replaces the compilers with the enhanced compilers
		self.app.compilers["algorithmic"] = GrapicAlgorithmicCompiler(self.app.compilers["algorithmic"], self.translate)
		self.app.compilers["C++"] = GrapicCppCompiler(self.app.compilers["C++"], self.translate)


def init(app):
	return GrapicPlugin(app)
