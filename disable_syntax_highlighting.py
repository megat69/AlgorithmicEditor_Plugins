from plugin import Plugin


class DisableSyntaxHighlighting(Plugin):
	def __init__(self, app):
		super().__init__(app)
		self.state = self.get_config("current_state", True)
		self.add_option("Toggle syntax highlighting", lambda: self.state, self.toggle)


	def init(self):
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