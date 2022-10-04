from plugin import Plugin
import pyperclip


class CopyPlugin(Plugin):
	"""
	Allows the user to paste text at the cursor position.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("co", self.copy, "Copy Selection")
		self.within_copy = False
		self.start_index = 0


	def copy(self):
		"""
		Starts a selection made by the user.
		"""
		self.start_index = self.app.current_index
		self.within_copy = True


	def update_on_keypress(self, key:str):
		"""
		Copies if the selection is finished.
		"""
		# If we are selecting something to copy
		if self.within_copy:
			# If the user hit Enter
			if key == "\n":
				# We copy what has been selected
				pyperclip.copy(
					self.app.current_text[
						min(self.start_index, self.app.current_index) :
						max(self.start_index, self.app.current_index)
					]
				)
				# We remember that we are no longer copying
				self.within_copy = False

			# Shows a message telling the user that he's still copying
			else:
				self.app.stdscr.addstr(self.app.rows - 1, 4, "Awaiting selection for copy")


def init(app) -> CopyPlugin:
	return CopyPlugin(app)
