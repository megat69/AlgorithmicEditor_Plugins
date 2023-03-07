from plugin import Plugin
import curses


class CustomBottomBarStylingPlugin(Plugin):
	"""
	Allows the user to paste text at the cursor position.
	"""
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
		# Sets the defaults of the config if it wasn't created
		if "motif" not in self.config.keys():
			self.config["motif"] = r"°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸ "
		if "animated" not in self.config.keys():
			self.config["animated"] = False
		if "reversed" not in self.config.keys():
			self.config["reversed"] = False

		# Creates a custom motif for the bottom bar
		self.motif = self.config["motif"]

		# Loads the config options
		self.animated = self.config["animated"]
		self.reversed = self.config["reversed"]

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


def init(app) -> CustomBottomBarStylingPlugin:
	return CustomBottomBarStylingPlugin(app)
