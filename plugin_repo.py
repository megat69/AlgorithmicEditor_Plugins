import curses
import requests
from bs4 import BeautifulSoup
import os
import importlib
import re
import hashlib

from plugin import Plugin
from utils import display_menu, input_text

# Creates the 'disabled_plugins' folder if it doesn't exist
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'disabled_plugins')):
	os.mkdir(os.path.join(os.path.dirname(__file__), 'disabled_plugins'))


# ------------ TRANSLATIONS ------------
translations = {
	"en": {
		"manage_plugins": "Manage plugins",
		"nb_plugins_loaded": "{} plugins loaded",
		"manage_plugins_menu": {
			"list_plugins": "List plugins",
			"download_plugins": "Download plugins",
			"delete_plugins": "Delete plugins",
			"disable_plugins": "Disable plugins",
			"enable_plugins": "Enable plugins",
			"reload_plugins": "Reload plugins",
			"read_online_plugins_doc": "Read online plugins documentation",
			"download_theme": "Download theme",
			"plugins_with_updates": "Check for plugin updates",
			"leave": "Leave"
		},
		"list_plugins": {
			"available": "available",
			"title": "-- {available} {listed_element} list --",
			"faulty_plugins": "Faulty plugins displayed in red."
		},
		"list_online_plugins": {
			"connection_error": "Please check your connection and try again."
		},
		"plugin_fetching_error": [
			"There have been a problem during the fetching of",
			"the plugins list online. We apologize for the inconvenience."
		],
		"download_plugins": {
			"input_plugin_name": "Input the name of the plugin to download, or leave blank to cancel.",
			"plugin_installed": "The plugin '{user_wanted_plugin}' has been successfully installed !",
			"reload_plugins_option": "Do you want to reload the plugins ?",
			"install_all_plugins_option": "Do you want to install all plugins ? This will update every plugin you have installed.",
			"successfully_installed_all": "The plugins have been successfully installed !",
			"nonexistent_plugin": "The plugin '{user_wanted_plugin}' doesn't seem to exist."
		},
		"docs_plugin": {
			"docs_list": [
				"We are listing all library documentations you have downloaded.",
				"(They might not be up to date.)"
			],
			"input_name": "Input the name of the plugin to download, or leave blank to cancel.",
			"nonexistent_docs": "The plugin documentation for '{user_wanted_plugin}' doesn't seem to exist."
		},
		"delete_plugin": {
			"input_name": "Input the name of the plugin you want to delete (or leave blank to cancel) :",
			"plugin_deleted_confirm": "Plugin {plugin_name} deleted.",
			"confirm_delete_plugin": "Are you sure you want to delete the plugin '{plugin_name}' ?",
			"non_installed_plugin": "The plugin '{plugin_name}' doesn't seem to be installed."
		},
		"disable_plugins": {
			"input_name": "Input the name of the plugin you want to {state} (or leave blank to cancel) :",
			"plugin_disabled": "Plugin {plugin_name} {state}.",
			"confirm_disable_plugins": "Are you sure you want to {state} the plugin '{plugin_name}' ?",
			"disable": "disable",
			"disabled": "disabled"
		},
		"enable_plugins": {
			"enable": "enable",
			"enabled": "enabled"
		},
		"download": {
			"check_connection": "Please check your connection and try again."
		},
		"download_theme": {
			"input_name": "Input the name of the theme to download, or leave blank to cancel.",
			"successfully_installed": "The theme '{user_wanted_theme}' has been successfully installed !",
			"changes_taken_effect": "Changes should have already taken effect.",
			"non_existent_theme": "The theme '{user_wanted_theme}' doesn't seem to exist."
		},
		"requests": {
			"awaiting_response": "Awaiting response from server...",
			"downloading_docs":  "Downloading docs of plugin {user_wanted_plugin}...",
			"downloading_theme": "Downloading theme {user_wanted_theme}..."
		},
		"plugins_with_updates": {
			"status": {
				"none": "No updates needed",
				"update_available": "Update available",
				"pending": "Pending...",
				"error": "An error occurred."
			}
		}
	},
	"fr": {
		"manage_plugins": "Gérer les plugins",
		"nb_plugins_loaded": "{} plugins chargés",
		"manage_plugins_menu": {
			"list_plugins": "Liste des plugins",
			"download_plugins": "Télécharger des plugins",
			"delete_plugins": "Supprimer des plugins",
			"disable_plugins": "Désactiver des plugins",
			"enable_plugins": "Activer des plugins",
			"reload_plugins": "Actualiser les plugins",
			"read_online_plugins_doc": "Lire la documentation de plugins en ligne",
			"download_theme": "Télécharger un thème",
			"plugins_with_updates": "Vérifier si des mises à jour sont disponibles",
			"leave": "Quitter"
		},
		"list_plugins": {
			"available": "disponibles",
			"title": "-- liste des {listed_element} {available} --",
			"faulty_plugins": "Plugins avec une erreur affichés en rouge."
		},
		"list_online_plugins": {
			"connection_error": "Vérifiez votre connection et réessayez."
		},
		"plugin_fetching_error": [
			"Un problème est survenu durant la récupération de",
			"la liste des plugins en ligne. Veuillez nous excuser de la gène occasionnée."
		],
		"download_plugins": {
			"input_plugin_name": "Entrez le nom du plugin a télécharger, ou laissez-vide pour annuler.",
			"plugin_installed": "Le plugin '{user_wanted_plugin}' a été installé avec succès !",
			"reload_plugins_option": "Voulez-vous recharger les plugins ?",
			"install_all_plugins_option": "Voulez-vous installer tous les plugins ? Cela mettra à jour tous vos plugins.",
			"successfully_installed_all": "Les plugins ont été installés avec succès !",
			"nonexistent_plugin": "Le plugin '{user_wanted_plugin}' n'a pas l'air d'exister."
		},
		"docs_plugin": {
			"docs_list": [
				"Nous listons la documentation de tous les plugins que vous avez téléchargé.",
				"(Elles peuvent être obsolète.)"
			],
			"input_name": "Entrez le nom du plugin à télécharger, ou laissez vide pour annuler.",
			"nonexistent_docs": "La documentation du plugin '{user_wanted_plugin}' n'a pas l'air d'exister."
		},
		"delete_plugin": {
			"input_name": "Entrez le nom du plugin que vous souhaitez supprimer (ou laissez vide pour annuler) :",
			"plugin_deleted_confirm": "Le plugin {plugin_name} a été supprimé.",
			"confirm_delete_plugin": "Voulez-vous vraiment supprimer le plugin '{plugin_name}' ?",
			"non_installed_plugin": "Le plugin '{plugin_name}' ne semble pas être installé."
		},
		"disable_plugins": {
			"input_name": "Entrez le nom du plugin que vous voulez {state} (ou laissez vide pour annuler) :",
			"plugin_disabled": "Le plugin {plugin_name} a été {state}.",
			"confirm_disable_plugins": "Voulez-vous vraiment {state} le plugin '{plugin_name}' ?",
			"disable": "désactiver",
			"disabled": "désactivé"
		},
		"enable_plugins": {
			"enable": "activer",
			"enabled": "activé"
		},
		"download": {
			"check_connection": "Veuillez vérifier votre connexion et réessayer."
		},
		"download_theme": {
			"input_name": "Entrez le nom du thème à télécharger, ou laissez vide pour annuler.",
			"successfully_installed": "Le thème '{user_wanted_theme}' a été installé avec succès !",
			"changes_taken_effect": "Les changements ont déjà dû être appliqués.",
			"non_existent_theme": "Le thème '{user_wanted_theme}' n'a pas l'air d'exister."
		},
		"requests": {
			"awaiting_response": "En attente d'une réponse du serveur...",
			"downloading_docs":  "Téléchargement de la documentation du plugin {user_wanted_plugin}...",
			"downloading_theme": "Téléchargement du thème {user_wanted_theme}..."
		},
		"plugins_with_updates": {
			"status": {
				"none": "Aucune mise à jour nécessaire",
				"update_available": "Mise à jour disponible",
				"pending": "En attente...",
				"error": "Une erreur est survenue."
			}
		}
	}
}
# --------------------------------------


def r_get(url: str) -> requests.Response:
	"""
	Tries to make a request to the given URL. If so, returns it. If a connection error occurs,
		returns a code Response with a status code of -1.
	:param url: A URL.
	:return: A requests object.
	"""
	try:
		r = requests.get(url)
	except requests.exceptions.ConnectionError:
		r = requests.Response()
		r.status_code = -1
	return r


class PluginRepo(Plugin):
	# Modify to use another plugin repo
	PLUGIN_REPO_NAME   = "AlgorithmicEditor_Plugins"  # Name of the repo
	PLUGIN_REPO_USER   = "megat69"                    # Username of the repo creator
	PLUGIN_REPO_BRANCH = "main"                       # Branch to pull plugins from

	# Modify to use another theme repo
	THEME_REPO_NAME   = "AlgorithmicEditor_Themes"   # Name of the repo
	THEME_REPO_USER   = "megat69"                    # Username of the repo creator
	THEME_REPO_BRANCH = "main"                       # Branch to pull plugins from

	# Constants for the plugin repository URL. Should not be touched.
	PLUGINS_REPO_INDIVIDUAL_FILE = f"https://raw.githubusercontent.com/{PLUGIN_REPO_USER}/{PLUGIN_REPO_NAME}/{PLUGIN_REPO_BRANCH}"
	PLUGINS_REPO_URL = f"https://github.com/{PLUGIN_REPO_USER}/{PLUGIN_REPO_NAME}/tree/{PLUGIN_REPO_BRANCH}/"
	THEME_REPO_URL = f"https://github.com/{THEME_REPO_USER}/{THEME_REPO_NAME}/tree/{THEME_REPO_BRANCH}/"

	__singleton = None

	def __new__(cls, *args, **kwargs):
		"""
		Creates a singleton of the class.
		"""
		if cls.__singleton is None:
			cls.__singleton = super().__new__(cls)
		return cls.__singleton

	def __init__(self, app):
		super().__init__(app)

		# Sets the translations
		self.translations = translations

		# Creates the use vars
		self.manage_plugins_menu = False
		self.selected_menu_item = 0

		# Creates the command
		self.add_command("r", self.manage_plugins, self.translate("manage_plugins"))


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
			# Clears the screen
			self.app.stdscr.clear()

			# Displays the amount of plugins loaded at the bottom right of the screen
			self.app.stdscr.addstr(
				self.app.rows - 4,
				20,
				self.translate("nb_plugins_loaded").format(str(len(self.app.plugins.keys())))
			)
			self.app.stdscr.addstr(
				self.app.rows - 4,
				20 + self.translate("nb_plugins_loaded").find("{"),
				str(len(self.app.plugins.keys())),
				curses.color_pair(self.app.color_pairs["instruction"])
			)

			# Displays the possible options
			display_menu(self.app.stdscr, (
				(self.translate("manage_plugins_menu", "list_plugins"), self.list_plugins),
				(self.translate("manage_plugins_menu", "download_plugins"), self.download_plugins),
				(self.translate("manage_plugins_menu", "delete_plugins"), self.delete_plugins),
				(self.translate("manage_plugins_menu", "disable_plugins"), self.disable_plugins),
				(self.translate("manage_plugins_menu", "enable_plugins"), self.enable_plugins),
				(self.translate("manage_plugins_menu", "reload_plugins"), self.reload_plugins),
				(self.translate("manage_plugins_menu", "read_online_plugins_doc"), self.docs_plugins),
				(self.translate("manage_plugins_menu", "download_theme"), self.download_theme),
				(self.translate("manage_plugins_menu", "plugins_with_updates"), self.plugins_with_updates),
				(self.translate("manage_plugins_menu", "leave"), self.leave)
			), self.selected_menu_item, clear=False, space_out_last_option=True, allow_key_input=True)


	def leave(self):
		"""
		Closes the menu by setting the variable controlling the while loop to False.
		"""
		self.manage_plugins_menu = False


	def list_plugins(
			self, plist: list = None,
			getch: bool = True, check_py: bool = True,
			highlighted_plugins: list = None, listed_element: str = "PLUGINS"
	):
		"""
		Lists all the installed plugins, and displays in red the faulty ones.
		:param plist: A list of plugins to show the user. If None, will look into the plugins folder. Default is None.
		:param getch: Whether to do a getch at the after the list is fully displayed.
		:param check_py: Whether to ask for py files.
		:param highlighted_plugins: Will highlight the plugins in this list. None by default.
		:param listed_element: The name of what is listed. "Plugins" by default.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 0

		# Initializing a counter
		i = 0

		# Creating the message displayed to the user
		msg = self.translate(
			"list_plugins", "title", listed_element=listed_element,
			available = self.translate("list_plugins", "available") if plist is not None else ''
		).upper()
		self.app.stdscr.addstr(0, self.app.cols // 2 - len(msg) // 2, msg, curses.A_BOLD)

		# If no plugins list was provided to the function, we add another message
		if plist is None:
			msg = self.translate("list_plugins", "faulty_plugins")
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

			# Gets the color of the plugin
			plugin_display_color = curses.A_NORMAL
			# If no plugin is highlighted by the user
			if highlighted_plugins is None:
				# If the plugin is not in the loaded plugins (thus is faulty), we display it in red.
				if plugin not in self.app.plugins.keys() and plist is None:
					plugin_display_color |= curses.color_pair(1)

			# If the user defined highlighted plugins, they get highlighted in blue
			else:
				if plugin in highlighted_plugins:
					plugin_display_color |= curses.color_pair(4)

			# Displaying each plugin name at the left of the screen
			self.app.stdscr.addstr(i + 3, self.app.cols // 2 - len(plugin) // 2, plugin, plugin_display_color)

			# Incrementing i by 1, we are forced to do this because we ignore some files at the
			# start of the loop.
			i += 1

		# Makes a pause
		if getch:
			self.app.stdscr.getch()


	def list_online_plugins(self, show_user:bool=True):
		"""
		Lists the online plugins available.
		:param show_user: Whether to show the user the list of plugins or not.
		"""
		# Tries to connect to the URL on GitHub
		try:
			# We display a message to the user
			self.app.stdscr.clear()
			msg_str = self.translate("requests", "awaiting_response")
			self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)

			# Makes a request towards the server
			r = r_get(PluginRepo.PLUGINS_REPO_URL)
			self.app.stdscr.clear()
		# If the connection fails, it tells the user and exits the function
		except requests.exceptions.ConnectionError:
			self._wrong_return_code_inconvenience()
			msg_str = self.translate("list_online_plugins", "connection_error")
			self.app.stdscr.addstr(self.app.rows // 2 + 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
			return None

		# If the status code is not HTTP 200 (OK), we tell the user that something went wrong.
		if r.status_code != 200:
			self._wrong_return_code_inconvenience()

		# If everything worked, we parse the webpage to find all references to .py files
		else:
			# Uses BeautifulSoup to parse all the plugin names (every item in the request ending in ".py")
			soup = BeautifulSoup(r.text, 'html.parser')
			plugins = soup.find_all(title=re.compile("\.py$"))

			# Lists the available plugins to the user
			plugins_list = [e.extract().get_text() for e in plugins]

			# Shows the list of installed plugins to the user if they want to
			if show_user:
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
		self.app.stdscr.addstr(self.app.rows - 2, 0, self.translate("download_plugins", "input_plugin_name"))
		user_wanted_plugin = input_text(self.app.stdscr)

		# If the user wrote nothing, it means he wants to cancel, so we stop the function there
		if user_wanted_plugin != "":
			# If the user specified an existing plugin name
			if user_wanted_plugin in plugins_list:
				# We call the install plugin function
				self._install_plugin(user_wanted_plugin)

				# We tell the user that the plugin has been successfully installed
				msg_str = self.translate("download_plugins", "plugin_installed", user_wanted_plugin=user_wanted_plugin)
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()

				# We ask the user if he wants to reload the plugins, and if so, we do it
				self._prompt_reload_plugins()

			# If the user wants to download all plugins
			elif user_wanted_plugin == "all":
				def _install_all_plugins():
					for plugin in self.list_online_plugins(show_user=False):
						if plugin != "flying_banana":
							self._install_plugin(plugin)

				display_menu(self.app.stdscr, (
					(self.app.get_translation("yes"), _install_all_plugins),
					(self.app.get_translation("no"), lambda: None)
				),
				label = self.translate("download_plugins", "install_all_plugins_option")
				)

				# We tell the user that the plugin has been successfully installed
				msg_str = self.translate("download_plugins", "successfully_installed_all")
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()

				# We ask the user if he wants to reload the plugins, and if so, we do it
				self._prompt_reload_plugins()

			# If the user specified a non-existing plugin name, we show him an error and exit the function
			else:
				msg_str = self.translate(
					"download_plugins", "nonexistent_plugin", user_wanted_plugin=user_wanted_plugin
				)
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()


	def _prompt_reload_plugins(self):
		"""
		Prompts the user a menu to reload the plugins.
		"""
		display_menu(
			self.app.stdscr,
			(
				(self.app.get_translation("yes"), self.reload_plugins),
				(self.app.get_translation("no"), lambda: None)
			),
			label=self.translate("download_plugins", "reload_plugins_option")
		)


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
			msg_str = self.translate("docs_plugin", "docs_list")
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
		self.app.stdscr.addstr(self.app.rows - 2, 0, self.translate("docs_plugin", "input_name"))
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
					# We display a message to the user
					self.app.stdscr.clear()
					msg_str = self.translate("requests", "downloading_docs").format(user_wanted_plugin=user_wanted_plugin)
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)

					# We download the contents of the file from GitHub
					r = r_get(f"{PluginRepo.PLUGINS_REPO_INDIVIDUAL_FILE}/{user_wanted_plugin}.md")
					self.app.stdscr.clear()

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
				msg_str = self.translate("docs_plugin", "nonexistent_docs", user_wanted_plugin=user_wanted_plugin)
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
		self.app.stdscr.addstr(self.app.rows - 3, 0, self.translate("delete_plugin", "input_name"))

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

					# Unloads the plugin
					del self.app.plugins[plugin_name]

					# Shows a message to the user indicating that a plugin was deleted
					msg_str = self.translate("delete_plugin", "plugin_deleted_confirm", plugin_name=plugin_name)
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()

				# We display a confirmation menu for the user
				display_menu(self.app.stdscr, (
					(self.app.get_translation("yes"), delete_plugin),
					(self.app.get_translation("no"), lambda: None)
				), label=self.translate("delete_plugin", "confirm_delete_plugin", plugin_name=plugin_name))

			# If the plugin doesn't exist, we show an error message and exit
			else:
				msg_str = self.translate("delete_plugin", "non_installed_plugin", plugin_name=plugin_name)
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
					self.app.plugins[plugin][-1].plugin_name = plugin
					if plugin not in self.app.plugins_config.keys():
						self.app.plugins_config[plugin] = {}
					self.app.plugins[plugin][-1].config = self.app.plugins_config[plugin]
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

		# Lists the plugins afterwards
		self.list_plugins()


	def disable_plugins(self):
		"""
		Disables an existing plugin.
		"""
		# Selects this function by default from the menu
		self.selected_menu_item = 3

		# Lists all plugins and asks to select the plugin to disable
		self.list_plugins(getch=False)
		self.app.stdscr.addstr(self.app.rows - 3, 0, self.translate(
			"disable_plugins", "input_name",
			state=self.translate("disable_plugins", "disable")
		))
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

					# We remove the key from the dict of plugins
					del self.app.plugins[plugin_name]

					# We display a message confirming that the plugin was disabled
					msg_str = self.translate(
						"disable_plugins", "plugin_disabled", plugin_name=plugin_name,
						state=self.translate("disable_plugins", "disabled")
					)
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()

				# We display a confirmation menu
				display_menu(self.app.stdscr, (
					(self.app.get_translation("yes"), disable_plugin),
					(self.app.get_translation("no"), lambda: None)
				), label=self.translate(
					"disable_plugins", "confirm_disable_plugins", plugin_name=plugin_name,
					state = self.translate("disable_plugins", "disable")
				))

			# If the plugin doesn't seem to exist, we tell the user and exit
			else:
				msg_str = self.translate("delete_plugin", "non_installed_plugin", plugin_name=plugin_name)
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

		# Lists the plugins
		self.list_plugins(getch=False, plist=list(plugins_list))

		# Asks the user to input a name for a plugin to enable
		self.app.stdscr.addstr(self.app.rows - 3, 0, self.translate(
			"disable_plugins", "input_name",
			state=self.translate("enable_plugins", "enable")
		))
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
					msg_str = self.translate(
						"disable_plugins", "plugin_disabled",
						plugin_name=plugin_name,
						state=self.translate("enable_plugins", "enabled")
					)
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.log(msg_str)
					self.app.stdscr.getch()

				# Displaying a confirmation menu
				display_menu(self.app.stdscr, (
					(self.app.get_translation("yes"), enable_plugin),
					(self.app.get_translation("no"), lambda: None)
				), label=self.translate(
					"disable_plugins", "confirm_disable_plugins",
					state=self.translate("enable_plugins", "enable"),
					plugin_name=plugin_name
				))

			# If the plugin doesn't seem to be installed, we tell the user and exit
			else:
				msg_str = self.translate("delete_plugin", "non_installed_plugin", plugin_name=plugin_name)
				self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
				self.app.stdscr.getch()


	def download_theme(self):
		"""
		Allows the user to download a theme to replace the new one.
		"""
		# Tries to connect to the URL on GitHub
		try:
			# We display a message to the user
			self.app.stdscr.clear()
			msg_str = self.translate("requests", "awaiting_response")
			self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)

			# Makes the request
			r = r_get(PluginRepo.THEME_REPO_URL)
			self.app.stdscr.clear()
		# If the connection fails, it tells the user and exits the function
		except requests.exceptions.ConnectionError:
			self._wrong_return_code_inconvenience()
			msg_str = self.translate("download", "check_connection")
			self.app.stdscr.addstr(self.app.rows // 2 + 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
			return None

		# If the status code is not HTTP 200 (OK), we tell the user that something went wrong.
		if r.status_code != 200:
			self._wrong_return_code_inconvenience()

		# If everything worked, we parse the webpage to find all references to .ini files (themes)
		else:
			soup = BeautifulSoup(r.text, 'html.parser')
			themes = soup.find_all(title=re.compile("\.ini$"))

			# Lists the available plugins to the user
			themes_list = [e.extract().get_text()[:-4] for e in themes]

			# We show this list to the user
			self.list_plugins(themes_list, listed_element="THEMES", check_py=False, getch=False)

			# Asks the user to input the plugin name
			self.app.stdscr.addstr(self.app.rows - 2, 0, self.translate("download_theme", "input_name"))
			user_wanted_theme = input_text(self.app.stdscr)

			# If the user wrote nothing, it means he wants to cancel, so we stop the function there
			if user_wanted_theme != "":
				# If the user specified an existing theme name
				if user_wanted_theme in themes_list:
					# We display a message to the user
					self.app.stdscr.clear()
					msg_str = self.translate("requests", "downloading_theme").format(user_wanted_theme=user_wanted_theme)
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)

					# We download the contents of the file from GitHub
					r = r_get(f"https://raw.githubusercontent.com/megat69/AlgorithmicEditor_Themes/main/{user_wanted_theme}.ini")
					self.app.stdscr.clear()

					# If something went wrong with the request (the webpage didn't return an HTTP 200 (OK) code), we warn the user and exit the function
					if r.status_code != 200:
						self._wrong_return_code_inconvenience()

					# If everything went well
					else:
						# We dump the contents of the theme file into the softwares theme file
						with open(os.path.join(os.path.dirname(__file__), "../theme.ini"), "w", encoding="utf-8") as f:
							f.write(r.text)

						# Reloads the changes
						self.app.reload_theme()

						# We tell the user that the theme has been successfully installed
						msg_str = self.translate(
							"download_theme", "successfully_installed", user_wanted_theme=user_wanted_theme
						)
						self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
						msg_str = self.translate("download_theme", "changes_taken_effect")
						self.app.stdscr.addstr(self.app.rows // 2 + 1, self.app.cols // 2 - len(msg_str) // 2, msg_str)
						self.app.stdscr.getch()

				# If the user specified a non-existing theme name, we show him an error and exit the function
				else:
					msg_str = self.translate("download_theme", "non_existing_theme")
					self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)
					self.app.stdscr.getch()


	def plugins_with_updates(self):
		"""
		Checks for updates in each of the installed plugins.
		"""
		status = {
			0: "none",
			1: "update_available",
			2: "pending",
			3: "error"
		}

		# Gets the list of installed plugins (into a set because no two plugins will have the same name,
		# so I prefer the fast lookup)
		plugin_list = [
			[
				file[:-3],
				2
			]
			for file in os.listdir(os.path.dirname(__file__)) if file[-3:] == ".py"
		]

		# Keeps in mind which plugin is selected
		selected_plugin = 0

		# Keeps in mind whether the menu is open
		menu_open = True

		# Keeps in mind which key the user pressed
		key = ''


		def display_plugins_menu():
			"""
			Displays the menu of plugins.
			"""
			self.app.stdscr.clear()
			for i, (plugin_name, plugin_status) in enumerate(plugin_list):
				# Gets the status text of the plugin
				plugin_status_text = f"{plugin_name} - {self.translate('plugins_with_updates', 'status', status[plugin_status])}"

				# Gets the style of the plugin
				plugin_style = curses.A_NORMAL
				if selected_plugin == i:
					plugin_style |= curses.A_REVERSE
					if plugin_status == 1:
						plugin_style |= curses.color_pair(self.app.color_pairs["instruction"])
				if plugin_status == 3:
					plugin_style |= curses.color_pair(self.app.color_pairs["statement"])

				# Displays the status of each plugin
				self.app.stdscr.addstr(
					i + 2,
					self.app.cols // 2 - plugin_status_text.rfind("-"),
					plugin_status_text,
					plugin_style
				)


		# Gets the state of each of the plugins before activating the menu
		cached_plugins = {}
		for i, (plugin_name, plugin_status) in enumerate(plugin_list):
			r = r_get(f"{PluginRepo.PLUGINS_REPO_INDIVIDUAL_FILE}/{plugin_name}.py")

			# In case of an error
			if r.status_code != 200:
				plugin_list[i][1] = 3

			# If everything went well
			else:
				cached_plugins[plugin_name] = r.text

				# Checks the SHA-256 hash of both the documents
				with open(os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"), "r", encoding="utf-8") as f:
					checksum_local = hashlib.sha256(f.read().encode("utf-8")).hexdigest()
				checksum_server = hashlib.sha256(r.text.encode("utf-8")).hexdigest()

				# If the checksum is identical, sets the status to 'none', otherwise to 'update_available'
				if checksum_local == checksum_server:
					plugin_list[i][1] = 0
				else:
					plugin_list[i][1] = 1

			# Draws the menu
			display_plugins_menu()
			self.app.stdscr.refresh()


		while menu_open:
			# Runs through the list of all installed plugins
			display_plugins_menu()
			self.app.stdscr.addstr(
				len(plugin_list) + 3,
				self.app.cols // 2 - len(self.app.get_translation("cancel")) // 2,
				self.app.get_translation("cancel"),
				curses.A_REVERSE if selected_plugin == len(plugin_list) else curses.A_NORMAL
			)

			# Gets the key pressed
			key = self.app.stdscr.getkey()

			# If the key is an up/down arrow key, modifies the selected plugin
			if key == "KEY_UP":
				selected_plugin -= 1
			elif key == "KEY_DOWN":
				selected_plugin += 1
			wrap_around = len(plugin_list) + 1
			selected_plugin = ((selected_plugin % wrap_around) + wrap_around) % wrap_around

			# If the key is Enter, executes the corresponding action
			if key in ("\n", "\t"):
				# If the user selected to exit
				if selected_plugin == len(plugin_list):
					menu_open = False

				# If the user selected a plugin
				else:
					# If the plugin can be updated
					if plugin_list[selected_plugin][1] == 1:
						plugin_name = plugin_list[selected_plugin][0]
						if plugin_name in cached_plugins:
							with open(os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"), "w", encoding="utf-8") as f:
								f.write(cached_plugins[plugin_name])
							# We then try to download the plugin's docs
							r = r_get(f"{PluginRepo.PLUGINS_REPO_INDIVIDUAL_FILE}/{plugin_name}.md")
							# If everything went well, we simply dump the contents of the documentation file into another file
							# And if something went wrong, we simply don't do it and don't warn the user, he'll download it later
							if r.status_code == 200:
								with open(os.path.join(os.path.dirname(__file__), f"{plugin_name}.md"), "w", encoding="utf-8") as f:
									f.write(r.text)
						else:
							self._install_plugin(plugin_name)
						plugin_list[selected_plugin][1] = 0


	def update_on_keypress(self, key:str):
		"""
		Triggers the :r if F6 is hit, and reloads the plugins/themes if F5 is hit.
		"""
		if key == "KEY_F(6)":
			self.manage_plugins()
		elif key == "KEY_F(5)":
			self.reload_plugins()
			self.app._declare_color_pairs()


	def _wrong_return_code_inconvenience(self):
		"""
		Tells the user about an inconvenience during download attempt.
		"""
		# Throws a return code to the user about an error while fetching the plugins
		for i, msg_str in enumerate(self.translate("plugin_fetching_error")):
			self.app.stdscr.addstr(self.app.rows // 2 + i, self.app.cols // 2 - len(msg_str) // 2, msg_str)
		self.app.stdscr.getch()


	def _install_plugin(self, plugin_name: str):
		"""
		Installs the given plugin from GitHub.
		:param plugin_name: The name of the plugin to install.
		"""
		# We display a message to the user
		self.app.stdscr.clear()
		msg_str = f"Downloading plugin {plugin_name}..."
		self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)

		# We download the contents of the file from GitHub
		r = r_get(f"{PluginRepo.PLUGINS_REPO_INDIVIDUAL_FILE}/{plugin_name}.py")

		# If something went wrong with the request (the webpage didn't return an HTTP 200 (OK) code), we warn the user and exit the function
		if r.status_code != 200:
			self._wrong_return_code_inconvenience()

		# If everything went well
		else:
			# We dump the contents of the plugin file into a file of the corresponding name
			with open(os.path.join(os.path.dirname(__file__), f"{plugin_name}.py"), "w", encoding="utf-8") as f:
				f.write(r.text)

			# We display a message to the user
			self.app.stdscr.clear()
			msg_str = self.translate("requests", "downloading_docs").format(user_wanted_plugin=plugin_name)
			self.app.stdscr.addstr(self.app.rows // 2, self.app.cols // 2 - len(msg_str) // 2, msg_str)

			# We then try to download the plugin's docs
			r = r_get(f"{PluginRepo.PLUGINS_REPO_INDIVIDUAL_FILE}/{plugin_name}.md")
			# If everything went well, we simply dump the contents of the documentation file into another file
			# And if something went wrong, we simply don't do it and don't warn the user, he'll download it later
			if r.status_code == 200:
				with open(os.path.join(os.path.dirname(__file__), f"{plugin_name}.md"), "w", encoding="utf-8") as f:
					f.write(r.text)
			self.app.stdscr.clear()


def init(app) -> PluginRepo:
	return PluginRepo(app)
