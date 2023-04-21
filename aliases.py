import curses
from dataclasses import dataclass

from plugin import Plugin
from utils import input_text


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
		self.aliases: list[Alias] = []


	def init(self):
		"""
		Loads the previous config.
		"""
		# Loads the commands added before this plugin
		self.previous_commands = self.app.commands.copy()

		# Loads from the config
		self.load_from_config()

		# Loads all the aliases
		self.load_aliases()


	def modify_aliases(self):
		"""
		Modifies the aliases of the commands.
		"""
		# Displays the label of the aliases
		msg_str = "-- Modify the aliases --"
		self.app.stdscr.addstr(
			1,
			self.app.cols // 2 - len(msg_str) // 2,
			msg_str,
			curses.A_REVERSE
		)

		# Counts which option is selected
		current_index = 0
		col_index = 0

		while True:
			# Which key was last pressed
			key = ""

			while key not in ("\n", "\t"):
				# Displays each of the aliases already created
				for i, alias in enumerate(self.aliases):
					self.app.stdscr.addstr(
						i + 3, 10, alias.source,
						curses.A_REVERSE if i == current_index and col_index == 0 else curses.A_NORMAL
					)
					self.app.stdscr.addstr(
						i + 3, self.app.cols // 2, alias.destination,
						curses.A_REVERSE if i == current_index and col_index == 1 else curses.A_NORMAL
					)

				# Displays the two other options
				self.app.stdscr.addstr(
					len(self.aliases) + 5, 10, "Add new alias",
					curses.A_REVERSE if current_index - len(self.aliases) == 0 else curses.A_NORMAL
				)
				self.app.stdscr.addstr(
					len(self.aliases) + 6, 10, "Done",
					curses.A_REVERSE if current_index - len(self.aliases) == 1 else curses.A_NORMAL
				)

				# Gets what the user wants to do
				key = self.app.stdscr.getkey()

				# Gets which key is used
				if key == "KEY_UP":
					current_index -= 1
				elif key == "KEY_DOWN":
					current_index += 1
				if key == "KEY_LEFT":
					col_index -= 1
				elif key == "KEY_RIGHT":
					col_index += 1
				current_index %= len(self.aliases) + 2
				col_index %= 2

			if current_index - len(self.aliases) == 0:  # Add one row
				new_alias = Alias("", "")
				new_alias.source = input_text(self.app.stdscr, 10, len(self.aliases) + 3)
				new_alias.destination = input_text(self.app.stdscr, self.app.cols // 2, len(self.aliases) + 3)
				if new_alias.source == "" or new_alias.destination == "":
					self.app.stdscr.addstr(len(self.aliases) + 3, 10, "Cannot add this alias.")
					self.app.stdscr.getch()
				else:
					self.aliases.append(new_alias)
					self.app.stdscr.clear()

			if current_index - len(self.aliases) == 1:  # Finish changing the aliases
				self.load_aliases()
				self.save_to_config()
				break

			else:
				self.app.stdscr.addstr(
					current_index + 3,
					10 if col_index == 0 else self.app.cols // 2,
					" " * (self.app.cols // 2 - 10)
				)
				new_text = input_text(
					self.app.stdscr,
					10 if col_index == 0 else self.app.cols // 2,
					current_index + 3
				)

				if new_text != "":
					if col_index == 0:
						self.aliases[current_index].source = new_text
					else:
						self.aliases[current_index].destination = new_text


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
		self.app.commands = self.previous_commands.copy()

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
