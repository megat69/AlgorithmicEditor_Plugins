from plugin import Plugin


class DisableSyntaxHighlighting(Plugin):
	def __init__(self, app):
		super().__init__(app)
		self.translations = {
			"en": {
				"option_name": "Toggle syntax highlighting",
				"no_colors": "No colors",
				"all_colors": "All colors"
			},
			"fr": {
				"option_name": "Activer/Désactiver la coloration syntaxique",
				"no_colors": "Aucune couleur",
				"all_colors": "Toutes les couleurs"
			}
		}
		self.state = True
		self.add_option(self.translate("option_name"), lambda: (
			self.translate("no_colors")
				if self.state else
			self.translate("all_colors")
		), self.toggle)


	def init(self):
		self.state = self.get_config("current_state", True)
		self.base_function = self.app.syntax_highlighting
		self.set_function()


	def toggle(self):
		self.state = not self.state
		self.config["current_state"] = self.state
		self.set_function()

	def set_function(self):
		if self.state:
			self.app.syntax_highlighting = lambda x,y,z: None
		else:
			self.app.syntax_highlighting = self.base_function


def init(app):
	return DisableSyntaxHighlighting(app)