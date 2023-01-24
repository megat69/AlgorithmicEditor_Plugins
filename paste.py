from plugin import Plugin
import pyperclip


class PastePlugin(Plugin):
	"""
	Allows the user to paste text at the cursor position.
	"""
	def __init__(self, app):
		super().__init__(app)

		# Sets up the translation
		self.translation = {
			"en": {
				"paste": "Paste"
			},
			"fr": {
				"paste": "Coller"
			}
		}

		# Adds the command
		self.add_command("v", self.paste, self.translate("paste"))


	def paste(self):
		"""
		Pastes the contents of the clipboard to the cursor position.
		"""
		clipboard_contents = pyperclip.paste()
		self.app.add_char_to_text(clipboard_contents)


def init(app) -> PastePlugin:
	return PastePlugin(app)
