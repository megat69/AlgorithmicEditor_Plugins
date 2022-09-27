import curses
import requests
import os
import importlib

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


	def list_plugins(self):
		"""
		Lists all the installed plugins, and displays in red the faulty ones.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 0

		i = 0
		self.cls.stdscr.addstr(0, 20, "-- PLUGINS LIST --".center(32), curses.A_BOLD)
		self.cls.stdscr.addstr(1, 20, "Faulty plugins displayed in red.", curses.A_BOLD)
		for plugin in os.listdir(os.path.dirname(__file__)):
			if plugin.startswith("__"): continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Displaying each plugin name at the left of the screen
			if plugin in self.cls.plugins.keys():
				self.cls.stdscr.addstr(i + 3, 20, plugin.center(32))
			else:
				self.cls.stdscr.addstr(i + 3, 20, plugin.center(32), curses.color_pair(1))

			# Incrementing i by 1, we are forced to do this because we ignore some files at the
			# start of the loop.
			i += 1

		# Makes a pause
		self.cls.stdscr.getch()

	def download_plugins(self):
		"""
		Downloads a plugin from the plugins repository.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 1

		pass

	def delete_plugins(self):
		"""
		Gets a plugin name then deletes it.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 2

		self.list_plugins()
		self.cls.stdscr.addstr(self.cls.rows - 3, 0, "Input the name of the plugin you want to delete :")
		plugin_name = input_text(self.cls.stdscr, position_y=self.cls.rows - 2)
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
