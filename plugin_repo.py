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

# TODO Plugin documentation
class PluginRepo(Plugin):
	def __init__(self, app):
		super().__init__(app)
		self.manage_plugins_menu = False
		self.selected_menu_item = 0
		self.add_command("r", self.manage_plugins, "Manage plugins")


	def init(self):
		"""
		Initializes the plugin with a message to tell you it was correctly loaded.
		"""
		self.app.log("PluginRepo plugin loaded !")


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
				("Reload plugins", self.reload_plugins),
				("Read online plugins doc", self.docs_plugins),
				("Leave", self.leave)
			), self.selected_menu_item)


	def leave(self):
		"""
		Closes the menu by setting the variable controlling the while loop to False.
		"""
		self.manage_plugins_menu = False


	def list_plugins(self, plist:list=None, getch:bool=True):
		"""
		Lists all the installed plugins, and displays in red the faulty ones.
		:param plist: A list of plugins to show the user. If None, will look into the plugins folder. Default is None.
		:param getch: Whether to do a getch at the after the list is fully displayed.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 0

		# Initializing a counter
		i = 0

		# Creating the message displayed to the user
		msg = f"-- {'AVAILABLE' if plist is not None else ''} PLUGINS LIST --"
		self.app.stdscr.addstr(0, self.app.cols // 2 - len(msg) // 2, msg, curses.A_BOLD)

		# If no plugins list was provided to the function, we add another message
		if plist is None:
			msg = "Faulty plugins displayed in red."
			self.app.stdscr.addstr(1, self.app.cols // 2 - len(msg) // 2, msg, curses.A_BOLD)

		# We fetch each plugin in the list of plugins or in the plugins folder, depending on plist
		for plugin in (os.listdir(os.path.dirname(__file__)) if plist is None else plist):
			# We eject non-conforming files
			if plugin.startswith("__") or \
				os.path.isdir(os.path.join(os.path.dirname(__file__), plugin))\
				or not plugin.endswith(".py"):
				continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Displaying each plugin name at the left of the screen
			if plugin in self.app.plugins.keys() or plist is not None:
				self.app.stdscr.addstr(i + 3, self.app.cols // 2 - len(plugin) // 2, plugin)
			else:
				self.app.stdscr.addstr(i + 3, self.app.cols // 2 - len(plugin) // 2, plugin, curses.color_pair(1))

			# Incrementing i by 1, we are forced to do this because we ignore some files at the
			# start of the loop.
			i += 1

		# Makes a pause
		if getch:
			self.app.stdscr.getch()


	def list_online_plugins(self):
		"""
		Lists the online plugins available.
		"""
		# Gives a list of all the available apps
		github_url = 'https://github.com/megat69/AlgorithmicEditor_Plugins/tree/master/'

		# Tries to connect to the URL on GitHub
		try:
			r = requests.get(github_url)
		# If the connection fails, it tells the user and exits the function
		except requests.exceptions.ConnectionError:
			self._wrong_return_code_inconvenience()
			msg_str = f"Please check your connection and try again."
			self.app.stdscr.addstr(self.app.rows // 2 + 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
			return None

		# If the status code is not HTTP 200 (OK), we tell the user that something went wrong.
		if r.status_code != 200:
			self._wrong_return_code_inconvenience()

		# If everything worked, we parse the webpage to find all references to .py files
		else:
			soup = BeautifulSoup(r.text, 'html.parser')
			plugins = soup.find_all(title=re.compile("\.py$"))

			# Lists the available plugins to the user
			plugins_list = [e.extract().get_text() for e in plugins]
			self.list_plugins(plugins_list, getch=False)
			# We return the list of plugins, cleaning up their extension as well.
			return [e[:-3] for e in plugins_list]


	def download_plugins(self):
		"""
		Downloads a plugin from the plugins repository.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 1

		# Gets the list of available plugins from online
		plugins_list = self.list_online_plugins()
		# Leaves the function if self.list_online_plugins() returned None (an error occured)
		if plugins_list is None: return None

		# Asks the user to input the plugin name
		self.app.stdscr.addstr(self.app.rows - 2, 0, "Input the name of the plugin to download, or leave blank to cancel.")
		user_wanted_plugin = input_text(self.app.stdscr)

		# If the user wrote nothing, it means he wants to cancel, so we stop the function there
		if user_wanted_plugin != "":
			# If the user specified an existing plugin name
			if user_wanted_plugin in plugins_list:
				# We download the contents of the file from GitHub
				r = requests.get(f"https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Plugins/main/{user_wanted_plugin}.py")

				# If something went wrong with the request (the webpage didn't return an HTTP 200 (OK) code), we warn the user and exit the function
				if r.status_code != 200:
					self._wrong_return_code_inconvenience()

				# If everything went well
				else:
					# We dump the contents of the plugin file into a file of the corresponding name
					with open(os.path.join(os.path.dirname(__file__), f"{user_wanted_plugin}.py"), "w", encoding="utf-8") as f:
						f.write(r.text)

					# We then try to download the plugin's docs
					r = requests.get(f"https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Plugins/main/{user_wanted_plugin}.md")
					# If everything went well, we simply dump the contents of the documentation file into another file
					# And if something went wrong, we simply don't do it and don't warn the user, he'll download it later
					if r.status_code == 200:
						with open(os.path.join(os.path.dirname(__file__), f"{user_wanted_plugin}.md"), "w", encoding="utf-8") as f:
							f.write(r.text)

					# We tell the user that the plugin has been successfully installed
					msg_str = f"The plugin '{user_wanted_plugin}' has been successfully installed !"
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()

					# We ask the user if he wants to reload the plugins, and if so, we do it
					display_menu(
						self.app.stdscr,
						(
							("Yes", self.reload_plugins),
							("No", lambda: None)
						),
						label = "Do you want to reload the plugins ?"
					)

			# If the user specified a non-existing plugin name, we show him an error and exit the function
			else:
				msg_str = f"The plugin '{user_wanted_plugin}' doesn't seem to exist."
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()


	def docs_plugins(self):
		"""
		Reads the documentation of a plugin from the repository
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 6

		# Gets the list of available plugins from online
		plugins_list = self.list_online_plugins()
		# Leaves the function if self.list_online_plugins() returned None (an error occured)
		if plugins_list is None: return None

		# Asks the user to input the plugin name
		self.app.stdscr.addstr(self.app.rows - 2, 0, "Input the name of the plugin to download, or leave blank to cancel.")
		user_wanted_plugin = input_text(self.app.stdscr)

		# If the user wrote nothing, it means he wants to cancel, so we stop the function there
		if user_wanted_plugin != "":
			# If the user specified an existing plugin name
			if user_wanted_plugin in plugins_list:
				# We download the contents of the file from GitHub
				r = requests.get(f"https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Plugins/main/{user_wanted_plugin}.md")

				# If something went wrong with the request (the webpage didn't return an HTTP 200 (OK) code), we warn the user and exit the function
				if r.status_code != 200:
					self._wrong_return_code_inconvenience()

				# If everything went well
				else:
					# We clear the screen to make room for the docs display
					self.app.stdscr.clear()
					# Puts text into shape with markdown
					for i, line in enumerate(r.text.split("\n")):
						color = line.count("#")
						# Adds the markdown line by line
						self.app.stdscr.addstr(i, 0, line, curses.color_pair(color))
					# Awaits a character input to make a pause
					self.app.stdscr.getch()

			# If the user specified a non-existing plugin name, we show him an error and exit the function
			else:
				msg_str = f"The plugin documentation for '{user_wanted_plugin}' doesn't seem to exist."
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
					try:
						os.remove(os.path.join(os.path.dirname(__file__), f"{plugin_name}.md"))
					except FileNotFoundError: pass
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
					self.app.log(f"Failed to (re)load plugin {plugin} :\n{e}")
					continue
			else:
				try:
					self.app.plugins[plugin] = [importlib.reload(self.app.plugins[plugin][0])]
				except Exception as e:
					self.app.log(f"Failed to reload plugin {plugin} :\n{e}")
					del self.app.plugins[plugin]
					continue

			# Initializes the plugins init function
			try:
				self.app.plugins[plugin].append(self.app.plugins[plugin][0].init(self.app))
			except Exception as e:
				self.app.log(f"An error occurred while importing the plugin '{plugin}' :\n{e}")
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
						self.app.log(f"Failed to load plugin {plugin_name} :\n{e}")
						return

					# Initializes the plugins init function
					try:
						self.app.plugins[plugin_name].append(self.app.plugins[plugin_name][0].init(self.app))
					except Exception as e:
						del self.app.plugins[plugin_name]
						self.app.log(f"An error occurred while importing the plugin '{plugin_name}' :\n{e}")

					msg_str = f"Plugin {plugin_name} enabled !"
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.log(msg_str)
					self.app.stdscr.getch()

				display_menu(self.app.stdscr, (
					("Yes", enable_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to enable the plugin '{plugin_name}' ?")
			else:
				msg_str = f"The plugin '{plugin_name}' doesn't seem to be installed."
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()


	def update_on_keypress(self, key:str):
		"""
		Triggers the :r if F6 is hit.
		"""
		if key == "KEY_F(6)":
			self.manage_plugins()
		elif key == "KEY_F(5)":
			self.reload_plugins()


	def _wrong_return_code_inconvenience(self):
		"""
		Tells the user about an inconvenience during download attempt.
		"""
		msg_str = f"There have been a problem during the fetching of"
		self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
		msg_str = f"the plugins list online. We apologize for the inconvenience."
		self.app.stdscr.addstr(self.app.rows // 2 + 1, self.app.cols // 2 - len(msg_str) // 2, msg_str)
		self.app.stdscr.getch()


def init(app) -> PluginRepo:
	return PluginRepo(app)
