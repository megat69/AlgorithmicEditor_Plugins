import curses

from plugin import Plugin

class FlyingBanana(Plugin):
	def __init__(self, app):
		super().__init__(app)

		self.banana = [
			['_'],
			['/', '/', '\\'],
			['V', ' ', ' ', '\\'],
			[' ', '\\', ' ', ' ', '\\', '_'],
			[' ', ' ', '\\', ',', "'", '.', '`', '-', '.'],
			[' ', ' ', ' ', '|', '\\', ' ', '`', '.', ' ', '`', '.', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', '(', ' ', '\\', ' ', ' ', '`', '.', ' ', '`', '-', '.', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '_', ',', '.', '-', ':'],
			[' ', ' ', ' ', ' ', ' ', '\\', ' ', '`', '.', ' ', ' ', ' ', '`', '-', '.', ' ', ' ', ' ', '`', '-', '.', '.', '_', '_', '_', '.', '.', '-', '-', '-', "'", ' ', ' ', ' ', '_', '.', '-', '-', "'", ' ', ',', "'", '/'],
			[' ', ' ', ' ', ' ', ' ', ' ', '`', '.', ' ', '`', '.', ' ', ' ', ' ', ' ', '`', '-', '.', '_', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '_', '_', '.', '.', '-', '-', "'", ' ', ' ', ' ', ' ', ',', "'", ' ', '/'],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '`', '.', ' ', '`', '-', '_', ' ', ' ', ' ', ' ', ' ', '`', '`', '-', '-', '.', '.', "'", "'", ' ', ' ', ' ', ' ', ' ', ' ', ' ', '_', '.', '-', "'", ' ', ',', "'"],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '`', '-', '_', ' ', '`', '-', '.', '_', '_', '_', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '_', '_', ',', '-', '-', "'", ' ', ' ', ' ', ',', "'"],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '`', '-', '.', '_', '_', ' ', ' ', '`', '-', '-', '-', '-', '"', '"', '"', ' ', ' ', ' ', ' ', '_', '_', '.', '-', "'"],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '`', '-', '-', '.', '.', '_', '_', '_', '_', '.', '.', '-', '-', "'"]
		]
		self.x_pos = 0


	def update_on_keypress(self, key:str):
		for i in range(len(self.banana)):
			for j in range(len(self.banana[i])):
				try:
					self.app.stdscr.addstr(10 + i, j + self.x_pos, self.banana[i][j], curses.color_pair(3))
				except curses.error:
					self.app.stdscr.addstr(10 + i, (j + self.x_pos) - self.app.cols, self.banana[i][j], curses.color_pair(3))

		self.x_pos += 1
		if self.x_pos > self.app.cols:
			self.x_pos = 0


def init(app):
	return FlyingBanana(app)