import curses
import requests
from bs4 import BeautifulSoup
import os
import importlib
import re

from plugin import Plugin
from utils import display_menu, input_text

# TODO Install all plugins

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


	def list_plugins(self, plist:list=None, getch:bool=True, check_py:bool=True, highlighted_plugins:list=None):
		"""
		Lists all the installed plugins, and displays in red the faulty ones.
		:param plist: A list of plugins to show the user. If None, will look into the plugins folder. Default is None.
		:param getch: Whether to do a getch at the after the list is fully displayed.
		:param check_py: Whether to ask for py files.
		:param highlighted_plugins: Will highlight the plugins in this list. None by default.
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
				or (not plugin.endswith(".py") and check_py):
				continue  # Python folders/files

			# Cleaning the name
			plugin = plugin.replace(".py", "")

			# Displaying each plugin name at the left of the screen
			if highlighted_plugins is None:
				if plugin in self.app.plugins.keys() or plist is not None:
					self.app.stdscr.addstr(i + 3, self.app.cols // 2 - len(plugin) // 2, plugin)
				else:
					self.app.stdscr.addstr(i + 3, self.app.cols // 2 - len(plugin) // 2, plugin, curses.color_pair(1))
			else:
				if plugin in highlighted_plugins:
					self.app.stdscr.addstr(i + 3, self.app.cols // 2 - len(plugin) // 2, plugin, curses.color_pair(4))
				else:
					self.app.stdscr.addstr(i + 3, self.app.cols // 2 - len(plugin) // 2, plugin)

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
			# Listing all plugins already installed
			installed_plugins_list = [
				file[:-3] for file in os.listdir(os.path.dirname(__file__)) \
				if not (file.startswith("__") or os.path.isdir(os.path.join(os.path.dirname(__file__), file))) \
					and file.endswith(".py")
			]
			self.list_plugins(plugins_list, getch=False, highlighted_plugins=installed_plugins_list)
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
		force_local = False
		# Tries to fetch already downloaded docs if self.list_online_plugins() returned None (an error occured)
		if plugins_list is None:
			msg_str = (
				"We are listing all library documentations you have downloaded.",
				"(They might not be up to date.)"
			)
			for i in range(len(msg_str)):
				self.app.stdscr.addstr(self.app.rows // 2 + 3 + i, self.app.cols // 2 - len(msg_str[i]) // 2, msg_str[i])

			# Lists all the files in the folder
			plugins_list = [
				file[:-3] for file in os.listdir(os.path.dirname(__file__))
				if not (file.startswith("__") or os.path.isdir(file)) and file.endswith(".md")
			]

			# Uses that as the plugins list
			force_local = True

			# Shows the user the list of available docs
			self.list_plugins(plist=plugins_list, getch=False, check_py=False)

		# Asks the user to input the plugin name
		self.app.stdscr.addstr(self.app.rows - 2, 0, "Input the name of the plugin to download, or leave blank to cancel.")
		user_wanted_plugin = input_text(self.app.stdscr)

		# If the user wrote nothing, it means he wants to cancel, so we stop the function there
		if user_wanted_plugin != "":
			# If the user specified an existing plugin name
			if user_wanted_plugin in plugins_list:
				# If force local is True, we just get the docs from the file
				if force_local is True:
					with open(
						os.path.join(os.path.dirname(__file__), f"{plugins_list[plugins_list.index(user_wanted_plugin)]}.md"),
						"r", encoding="utf-8"
					) as f:
						final_text = f.read()

				else:
					# We download the contents of the file from GitHub
					r = requests.get(f"https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Plugins/main/{user_wanted_plugin}.md")

					# If something went wrong with the request (the webpage didn't return an HTTP 200 (OK) code), we warn the user and exit the function
					if r.status_code != 200:
						return self._wrong_return_code_inconvenience()

					# If everything went well
					else:
						final_text = r.text

				# We clear the screen to make room for the docs display
				self.app.stdscr.clear()
				# Puts text into shape with markdown
				for i, line in enumerate(final_text.split("\n")):
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

		# Lists all the plugins available
		self.list_plugins(getch=False)

		# Shows a message to the user about the plugins he can delete
		self.app.stdscr.addstr(self.app.rows - 3, 0, "Input the name of the plugin you want to delete (or leave blank to cancel) :")

		# Asks the user to input the name of the plugin he wants to delete
		plugin_name = input_text(self.app.stdscr, position_y=self.app.rows - 2)

		# If the user inputted nothing, we cancel the operation
		if plugin_name != "":
			# We list all the plugins available
			plugins_list = tuple(
				plugin.replace(".py", "") for plugin in os.listdir(os.path.dirname(__file__)) if not (plugin.startswith("__")
				or os.path.isdir(os.path.join(os.path.dirname(__file__), plugin))
				or not plugin.endswith(".py"))
			)

			# If the plugin exists
			if plugin_name in plugins_list:
				def delete_plugin():
					# Deletes the plugin file
					os.remove(os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"))

					# If the documentation exists, deletes it as well
					try:
						os.remove(os.path.join(os.path.dirname(__file__), f"{plugin_name}.md"))
					except FileNotFoundError: pass

					# Shows a message to the user indicating that a plugin was deleted
					msg_str = f"Plugin {plugin_name} deleted."
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()

				# We display a confirmation menu for the user
				display_menu(self.app.stdscr, (
					("Yes", delete_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to delete the plugin '{plugin_name}' ?")

			# If the plugin doesn't exist, we show an error message and exit
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

		# If the user inputted nothing, we cancel the action
		if plugin_name != "":
			# We list all available plugins
			plugins_list = tuple(
				plugin.replace(".py", "") for plugin in os.listdir(os.path.dirname(__file__)) if not \
				(plugin.startswith("__")
				or os.path.isdir(os.path.join(os.path.dirname(__file__), plugin))
				or not plugin.endswith(".py"))
			)

			# If the plugin exists
			if plugin_name in plugins_list:
				def disable_plugin():
					# We move the plugin to the disabled_plugins folder
					os.rename(
						os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"),
						os.path.join(os.path.dirname(__file__), "disabled_plugins", f"{plugin_name}.py")
					)

					# We display a message confirming that the plugin was disabled
					msg_str = f"Plugin {plugin_name} disabled."
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()

				# We display a confirmation menu
				display_menu(self.app.stdscr, (
					("Yes", disable_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to disable the plugin '{plugin_name}' ?")

			# If the plugin doesn't seem to exist, we tell the user and exit
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

		# Lists all disabled plugins and asks to select the plugin to disable
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

		# If the user typed nothing, we cancel the action
		if plugin_name != "":
			# If the plugin exists
			if plugin_name + ".py" in plugins_list:
				def enable_plugin():
					# We move the plugin from the disabled_plugins folder to the active one
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

					# Showing a message indicating that the plugin has been loaded
					msg_str = f"Plugin {plugin_name} enabled !"
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.log(msg_str)
					self.app.stdscr.getch()

				# Displaying a confirmation menu
				display_menu(self.app.stdscr, (
					("Yes", enable_plugin),
					("No", lambda: None)
				), label=f"Are you sure you want to enable the plugin '{plugin_name}' ?")

			# If the plugin doesn't seem to be installed, we tell the user and exit
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
