from plugin import Plugin
import pyperclip


class CopyPlugin(Plugin):
	"""
	Allows the user to paste text at the cursor position.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("co", self.copy, "Copy Selection")
		self.add_command("x", self.cut, "Cut Selection")
		self.within_copy = False
		self.start_index = 0
		self.do_cut = False


	def copy(self):
		"""
		Starts a selection made by the user.
		"""
		self.start_index = self.app.current_index
		self.within_copy = True
		self.do_cut = False

	def cut(self):
		self.copy()
		self.do_cut = True


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
						max(self.start_index, self.app.current_index) + 1
					]
				)
				# We remember that we are no longer copying
				self.within_copy = False

				# If we want to cut, we remove all text between the selection areas
				if self.do_cut:
					self.app.current_text = self.app.current_text[:min(self.start_index, self.app.current_index)] + \
						self.app.current_text[max(self.start_index, self.app.current_index)+1:]
					self.app.current_index -= len(pyperclip.paste())

				# Removes the enter that was added due to the keypress
				self.app.current_text = self.app.current_text[:self.app.current_index - 1] +\
						self.app.current_text[self.app.current_index:]
				self.app.current_index -= 1


			# Shows a message telling the user that he's still copying
			else:
				self.app.stdscr.addstr(self.app.rows - 1, 4, "Awaiting selection for copy")


def init(app) -> CopyPlugin:
	return CopyPlugin(app)
