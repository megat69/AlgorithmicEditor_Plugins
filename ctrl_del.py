import string

from plugin import Plugin


class CtrlDel(Plugin):
	"""
	Allows the user to use the Ctrl + Del keybind to remove a whole word.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("e", self.delete_word, "Delete Word")
		self.add_command("dl", self.delete_line, "Delete Line")


	def delete_word(self):
		"""
		Removes a whole world backwards.
		"""
		try:
			if self.app.current_text[self.app.current_index - 1] == " ":
				self._remove_current_char()
			while self.app.current_text[self.app.current_index - 1] in string.ascii_letters and self.app.current_index - 1 > 0:
				self._remove_current_char()
		except IndexError: return
		self.app.stdscr.clear()


	def delete_line(self):
		"""
		Removes a whole line backwards.
		"""
		try:
			while self.app.current_text[self.app.current_index - 1] != "\n" and self.app.current_index - 1 > 0:
				self._remove_current_char()
			else:
				self._remove_current_char()
		except IndexError: return
		self.app.stdscr.clear()

	def _remove_current_char(self):
		"""
		Removes the character at the index position.
		"""
		self.app.current_text = self.app.current_text[:self.app.current_index - 1] \
			+ self.app.current_text[self.app.current_index:]
		self.app.current_index -= 1

def init(app) -> CtrlDel:
	return CtrlDel(app)
