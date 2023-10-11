import sys
import socket

from plugin import Plugin

try:
	from .stopwatch import StopwatchPlugin
except ImportError:
	STOPWATCH_PLUGIN_INSTALLED = False
	print("You need to install the `stopwatch` plugin to use the exam plugin !")
else:
	STOPWATCH_PLUGIN_INSTALLED = True


class ExamPlugin(Plugin):
	def __init__(self, app):
		super().__init__(app)


class EmptyExamPlugin(Plugin):
	"""
	An empty plugin, so it doesn't affect anybody.
	"""
	def __init__(self, app):
		super().__init__(app)


def init(app):
	if "--exam" in sys.argv and STOPWATCH_PLUGIN_INSTALLED:
		return ExamPlugin(app)
	else:
		return EmptyExamPlugin(app)
