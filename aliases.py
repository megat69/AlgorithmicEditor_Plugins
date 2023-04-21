from dataclasses import dataclass

from plugin import Plugin


@dataclass(slots=True)
class Alias:
	source: str
	destination: str


def alias_to_list(alias: Alias) -> list[str]:
	return [alias.source, alias.destination]


def list_to_alias(lst: list[str]) -> Alias:
	return Alias(lst[0], lst[1])



class AliasesPlugin(Plugin):
	"""
	Adds a new config option for the user to rebind their aliases.
	"""
	def __init__(self, app):
		super().__init__(app)
		self.add_option("Add command aliases", lambda: "New", self.modify_aliases)

		# Contains the list of aliases
		self.aliases: list[Alias] = [Alias("tr", "q")]


	def init(self):
		"""
		Loads the previous config.
		"""
		# Loads from the config
		self.load_from_config()

		# Loads all the aliases
		self.load_aliases()


	def modify_aliases(self):
		"""
		Modifies the aliases of the commands.
		"""
		pass


	def save_to_config(self):
		"""
		Saves the current alias preset to config.
		"""
		self.config["aliases"] = [
			alias_to_list(alias) for alias in self.aliases
		]


	def load_from_config(self):
		"""
		Saves the current alias preset to config.
		"""
		if "aliases" in self.config.keys():
			self.aliases = [
				list_to_alias(alias) for alias in self.config["aliases"]
			]
		else:
			self.config["aliases"] = []


	def load_aliases(self):
		"""
		Loads the aliases of each command.
		"""
		# Deletes all the previous aliased commands
		for key, value in list(self.app.commands.items()):
			if len(value) > 3:
				del self.app.commands[key]

		# Adds all the aliased commands
		for alias in self.aliases:
			if alias.source in self.app.commands:
				print(f"{alias.source!r} command already exists, cannot replace with {alias.destination!r}")

			elif alias.destination not in self.app.commands:
				print(f"{alias.source!r} cannot be set as {alias.destination!r} does not exist")

			else:
				self.app.commands[alias.source] = self.app.commands[alias.destination]


def init(app):
	return AliasesPlugin(app)
