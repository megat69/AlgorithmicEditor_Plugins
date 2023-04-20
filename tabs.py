import curses
import os

from plugin import Plugin
from utils import browse_files


class TabsPlugin(Plugin):
	"""
	Adds support for all the tabs opened by the user.
	"""
	def __init__(self, app):
		super().__init__(app)

		# Sets up the translations
		self.translations = {
			"en": {
				"untitled": "Untitled",
				"new_empty": "New empty tab",
				"new_open": "Open new tab",
				"close_tab": "Close current tab"
			},
			"fr": {
				"untitled": "Sans titre",
				"new_empty": "Nouvel onglet vide",
				"new_open": "Ouvrir un onglet",
				"close_tab": "Fermer l'onglet actuel"
			}
		}

		# Contains all the tabs, in the scheme <name> <current_text> <current_index> <last_save_action>
		self.tabs = []

		# The index of the current selected tab
		self.current_tab = 0

		# Saves the default 'apply_stylings' method of the app in a variable
		self.default_apply_stylings = self.app.apply_stylings

		# Overrides the app's 'apply_stylings' method with a custom one
		self.app.apply_stylings = self.custom_apply_stylings

		# Creates the two commands to open new tabs
		self.add_command("n", self.user_new_tab, self.translate("new_empty"))
		self.add_command("no", self.user_open_new_tab, self.translate("new_open"))

		# Creates the command to close a tab
		self.add_command("w", self.close_tab, self.translate("close_tab"))


	def init(self):
		"""
		Creates the first tab.
		"""
		self.tabs.append([
			(self.translate("untitled")
			 if self.app.last_save_action == "clipboard" else
			 os.path.split(os.path.normpath(self.app.last_save_action))[-1]),
			self.app.current_text,
			0,
			self.app.last_save_action
		])


	def _reset_tab(self):
		"""
		Resets the contents of the current tab to what is stored in the tab info.
		"""
		self.app.current_text = self.tabs[self.current_tab][1]
		self.app.current_index = self.tabs[self.current_tab][2]
		self.app.last_save_action = self.tabs[self.current_tab][3]


	def user_new_tab(self):
		"""
		Opens a new blank tab for the user.
		"""
		# Creates the tab name as "Yntitled", "Untitled 2", etc...
		tab_name = self.translate("untitled")
		untitled_count = 0
		for names in self.tabs:
			if names[0].startswith(tab_name):
				untitled_count += 1
		if untitled_count != 0:
			tab_name += " " + str(untitled_count + 1)

		# Creates the new tab
		self.tabs.append([
			tab_name,
			"",
			0,
			"clipboard"
		])
		self.current_tab = len(self.tabs) - 1
		self._reset_tab()
		self.app.stdscr.clear()
		self.app.display_text()


	def user_open_new_tab(self):
		"""
		Promptes the user for a new tab open.
		"""
		# Asks the user to get to the file he wants to open
		filename = browse_files(self.app.stdscr)()

		# If the user cancelled, so do we do with this function
		if filename == "": return

		# We create a new tab
		with open(filename) as f:
			self.tabs.append([
				 os.path.split(os.path.normpath(filename))[-1],
				f.read(),
				0,
				filename
			])
			self.current_tab = len(self.tabs) - 1
			self._reset_tab()



	def close_tab(self):
		"""
		Closes the current tab.
		"""
		self.tabs.pop(self.current_tab)
		if self.current_tab != 0:
			self.current_tab -= 1
		self._reset_tab()


	def update_on_keypress(self, key: str):
		"""
		Allows the user to switch tabs.
		:param key: The currently pressed key.
		"""
		# Saves the current progress of the tab
		self.tabs[self.current_tab][1] = self.app.current_text
		self.tabs[self.current_tab][2] = self.app.current_index

		# Changes tab upon tab or shift tab
		if key == "KEY_BTAB":
			self.current_tab += 1
			self.current_tab %= len(self.tabs)
			self._reset_tab()

		# Updates the last save action if it was changed
		elif self.app.last_save_action != "clipboard":
			self.tabs[self.current_tab][0] = os.path.split(os.path.normpath(self.app.last_save_action))[-1]


	def custom_apply_stylings(self):
		"""
		Displays the tab names.
		"""
		self.default_apply_stylings()

		for i in range(len(self.tabs)):
			x_pos = 0
			for j in range(i):
				x_pos += len(self.tabs[j][0]) + 4

			# Displays the name of the tab one by one
			self.app.stdscr.addstr(
				self.app.rows - 3,
				x_pos,
				"| " + self.tabs[i][0] + " |",
				(curses.color_pair(self.app.color_pairs["instruction"]) | curses.A_REVERSE)
					if i == self.current_tab else
				curses.A_NORMAL
			)


def init(app) -> TabsPlugin:
	return TabsPlugin(app)
