from plugin import Plugin
import pyperclip


class PastePlugin(Plugin):
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

		# Sets up the translation
		self.translations = {
			"en": {
				"paste": "Paste"
			},
			"fr": {
				"paste": "Coller"
			}
		}

		# Adds the command
		self.add_command("v", self.paste, self.translate("paste"))
		self.bind_control('v', 'v')


	def paste(self):
		"""
		Pastes the contents of the clipboard to the cursor position.
		"""
		clipboard_contents = pyperclip.paste()
		self.app.add_char_to_text(clipboard_contents)


def init(app) -> PastePlugin:
	return PastePlugin(app)
