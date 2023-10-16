from functools import partial

import requests
from bs4 import BeautifulSoup
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import List, Union

from plugin import Plugin
from utils import display_menu

try:
	from .plugin_repo import PluginRepo, r_get
except ImportError:
	raise ImportError("Updater plugin needs plugin_repo to function !")


class Updater(Plugin):
	# Modify to use another app repo
	REPO_NAME = "AlgorithmicEditor"  # Name of the repo
	REPO_USER = "megat69"  # Username of the repo creator
	REPO_BRANCH = "main"  # Branch to pull plugins from

	# Constants for the repository URL. Should not be touched.
	REPO_INDIVIDUAL_FILE = f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/{REPO_BRANCH}"
	REPO_URL = f"https://github.com/{REPO_USER}/{REPO_NAME}/tree/{REPO_BRANCH}/"
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
		self.translations = {
			"en": {
				"check_updates_on_startup": "Check updates on startup",
				"check_for_updates": "Check for updates",
				"do_you_want_to_update": "An update is available. Do you want to update now ?",
				"yes": "Yes",
				"no": "No",
				"download_in_progress": "Downloading update. Please wait...",
				"update_applied": "Update applied. Please reboot the editor to get the changes.",
				"no_updates_available": "No updates available !"
			},
			"fr": {
				"check_updates_on_startup": "Rechercher des mises à jour au lancement",
				"check_for_updates": "Rechercher des mises à jour",
				"do_you_want_to_update": "Une mise à jour est disponible. Voulez-vous l'effectuer ?",
				"yes": "Oui",
				"no": "Non",
				"download_in_progress": "Téléchargement de la mise à jour en cours. Veuillez patienter...",
				"update_applied": "Mise à jour appliquée. Veuillez redémarrer l'éditeur pour recevoir les changements.",
				"no_updates_available": "Pas de mises à jour disponibles"
			}
		}

		# Loads the plugin repo
		self.plugin_repo = PluginRepo(app)

		# Adds a command to manually check for updates
		self.add_command("u", partial(self.check_for_updates, True), self.translate("check_for_updates"))


	def init(self):
		# If the plugin repo is not initialized, we initialize it
		if self.plugin_repo.was_initialized is False:
			self.plugin_repo.init()
			self.plugin_repo.was_initialized = True

		# Defaults the config
		self.get_config("check_updates_on_startup", True)

		# Adds an option to check for an update on startup
		self.add_option(
			self.translate("check_updates_on_startup"),
			lambda: self.get_config("check_updates_on_startup", True),
			self.toggle_check_updates_on_startup
		)

		# If the user chose to check the updates on startup, we do so
		if self.config["check_updates_on_startup"]:
			self.check_for_updates()


	def toggle_check_updates_on_startup(self):
		"""
		Toggles whether to check updates on startup.
		"""
		self.config["check_updates_on_startup"] = not self.config["check_updates_on_startup"]


	def check_for_updates(self, show_message_if_no_updates: bool = False):
		"""
		Checks for updates, if one is available, asks the user, and if the user accepts, downloads the update then
			restarts the editor.
		:param show_message_if_no_updates: Shows a message in the command bar if no updates were available.
		"""
		if os.path.exists(os.path.join(os.path.dirname(__file__), '..', ".git")):
			os.system("git pull")
		else:
			updatable_files = check_for_updates()
			if updatable_files:
				display_menu(
					self.app.stdscr,
					(
						(self.translate("yes"), partial(self.update, updatable_files)),
						(self.translate("no"), lambda: None)
					),
					label=self.translate("do_you_want_to_update")
				)
			elif show_message_if_no_updates:
				self.app.stdscr.addstr(self.app.rows - 1, 3, self.translate("no_updates_available"))


	def update(self, updatable_files: List[str]):
		"""
		Updates all the given files to they server version.
		:param updatable_files: A list of files to be updated
		"""
		self.app.stdscr.clear()
		self.app.stdscr.addstr(
			self.app.rows // 2,
			self.app.cols // 2 - len(self.translate("download_in_progress")) // 2,
			self.translate("download_in_progress")
		)
		self.app.stdscr.refresh()
		for file in updatable_files:
			file_path = os.path.join(os.path.dirname(__file__), '..', file)
			try:
				r = r_get(Updater.REPO_INDIVIDUAL_FILE + "/" + file)
			except requests.exceptions.ConnectionError:
				continue
			if r.status_code != 200:
				continue
			with open(file_path, 'w', encoding='utf-8') as f:
				f.write(r.text)
		self.app.stdscr.clear()
		self.app.stdscr.addstr(
			self.app.rows // 2,
			self.app.cols // 2 - len(self.translate("update_applied")) // 2,
			self.translate("update_applied")
		)
		self.app.stdscr.refresh()
		self.app.stdscr.getch()


def check_hash(filename: str) -> bool:
	"""
	Compares the hash between the local and distant file of the same name.
	:param filename: The name of the file to be checked.
	:return: True if the hash is different, False is the hash is identical.
	"""
	file_path = os.path.join(os.path.dirname(__file__), '..', filename)
	if not os.path.exists(file_path):
		return True

	if os.path.isdir(file_path):
		return False

	try:
		r = r_get(Updater.REPO_INDIVIDUAL_FILE + "/" + filename)
	except requests.exceptions.ConnectionError:
		return False

	if r.status_code != 200:
		return False

	# If everything worked fine, we can open the current version of the file
	with open(file_path, encoding="utf-8") as f:
		checksum_local = hashlib.sha256(f.read().encode("utf-8")).hexdigest()
	checksum_server = hashlib.sha256(r.text.encode("utf-8")).hexdigest()

	# With both checksums computed, we return whether they are different
	return checksum_server != checksum_local


def check_for_updates() -> Union[List[str], False]:
	"""
	Checks if an update is available in the repository, and returns which files changed.
	:return: A list of all the files changedor False in case an error occured.
	"""
	# Tries to connect to the URL on GitHub
	try:
		r = r_get(Updater.REPO_URL)
	# If the connection fails, we exit the function with a given return code
	except requests.exceptions.ConnectionError:
		return False

	# If the status code is not HTTP 200 (OK), we exit the function with a given return code
	if r.status_code != 200:
		return False

	# If everything worked, we parse the webpage to find all references to all the files files
	else:
		# Uses BeautifulSoup to parse all the names
		soup = BeautifulSoup(r.text, 'html.parser')
		files_list = soup.select('.js-navigation-open')
		files_list_text = [f.text.strip() for f in files_list]
		for lang in ("en", "fr"):
			files_list_text.append(f"translations/translations_{lang}.json")

		# Now that all the file names have been found, we find all the hashes of the current installed files
		# and compare them to the online files. If they do not match, we simply add them to the list of files to return.
		files_to_return = []
		with ThreadPoolExecutor(max_workers=6) as executor:
			for file in files_list_text:
				future = executor.submit(check_hash, file)
				if future.result():
					files_to_return.append(file)
		return files_to_return


def init(app):
	return Updater(app)
