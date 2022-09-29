from plugin import Plugin
import pyperclip


class PastePlugin(Plugin):
	"""
	Allows the user to paste text at the cursor position.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_command("v", self.paste, "Paste")


	def paste(self):
		"""
		Changes the command symbol to whatever the user wants.
		"""
		clipboard_contents = pyperclip.paste()
		self.app.add_char_to_text(clipboard_contents)


def init(app) -> PastePlugin:
	return PastePlugin(app)
