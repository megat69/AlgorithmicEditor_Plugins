import curses
import requests
from bs4 import BeautifulSoup
import os
import importlib
import re

from plugin import Plugin
from utils import display_menu, input_text

# Creates the 'disabled_plugins' folder if it doesn't exist
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'disabled_plugins')):
	os.mkdir(os.path.join(os.path.dirname(__file__), 'disabled_plugins'))


class PluginRepo(Plugin):
	def __init__(self, app):
		super().__init__(app)
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
			display_menu(self.app.stdscr, (
				("List plugins", self.list_plugins),
				("Download plugins", self.download_plugins),
				("Delete plugins", self.delete_plugins),
				("Disable plugins", self.disable_plugins),
				("Enable plugins", self.enable_plugins),
				("Reload plugins", self.reload_plugins),  #Left on the side for later implementation
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
		self.app.stdscr.addstr(0, 20, f"-- {'AVAILABLE' if plist is not None else ''} PLUGINS LIST --".center(32), curses.A_BOLD)
		if plist is None:
			self.app.stdscr.addstr(1, 20, "Faulty plugins displayed in red.", curses.A_BOLD)
		for plugin in (os.listdir(os.path.dirname(__file__)) if plist is None else plist):
			if plugin.startswith("__") or \
				os.path.isdir(os.path.join(os.path.dirname(__file__), plugin))\
				or not plugin.endswith(".py"):
				continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Displaying each plugin name at the left of the screen
			if plugin in self.app.plugins.keys() or plist is not None:
				self.app.stdscr.addstr(i + 3, 20, plugin.center(32))
			else:
				self.app.stdscr.addstr(i + 3, 20, plugin.center(32), curses.color_pair(1))

			# Incrementing i by 1, we are forced to do this because we ignore some files at the
			# start of the loop.
			i += 1

		# Makes a pause
		if getch:
			self.app.stdscr.getch()

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
			self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
			msg_str = f"the plugins list online. We apologize for the inconvenience."
			self.app.stdscr.addstr(self.app.rows // 2 + 1, self.app.cols // 2 - len(msg_str) // 2, msg_str)
			self.app.stdscr.getch()

		# TODO : Async this to create the UI before the download

		try:
			r = requests.get(github_url)
		except requests.exceptions.ConnectionError:
			wrong_return_code_inconvenience()
			msg_str = f"Please check your connection and try again."
			self.app.stdscr.addstr(self.app.rows // 2 + 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
			return
		if r.status_code != 200:
			wrong_return_code_inconvenience()
		else:
			soup = BeautifulSoup(r.text, 'html.parser')
			plugins = soup.find_all(title=re.compile("\.py$"))

			# Lists the available plugins to the user
			plugins_list = [e.extract().get_text()[:-3] for e in plugins]
			self.list_plugins(plugins_list, getch=False)

			# Asks the user to input the plugin name
			self.app.stdscr.addstr(self.app.rows - 2, 0, "Input the name of the plugin to download, or leave blank to cancel.")
			user_wanted_plugin = input_text(self.app.stdscr)
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
						self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				else:
					msg_str = f"The plugin '{user_wanted_plugin}' doesn't seem to exist."
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()


	def delete_plugins(self):
		"""
		Gets a plugin name then deletes it.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 2

		self.list_plugins(getch=False)
		self.app.stdscr.addstr(self.app.rows - 3, 0, "Input the name of the plugin you want to delete (or leave blank to cancel) :")
		plugin_name = input_text(self.app.stdscr, position_y=self.app.rows - 2)
		if plugin_name != "":
			plugins_list = tuple(
				plugin.replace(".py", "") for plugin in os.listdir(os.path.dirname(__file__)) if not (plugin.startswith("__")
				or os.path.isdir(os.path.join(os.path.dirname(__file__), plugin))
				or not plugin.endswith(".py"))
			)
			if plugin_name in plugins_list:  # If the plugin exists
				def delete_plugin():
					os.remove(os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"))
					msg_str = f"Plugin {plugin_name} deleted."
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()

				display_menu(self.app.stdscr, (
					("Yes", delete_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to delete the plugin '{plugin_name}' ?")
			else:
				msg_str = f"The plugin '{plugin_name}' doesn't seem to be installed."
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()


	def reload_plugins(self):
		"""
		Reloads all plugins.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 5

		# --- Uses the reload function on existing plugins, loads the rest. ---
		# Lists all the plugin files inside the plugins folder
		for plugin in os.listdir(os.path.dirname(__file__)):
			if plugin.startswith("__") or \
					os.path.isdir(os.path.join(os.path.dirname(__file__), plugin)) \
					or not plugin.endswith(".py"):
				continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Importing the plugin and storing it in the variable
			if plugin not in self.app.plugins.keys():
				try:
					self.app.plugins[plugin] = [importlib.import_module(f"plugins.{plugin}")]
				except Exception as e:
					print(f"Failed to (re)load plugin {plugin} :\n{e}")
					continue
			else:
				try:
					self.app.plugins[plugin] = [importlib.reload(self.app.plugins[plugin][0])]
				except Exception as e:
					print(f"Failed to reload plugin {plugin} :\n{e}")
					del self.app.plugins[plugin]
					continue

			# Initializes the plugins init function
			try:
				self.app.plugins[plugin].append(self.app.plugins[plugin][0].init(self.app))
			except Exception as e:
				print(f"An error occurred while importing the plugin '{plugin}' :\n{e}")
				del self.app.plugins[plugin]

		self.list_plugins()

	def disable_plugins(self):
		"""
		Disables an existing plugin.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 3

		# Lists all plugins and asks to select the plugin to disable
		self.list_plugins(getch=False)
		self.app.stdscr.addstr(self.app.rows - 3, 0, "Input the name of the plugin you want to disable (or leave blank to cancel) :")
		plugin_name = input_text(self.app.stdscr, position_y=self.app.rows - 2)
		if plugin_name != "":
			plugins_list = tuple(
				plugin.replace(".py", "") for plugin in os.listdir(os.path.dirname(__file__)) if not \
				(plugin.startswith("__")
				or os.path.isdir(os.path.join(os.path.dirname(__file__), plugin))
				or not plugin.endswith(".py"))
			)
			if plugin_name in plugins_list:  # If the plugin exists
				def disable_plugin():
					os.rename(
						os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"),
						os.path.join(os.path.dirname(__file__), "disabled_plugins", f"{plugin_name}.py")
					)
					msg_str = f"Plugin {plugin_name} disabled."
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()

				display_menu(self.app.stdscr, (
					("Yes", disable_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to disable the plugin '{plugin_name}' ?")
			else:
				msg_str = f"The plugin '{plugin_name}' doesn't seem to be installed."
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()

	def enable_plugins(self):
		"""
		Enables a previously disabled plugin
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 4

		# Lists all plugins and asks to select the plugin to disable
		plugins_list = tuple(
			plugin for plugin in
			os.listdir(os.path.join(os.path.dirname(__file__), "disabled_plugins")) if
			(plugin.startswith("__")
			or os.path.isdir(os.path.join(os.path.dirname(__file__), "disabled_plugins", plugin))
			or not plugin.endswith(".py")) is False
		)
		self.list_plugins(getch=False, plist=list(plugins_list))
		self.app.stdscr.addstr(self.app.rows - 3, 0, "Input the name of the plugin you want to enable (or leave blank to cancel) :")
		plugin_name = input_text(self.app.stdscr, position_y=self.app.rows - 2)
		if plugin_name != "":
			if plugin_name + ".py" in plugins_list:  # If the plugin exists
				def enable_plugin():
					os.rename(
						os.path.join(os.path.dirname(__file__), "disabled_plugins", f"{plugin_name}.py"),
						os.path.join(os.path.dirname(__file__), f"{plugin_name}.py")
					)

					# Importing the plugin and storing it in the variable
					try:
						self.app.plugins[plugin_name] = [importlib.import_module(f"plugins.{plugin_name}")]
					except Exception as e:
						print(f"Failed to load plugin {plugin_name} :\n{e}")
						return

					# Initializes the plugins init function
					try:
						self.app.plugins[plugin_name].append(self.app.plugins[plugin_name][0].init(self.app))
					except Exception as e:
						del self.app.plugins[plugin_name]
						print(f"An error occurred while importing the plugin '{plugin_name}' :\n{e}")

					msg_str = f"Plugin {plugin_name} enabled !"
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					print(msg_str)
					self.app.stdscr.getch()

				display_menu(self.app.stdscr, (
					("Yes", enable_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to enable the plugin '{plugin_name}' ?")
			else:
				msg_str = f"The plugin '{plugin_name}' doesn't seem to be installed."
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()


def init(app) -> PluginRepo:
	return PluginRepo(app)
