from plugin import Plugin
from utils import input_text
import curses


class CustomBottomBarStylingPlugin(Plugin):
	"""
	Allows the user to paste text at the cursor position.
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
		# Saves the default 'apply_stylings' method of the app in a variable
		self.default_apply_stylings = self.app.apply_stylings

		# Overrides the app's 'apply_stylings' method with a custom one
		self.app.apply_stylings = self.custom_apply_stylings

		# Creating the class variables
		self.motif = " "
		self.animated = False
		self.reversed = False

		# Remembers that this is the first iteration of the animation
		self._iteration = 0


	def init(self):
		"""
		Loads the config.
		"""
		# Creates a custom motif for the bottom bar
		self.motif = self.get_config("motif", r"°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸ ")

		# Loads the config options
		self.animated = self.get_config("animated", False)
		self.reversed = self.get_config("reversed", False)

		# Creates the in-app options
		self.add_option("Change bottom bar motif", lambda: "", self.change_motif)
		self.add_option("Toggle bottom bar animation", lambda: self.animated, self.toggle_animation)
		self.add_option("Toggle bottom bar motif reversing", lambda: self.reversed, self.toggle_reversed)


	def custom_apply_stylings(self):
		"""
		Changes the bottom bar's style on keypress.
		"""
		# Calls the app's apply_stylings method
		self.default_apply_stylings()

		# If the iteration amount is longer than the motif, we reset it to 0
		if self._iteration >= len(self.motif):
			self._iteration = 0

		# -- Then replaces the bottom bar --
		# Generates the bottom bar characters
		final_string = self.motif[self._iteration * self.animated:] + self.motif * (self.app.cols // len(self.motif) + 1)
		final_string = final_string[:self.app.cols]
		# Writing the bottom bar
		try:
			self.app.stdscr.addstr(
				self.app.rows - 3, 0,
				final_string,
				curses.A_REVERSE if self.reversed else curses.A_NORMAL
			)
		except curses.error: pass
		except AttributeError: pass

		# Increasing the amount of iterations
		self._iteration += 1


	def change_motif(self):
		"""
		Grabs text from the user so they can change the motif of the bottom bar.
		"""
		self.app.stdscr.clear()
		self.app.stdscr.addstr(0, 0, f"Your current motif is : '{self.motif}'")
		self.app.stdscr.addstr(1, 0, "Input a new one :")
		new_motif = input_text(self.app.stdscr, 18, 1)
		if new_motif:
			self.motif = new_motif
		self.config["motif"] = self.motif

	def toggle_animation(self):
		"""
		Toggles whether the bottom bar will have an animation
		"""
		self.animated = not self.animated
		self.config["animated"] = self.animated

	def toggle_reversed(self):
		"""
		Toggles whether the motif should reverse every other motif.
		"""
		self.reversed = not self.reversed
		self.config["reversed"] = self.reversed


def init(app) -> CustomBottomBarStylingPlugin:
	return CustomBottomBarStylingPlugin(app)
