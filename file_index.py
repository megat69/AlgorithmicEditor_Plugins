import curses
import math
import os

from plugin import Plugin
from utils import input_text

# Tries to load the tabs plugin
try:
	from .tabs import TabsPlugin, Tab
except ImportError:
	TABS_PLUGIN_LOADED = False
else:
	TABS_PLUGIN_LOADED = True

APP_PLACEMENT_SHIFT = 30  # MIN VALUE : 2


class FileIndex(Plugin):
	"""
	Adds in the sidebar the list of files in the current directory.
	"""
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
		# If the tabs plugin is loaded, we store it
		if TABS_PLUGIN_LOADED:
			self.tabs_plugin = TabsPlugin(app)

		# Which file in the menu is currently selected
		self.selected_file_index = 0

		# Sets the translation
		self.translations = {
			"en": {
				"open_command": "Open/Exit file index",
				"display_command": "Show/Hide file index",
				"option_valid_files": "Only show valid files",
				"option_size": "Size of the file index",
				"size": "Enter the new size :"
			},
			"fr": {
				"open_command": "Ouvrir/Fermer l'index de fichiers",
				"display_command": "Afficher/Cacher l'index de fichiers",
				"option_valid_files": "Afficher uniquement les fichiers valides",
				"option_size": "Taille de l'index du fichier",
				"size": "Entrez la nouvelle taille :"
			}
		}

		# Are we currently moving in the index
		self.in_index = False
		self.add_command("fi", self.toggle_in_index, self.translate("open_command"), True)

		# Keeps in mind the minimum character to display next in the list
		self.min_char = 0

		# Whether to display the index
		self.display_index = True
		self.add_command("hi", self.toggle_display_index, self.translate("display_command"), True)

		# Emojis representing different file types
		self.file_types = {
			("algo", "txt"): "📝",
			("csv", "json", "xml", "yaml", "yml"): "📊",
			("xls", "xslx"): "📈",
			("ppt", "pptx"): "🎭",
			("doc", "docx", "pdf"): "🗃️",
			("jpg", "jpeg", "png", "gif", "bmp"): "📷",
			("mp4", "mov", "avi", "mkv"): "📹",
			("mp3", "wav", "ogg"): "🎵",
			("py",): "🐍",
			("php",): "🐘",
			("ipynb",): "📓",
			("ics",): "📆",
			("exe", "msi"): "🎮",
			("zip", "gz", "7z", "rar"): "📦",
			("html", "htm", "url"): "🌐"
		}


	def init(self):
		# Inits the tabs plugin if necessary
		if TABS_PLUGIN_LOADED and not self.tabs_plugin.was_initialized:
			self.tabs_plugin.init()
			self.tabs_plugin.was_initialized = True

		# Updates the shift of the line numbers so we can fit the file index at its left
		self.app.left_placement_shift = self.get_config("size_index", APP_PLACEMENT_SHIFT)

		# Added a way to change the size of the index
		self.add_option(self.translate("option_size"), lambda: self.config["size_index"], self.change_size_index)

		# Creates the current directory
		if "last_dir" not in self.config.keys():
			self.current_dir = os.getcwd()
			self.config["last_dir"] = self.current_dir
		else:
			self.current_dir = os.path.normpath(self.config["last_dir"])

		# Creates a curses color pair for the algo files
		self.green_pair = self.create_pair(
			curses.COLOR_GREEN
				if self.app.default_bg != curses.COLOR_GREEN else
			curses.COLOR_BLACK,
			self.app.default_bg
		)

		# Loads the config
		self.only_show_valid_files = self.get_config("only_show_valid_files", False)
		self.add_option(self.translate("option_valid_files"), lambda: self.only_show_valid_files, self.toggle_show_valid_files)

		# Overrides the app's default display text method
		self.default_display_text = self.app.display_text
		self.app.display_text = self.update_on_display

		# Shows the file index for the first time
		self.update_on_display()


	def toggle_display_index(self):
		"""
		Toggles whether to display the index.
		"""
		self.display_index = not self.display_index
		if self.display_index:
			self.app.left_placement_shift = self.config["size_index"]
		else:
			self.app.left_placement_shift = 0
			self.in_index = False
			self.app.stdscr.clear()
		self.update_on_display()


	def toggle_show_valid_files(self):
		"""
		Toggles whether to show only the valid files.
		"""
		self.only_show_valid_files = not self.only_show_valid_files
		self.config["only_show_valid_files"] = self.only_show_valid_files


	def toggle_in_index(self):
		""" Opens/Exits the file index. """
		self.in_index = not self.in_index and self.display_index
		self.app.input_locked = self.in_index
		if self.in_index:
			self.update_on_display()


	def change_size_index(self):
		"""
		Changes the size of the index.
		"""
		self.app.stdscr.addstr(
			self.app.rows // 2 - 1,
			self.app.cols // 2 - len(self.translate("size")) // 2,
			self.translate("size")
		)
		size = input_text(self.app.stdscr, self.app.cols // 2, self.app.rows // 2)

		# Checks if the size is int
		try:
			size = int(size)
			if 2 < size < self.app.cols - 1:
				self.config["size_index"] = size
		except ValueError:
			return

		# Finally changes the size
		self.app.left_placement_shift = self.config["size_index"]


	def update_on_display(self):
		"""
		Gets called after the display_text call.
		"""
		self.default_display_text()

		if not self.display_index: return
		# Draws a column right next to the line numbers to separate them from the file index
		for i in range(self.app.rows - 3 - self.app.top_placement_shift):
			self.app.stdscr.addstr(
				i + self.app.top_placement_shift,
				self.app.left_placement_shift - 2,
				"|"
			)
		if self.app.top_placement_shift > 0:
			self.app.stdscr.addstr(
				self.app.top_placement_shift,
				0,
				"_" * (self.app.left_placement_shift - 2) + " "
			)

		# Gets the formatted list of folders and files in the current directory
		menu_items = self.get_current_folder_files()

		# Displays each file in the current folder
		displayable_range_min = math.floor(self.selected_file_index / (self.app.rows - 3))
		for i, (filename, filepath) in enumerate(
			menu_items[
				displayable_range_min * (self.app.rows - 3 - self.app.top_placement_shift)
				: # Only shows the menu items that should be visible
				(displayable_range_min + 1) * (self.app.rows - 3 - self.app.top_placement_shift)
			]
		):
			# Gets the color scheme of the filename
			attrs = curses.A_NORMAL
			if not self.only_show_valid_files and filename[-5:] == ".algo":  # If the filename ends in .algo, we display it green
				attrs |= curses.color_pair(self.green_pair) | curses.A_BOLD
			if (i + displayable_range_min * (self.app.rows - 3)) == self.selected_file_index and self.in_index:  # If the file is selected, highlights it
				attrs |= curses.A_REVERSE

			# Displays the name of the file
			self.app.stdscr.addstr(
				i + self.app.top_placement_shift + (self.app.top_placement_shift > 0), 0,
				filename[:2] + filename[2 + self.min_char:self.app.left_placement_shift - 3 + self.min_char],
				attrs
			)


	def update_on_keypress(self, key: str):
		"""
		Every tick, displays the file index and updates it.
		"""
		if not self.display_index: return
		if self.in_index:
			menu_items = self.get_current_folder_files()
			# If the key is up or down, we move in the folder list accordingly
			if key == "KEY_UP":
				self.selected_file_index -= 1
			elif key == "KEY_DOWN":
				self.selected_file_index += 1
			if key == "KEY_LEFT":
				self.min_char -= 1
				self.min_char = max(self.min_char, 0)
			elif key == "KEY_RIGHT":
				self.min_char += 1
			# Wraps the index around its length
			self.selected_file_index = ((self.selected_file_index % len(menu_items)) + len(menu_items)) % len(menu_items)

			# If the key is Enter or Tab, we move into the selected folder or open the selected file
			if key in ("\n", "\t"):
				if self.open_new_file(menu_items): return


	def get_current_folder_files(self):
		""" Lists all the files in the current directory """
		current_files_list = os.listdir(self.current_dir)

		# Sorts the files by folders and files
		folders_list = []
		files_list = []
		for element in current_files_list:
			if os.path.isdir(os.path.join(self.current_dir, element)):
				folders_list.append(element)
			else:
				if not self.only_show_valid_files or element.split(".")[-1] in ("algo", "txt"):  # Checks that extension is a valid type
					files_list.append(element)
		menu_items = [("📁 ../", os.path.join(self.current_dir, "../"))]
		menu_items.extend([
			(f"📁 {name}", os.path.join(self.current_dir, name)) \
			for name in folders_list
		])
		menu_items.extend([
			(f"{self.get_emoji(name)} {name}", os.path.normpath(os.path.join(self.current_dir, name))) \
			for name in files_list
		])
		return menu_items


	def get_emoji(self, filename: str) -> str:
		"""
		Returns an emoji to use next to the filename based on the file extension.
		:param filename: The name of the file (including extension).
		:return: An emoji.
		"""
		# Sets as the return emoji the default file emoji
		return_emoji = "📄"

		if "." in filename:
			# Gets the file extension if it has one
			extension = filename.split(".")[-1].lower()

			# Based on the extension, changes the return emoji
			for extensions_list, emoji in self.file_types.items():
				if extension in extensions_list:
					return_emoji = emoji

		return return_emoji


	def open_new_file(self, menu_items: list) -> bool:
		"""
		Opens a new file.
		:return: Whether to stop the function there.
		"""
		if os.path.isdir(menu_items[self.selected_file_index][1]):  # If folder
			self.current_dir = menu_items[self.selected_file_index][1]
			self.config["last_dir"] = self.current_dir
			self.selected_file_index = 0
			# Reloads the file index
			self.update_on_display()
			return True

		else:  # If file
			if not TABS_PLUGIN_LOADED:
				# Opens in place
				self.app.open(menu_items[self.selected_file_index][1])

			else:  # If the tabs plugin is loaded
				# Before we open the file, we test if there is only one empty tab with no name or anything,
				# and if so, we replace it
				if len(self.tabs_plugin.tabs) == 1 and self.tabs_plugin.tabs[0] == Tab(
					self.tabs_plugin.translate("untitled"),
					"",
					0,
					"clipboard",
					[]
				):
					self.tabs_plugin.tabs.pop()

				# We open the file in a new tab
				with open(menu_items[self.selected_file_index][1], encoding="utf-8") as f:
					self.tabs_plugin.tabs.append(Tab(
						os.path.split(os.path.normpath(menu_items[self.selected_file_index][1]))[-1],
						f.read(),
						0,
						menu_items[self.selected_file_index][1],
						[]
					))
					self.tabs_plugin.current_tab = len(self.tabs_plugin.tabs) - 1
					self.tabs_plugin._reset_tab()

			# Makes the user return to edit mode
			self.toggle_in_index()

		return False


def init(app):
	return FileIndex(app)
