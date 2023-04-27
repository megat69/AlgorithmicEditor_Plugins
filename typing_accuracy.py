import curses

from plugin import Plugin


class TypingAccuracyPlugin(Plugin):
	"""
	A fun plugin that shows how many times you've removed characters versus how many times you've added characters.
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

		# How many characters have been typed vs how many were removed
		self.removed_chars, self.added_chars = 0, 0


	def init(self):
		"""
		Defines two color pairs for the colors of the bar.
		"""
		curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_GREEN)
		curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_RED)


	def update_on_keypress(self, key: str):
		"""
		Updates the count of characters and displays the percentage of them being removed/added.
		"""
		# Checks if the key is a backspace key, and if so, adds it to the removed characters
		if key in ("KEY_BACKSPACE", "\b", "\0"):
			self.removed_chars += 1
		# Then we increment the amount of total characters
		self.added_chars += 1

		# Displays the progress bar with the percentage of characters removed/added
		percentage = self.removed_chars / self.added_chars
		self.app.stdscr.addstr(
			self.app.rows - 5,
			self.app.cols - 20,
			" " * 10,
			curses.color_pair(11)
		)
		self.app.stdscr.addstr(
			self.app.rows - 5,
			self.app.cols - 20,
			" " * int((1 - percentage) * 10),
			curses.color_pair(10)
		)
		self.app.stdscr.addstr(
			self.app.rows - 5,
			self.app.cols - 9,
			f"{((1 - percentage) * 100):.1f}%",
			curses.color_pair(10 + (percentage > 0.5)) | curses.A_REVERSE
		)


def init(app):
	return TypingAccuracyPlugin(app)