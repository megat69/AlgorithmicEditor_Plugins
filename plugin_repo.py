import curses
import requests
from bs4 import BeautifulSoup
import os
import importlib
import re

from plugin import Plugin
from utils import display_menu, input_text


class PluginRepo(Plugin):
	def __init__(self, cls):
		super().__init__(cls)
		self.manage_plugins_menu = False
		self.selected_menu_item = 0
		self.add_command("r", self.manage_plugins, "Manage plugins")


	def init(self):
		print("PluginRepo plugin loaded !")


	def manage_plugins(self):
		"""
		Creates a menu with different plugin management options
		"""
		self.manage_plugins_menu = True
		while self.manage_plugins_menu:
			display_menu(self.cls.stdscr, (
				("List plugins", self.list_plugins),
				("Download plugins", self.download_plugins),
				("Delete plugins", self.delete_plugins),
				#("Reload plugins", self.reload_plugins),  #Left on the side for later implementation
				("Leave", self.leave)
			), self.selected_menu_item)


	def leave(self):
		self.manage_plugins_menu = False


	def list_plugins(self, plist:list=None, getch:bool=True):
		"""
		Lists all the installed plugins, and displays in red the faulty ones.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 0

		i = 0
		self.cls.stdscr.addstr(0, 20, f"-- {'AVAILABLE' if plist is not None else ''} PLUGINS LIST --".center(32), curses.A_BOLD)
		if plist is None:
			self.cls.stdscr.addstr(1, 20, "Faulty plugins displayed in red.", curses.A_BOLD)
		for plugin in (os.listdir(os.path.dirname(__file__)) if plist is None else plist):
			if plugin.startswith("__"): continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Displaying each plugin name at the left of the screen
			if plugin in self.cls.plugins.keys() or plist is not None:
				self.cls.stdscr.addstr(i + 3, 20, plugin.center(32))
			else:
				self.cls.stdscr.addstr(i + 3, 20, plugin.center(32), curses.color_pair(1))

			# Incrementing i by 1, we are forced to do this because we ignore some files at the
			# start of the loop.
			i += 1

		# Makes a pause
		if getch:
			self.cls.stdscr.getch()

	def download_plugins(self):
		"""
		Downloads a plugin from the plugins repository.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 1

		# Gives a list of all the available apps
		github_url = 'https://github.com/megat69/AlgorithmicEditor_Plugins/tree/master/'

		def wrong_return_code_inconvenience():
			"""
			Tells the user about an inconvenience during download attempt.
			"""
			msg_str = f"There have been a problem during the fetching of"
			self.cls.stdscr.addstr(self.cls.rows // 2, self.cls.cols // 2 - len(msg_str) // 2, msg_str)
			msg_str = f"the plugins list online. We apologize for the inconvenience."
			self.cls.stdscr.addstr(self.cls.rows // 2 + 1, self.cls.cols // 2 - len(msg_str) // 2, msg_str)
			self.cls.stdscr.getch()

		# TODO : Async this to create the UI before the download

		r = requests.get(github_url)
		if r.status_code != 200:
			wrong_return_code_inconvenience()
		else:
			soup = BeautifulSoup(r.text, 'html.parser')
			plugins = soup.find_all(title=re.compile("\.py$"))

			# Lists the available plugins to the user
			plugins_list = [e.extract().get_text()[:-3] for e in plugins]
			self.list_plugins(plugins_list, getch=False)

			# Asks the user to input the plugin name
			self.cls.stdscr.addstr(self.cls.rows - 2, 0, "Input the name of the plugin to download, or leave blank to cancel.")
			user_wanted_plugin = input_text(self.cls.stdscr)
			if user_wanted_plugin != "":
				if user_wanted_plugin in plugins_list:
					r = requests.get("https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Plugins/main/plugin_repo.py")
					if r.status_code != 200:
						wrong_return_code_inconvenience()
					else:
						with open(os.path.join(os.path.dirname(__file__), f"{user_wanted_plugin}.py"),
						          "w", encoding="utf-8") as f:
							f.write(r.text)
						msg_str = f"The plugin '{user_wanted_plugin}' has been successfully installed !"
						self.cls.stdscr.addstr(self.cls.rows // 2, self.cls.cols // 2 - len(msg_str) // 2, msg_str)
				else:
					msg_str = f"The plugin '{user_wanted_plugin}' doesn't seem to exist."
					self.cls.stdscr.addstr(self.cls.rows // 2, self.cls.cols // 2 - len(msg_str) // 2, msg_str)
			self.cls.stdscr.getch()


	def delete_plugins(self):
		"""
		Gets a plugin name then deletes it.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 2

		self.list_plugins(getch=False)
		self.cls.stdscr.addstr(self.cls.rows - 3, 0, "Input the name of the plugin you want to delete (or leave blank to cancel) :")
		plugin_name = input_text(self.cls.stdscr, position_y=self.cls.rows - 2)
		if plugin_name != "":
			plugins_list = tuple(
				plugin.replace(".py", "") for plugin in os.listdir(os.path.dirname(__file__)) if not plugin.startswith("__")
			)
			if plugin_name in plugins_list:  # If the plugin exists
				def delete_plugin():
					os.remove(os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"))
					msg_str = f"Plugin {plugin_name} deleted."
					self.cls.stdscr.addstr(self.cls.rows // 2, self.cls.cols // 2 - len(msg_str) // 2, msg_str)

				display_menu(self.cls.stdscr, (
					("Yes", delete_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to delete the plugin '{plugin_name}' ?")
			else:
				msg_str = f"The plugin '{plugin_name}' doesn't seem to be installed."
				self.cls.stdscr.addstr(self.cls.rows // 2, self.cls.cols // 2 - len(msg_str) // 2, msg_str)
				self.cls.stdscr.getch()


	def reload_plugins(self):
		"""
		Reloads all plugins.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 3

		# --- Uses the reload function on existing plugins, loads the rest. ---
		# Lists all the plugin files inside the plugins folder
		for plugin in os.listdir(os.path.dirname(__file__)):
			if plugin.startswith("__") or os.path.isdir(os.path.join(os.path.dirname(__file__), plugin)) \
					or not plugin.endswith(".py"):
				continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Importing the plugin and storing it in the variable
			if plugin not in self.cls.plugins.keys():
				try:
					self.cls.plugins[plugin] = [importlib.import_module(f"plugins.{plugin}")]
				except Exception as e:
					print(f"Failed to (re)load plugin {plugin} :\n{e}")
					continue
			else:
				try:
					self.cls.plugins[plugin] = [importlib.reload(self.cls.plugins[plugin][0])]
				except Exception as e:
					print(f"Failed to reload plugin {plugin} :\n{e}")
					del self.cls.plugins[plugin]
					continue

			# Initializes the plugins init function
			try:
				self.cls.plugins[plugin].append(self.cls.plugins[plugin][0].init(self))
			except Exception as e:
				print(f"An error occurred while importing the plugin '{plugin}' :\n{e}")
				del self.cls.plugins[plugin]

		self.list_plugins()


def init(cls) -> PluginRepo:
	return PluginRepo(cls)
