import curses
import math
import os

from plugin import Plugin
# Tries to load the tabs plugin
try:
	from .tabs import TabsPlugin, Tab
except ImportError:
	TABS_PLUGIN_LOADED = False
else:
	TABS_PLUGIN_LOADED = True


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

		# Updates the shift of the line numbers so we can fit the file index at its left
		self.app.left_placement_shift = 30  # MIN VALUE : 2

		# Which file in the menu is currently selected
		self.selected_file_index = 0

		# Are we currently moving in the index
		self.in_index = False
		self.add_command("fi", self.toggle_in_index, "Open/Exit file index", True)


	def init(self):
		# Inits the tabs plugin if necessary
		if TABS_PLUGIN_LOADED and not self.tabs_plugin.was_initialized:
			self.tabs_plugin.init()
			self.tabs_plugin.was_initialized = True

		# Creates the current directory
		if self.app.last_save_action in ("clipboard", ""):
			self.current_dir = os.getcwd()
		else:
			self.current_dir = "/".join(os.path.split(os.path.normpath(self.app.last_save_action))[:-1])

		# Creates a curses color pair for the algo files
		curses.init_pair(
			12,
			curses.COLOR_GREEN
				if self.app.default_bg != curses.COLOR_GREEN else
			curses.COLOR_BLACK,
			self.app.default_bg
		)

		# Loads the config
		if "only_show_valid_files" in self.config.keys():
			self.only_show_valid_files = self.config["only_show_valid_files"]
		else:
			self.config["only_show_valid_files"] = False
			self.only_show_valid_files = False
		self.add_option("Only show valid files", lambda: self.only_show_valid_files, self.toggle_show_valid_files)

		# Shows the file index for the first time
		self.update_on_keypress("")


	def toggle_show_valid_files(self):
		"""
		Toggles whether to show only the valid files.
		"""
		self.only_show_valid_files = not self.only_show_valid_files


	def toggle_in_index(self):
		""" Opens/Exits the file index. """
		self.in_index = not self.in_index
		self.app.input_locked = self.in_index
		if self.in_index:
			self.update_on_keypress("")


	def update_on_keypress(self, key: str):
		"""
		Every tick, displays the file index and updates it.
		"""
		# Draws a column right next to the line numbers to separate them from the file index
		for i in range(self.app.rows - 3):
			self.app.stdscr.addstr(
				i,
				self.app.left_placement_shift - 2,
				"|"
			)

		# Gets the formatted list of folders and files in the current directory
		menu_items = self.get_current_folder_files()

		if self.in_index:
			# If the key is up or down, we move in the folder list accordingly
			if key == "KEY_UP":
				self.selected_file_index -= 1
			elif key == "KEY_DOWN":
				self.selected_file_index += 1
			# Wraps the index around its length
			self.selected_file_index = ((self.selected_file_index % len(menu_items)) + len(menu_items)) % len(menu_items)

			# If the key is Enter or Tab, we move into the selected folder or open the selected file
			if key in ("\n", "\t"):
				if self.open_new_file(menu_items): return

		# Displays each file in the current folder
		displayable_range_min = math.floor(self.selected_file_index / (self.app.rows - 3))
		for i, (filename, filepath) in enumerate(
			menu_items[
				displayable_range_min * (self.app.rows - 3)
				: # Only shows the menu items that should be visible
				(displayable_range_min + 1) * (self.app.rows - 3)
			]
		):
			# Gets the color scheme of the filename
			attrs = curses.A_NORMAL
			if not self.only_show_valid_files and filename[-5:] == ".algo":  # If the filename ends in .algo, we display it green
				attrs |= curses.color_pair(12) | curses.A_BOLD
			if (i + displayable_range_min * (self.app.rows - 3)) == self.selected_file_index and self.in_index:  # If the file is selected, highlights it
				attrs |= curses.A_REVERSE

			# Displays the name of the file
			self.app.stdscr.addstr(
				i, 0, filename[:self.app.left_placement_shift - 3], attrs
			)


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
			(f"📄 {name}", os.path.normpath(os.path.join(self.current_dir, name))) \
			for name in files_list
		])
		return menu_items


	def open_new_file(self, menu_items: list) -> bool:
		"""
		Opens a new file.
		:return: Whether to stop the function there.
		"""
		if os.path.isdir(menu_items[self.selected_file_index][1]):  # If folder
			self.current_dir = menu_items[self.selected_file_index][1]
			self.selected_file_index = 0
			# Reloads the file index
			self.update_on_keypress("")
			return True

		else:  # If file
			if not TABS_PLUGIN_LOADED:
				# Opens in place
				self.app.open(menu_items[self.selected_file_index][1])

			else:  # If the tabs plugin is loaded
				# We open the file in a new tab
				with open(menu_items[self.selected_file_index][1]) as f:
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
