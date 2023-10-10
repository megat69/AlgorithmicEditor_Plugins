import curses
import time

from plugin import Plugin


class StopwatchPlugin(Plugin):
	PERCENTAGE_MEDIUM = 0.5
	PERCENTAGE_LOW = 0.25
	PERCENTAGE_VERY_LOW = 0.1


	def __init__(self, app):
		super().__init__(app)
		self.translations = {
			"en": {
				"enable_stopwatch": "Enable stopwatch",
				"label": "Select the time left to the stopwatch"
			},
			"fr": {
				"enable_stopwatch": "Compte à rebours",
				"label": "Entrez le temps restant du chronomètre"
			}
		}
		self.enabled = False
		self.end_time = time.time()
		self.start_time = time.time()
		self.add_option(self.translate("enable_stopwatch"), lambda: '', self.enable_stopwatch)
		self.stopwatch_value = [0, 0, 0]
		self.prevent_key_input_on_stop = False  # TODO if True make sure the user cannot add characters upon stopwatch end

		# Prepares the colors
		self.high_time_left_color = 0
		self.medium_time_left_color = 0
		self.low_time_left_color = 0


	def init(self):
		# Initializes the curses colors
		self.high_time_left_color = self.create_pair(curses.COLOR_GREEN, self.app.default_bg)
		self.medium_time_left_color = self.create_pair(curses.COLOR_YELLOW, self.app.default_bg)
		self.low_time_left_color = self.create_pair(curses.COLOR_RED, self.app.default_bg)


	def enable_stopwatch(self):
		"""
		Enables the stopwatch and shows a menu to set up the time.
		"""
		self.enabled = True

		# Shows the menu
		menu_items = self.stopwatch_value
		current_menu_item = 0
		key = ''
		while key != '\n':
			# Lets the user move around with tab, shift tab, and the side arrow keys
			if key in ('\t', 'KEY_RIGHT'):
				current_menu_item += 1
				current_menu_item %= len(menu_items)
			elif key in ('KEY_BTAB', 'KEY_LEFT'):
				current_menu_item -= 1
				if current_menu_item < 0:
					current_menu_item = len(menu_items) - 1
			elif key.isdigit():
				if menu_items[current_menu_item] == 0:
					menu_items[current_menu_item] = int(key)
				else:
					menu_items[current_menu_item] *= 10
					menu_items[current_menu_item] += int(key)
				# Sanitizes the value
				if current_menu_item != 0 and menu_items[current_menu_item] > 60:
					menu_items[current_menu_item - 1] += menu_items[current_menu_item] // 60
					menu_items[current_menu_item] %= 60
			elif key in ("\b", "\0", "KEY_DC"):
				menu_items[current_menu_item] = 0

			# Clears the screen
			self.app.stdscr.clear()

			# Displays the label
			message_str = self.translate("label")
			self.app.stdscr.addstr(
				self.app.rows // 2 - 2,
				self.app.cols // 2 - len(message_str) // 2,
				message_str
			)

			# Displays each element of the menu
			menu_str = ":".join((str(e).zfill(2) for e in menu_items))
			self.app.stdscr.addstr(
				self.app.rows // 2,
				self.app.cols // 2 - 4,
				menu_str
			)
			# Calculates the offset for the highlighted element
			offset = (-4, -1, 2)[current_menu_item]
			self.app.stdscr.addstr(
				self.app.rows // 2,
				self.app.cols // 2 + offset,
				str(menu_items[current_menu_item]).zfill(2),
				curses.A_REVERSE
			)

			# Refreshes the screen
			self.app.stdscr.refresh()
			key = self.app.stdscr.getkey()

		# Calculates the target time based on the inputted number
		self.stopwatch_value = menu_items
		self.end_time = int(time.time()) + self.stopwatch_value[2] + \
			self.stopwatch_value[1] * 60 + self.stopwatch_value[0] * 3600
		self.start_time = int(time.time())

		# Disables the stopwatch if all values are 0
		if all(value == 0 for value in self.stopwatch_value):
			self.enabled = False


	def fixed_update(self):
		"""
		Updates and displays the current time left
		"""
		if self.enabled:
			if any(value != 0 for value in self.stopwatch_value):
				current_time = int(time.time())
				time_left = self.end_time - current_time

				# Updates the stopwatch value
				self.stopwatch_value[2] = time_left % 60
				self.stopwatch_value[1] = (time_left // 60) % 60
				self.stopwatch_value[0] = time_left // 3600

				# Gets the correct color
				percentage_time_left = time_left / (self.end_time - self.start_time)
				blink = curses.A_NORMAL
				if percentage_time_left < StopwatchPlugin.PERCENTAGE_LOW:
					color = self.low_time_left_color
					if percentage_time_left < StopwatchPlugin.PERCENTAGE_VERY_LOW and time_left % 2 == 0:
						blink = curses.A_REVERSE
				elif percentage_time_left < StopwatchPlugin.PERCENTAGE_MEDIUM:
					color = self.medium_time_left_color
				else:
					color = self.high_time_left_color
			else:
				color = self.low_time_left_color
				blink = curses.A_REVERSE

			# Displays the current value
			self.app.stdscr.addstr(
				self.app.rows - 4,
				self.app.cols - 9,
				":".join((str(e).zfill(2) for e in self.stopwatch_value)),
				curses.color_pair(color) | blink
			)



def init(app):
	return StopwatchPlugin(app)
