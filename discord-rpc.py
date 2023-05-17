"""
Discord Rich Presence plugin.
"""
import os
try:
	from pypresence import Presence
except ImportError:
	import sys
	os.system(f"\"{sys.executable}\" -m pip install pypresence")
	from pypresence import Presence
import time

from plugin import Plugin


class DiscordRPCPlugin(Plugin):
	def __init__(self, app):
		super().__init__(app)
		self.translations = {
			"en": {
				"error": "Rich Presence has been disabled, since the following error occurred :",
				"state": "{nb_chars} characters !",
				"details": {
					"known": "Editing {file}",
					"unknown": "Editing an unsaved file"
				}
			},
			"fr": {
				"error": "Rich Presence a été désactivé, car l'erreur suivante s'est produite :",
				"state": "{nb_chars} caractères !",
				"details": {
					"known": "Dans {file}",
					"unknown": "Dans un fichier non sauvegardé"
				}
			}
		}
		self.rpc_enabled = True  # Whether the plugin should connect to discord RPC
		self.cooldown = 0  # A cooldown to update discord RPC
		self.start_time = int(time.time())  # When the app was started
		try:
			self.RPC = Presence("1108408802602139759")
			self.RPC.connect()
		except Exception as e:
			self.rpc_enabled = False
			print(self.translate("error"), e)
			raise e


	def __del__(self):
		self.RPC.close()

	def update_on_keypress(self, key: str):
		"""
		Updates Rich Presence.
		"""
		# Updates the RPC cooldown
		if self.rpc_enabled is True:
			if self.cooldown + 15 < time.time():
				self.cooldown = time.time()
				try:
					if self.app.last_save_action == "clipboard":
						details = self.translate("details", "unknown")
					else:
						details = self.translate(
							"details", "unknown",
							file=os.path.split(os.path.normpath(self.app.last_save_action))[-1]
						)
					self.RPC.update(
						details=details,
						state=self.translate("state", nb_chars=str(len(self.app.current_text))),
						start=self.start_time
					)
				except Exception as e:
					self.rpc_enabled = False
					print(self.translate("error"), e)


def init(app):
	return DiscordRPCPlugin(app)
