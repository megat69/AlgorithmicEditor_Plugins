from plugin import Plugin
from datetime import datetime
import curses

#-------------------------------------------------------




class DatePlugin(Plugin):


    __singleton = None

    def __new__(cls, *args, **kwargs):
        """
        Creates a singleton of the class.
        """
        if cls.__singleton is None:
            cls.__singleton = super().__new__(cls)
        return cls.__singleton


    def __init__(self,app):
        super().__init__(app)

        self.color = 0
        self.translations = {
            "en": {
                "display_date": "Display the date"
            },

            "fr": {
                "display_date": "Afficher la date"
            }
        }
        self.display_date = self.get_config("display_date", True)
        self.add_option(self.translate("display_date"), lambda:self.display_date, self.toggle_display_date)
        self.add_command("date", self.toggle_display_date, self.translate("display_date"), True)


    def init(self):
        self.color = self.create_pair(curses.COLOR_CYAN, self.app.default_bg)

    def toggle_display_date(self):
        self.display_date = not self.display_date
        self.config["display_date"] = self.display_date


    def update_on_keypress(self, key: str):
        if self.display_date:
            date = datetime.now()
            dateD_str = date.strftime("%d/%m/%Y")
            dateH_str = date.strftime("%H:%M:%S")
            self.app.stdscr.addstr(self.app.rows-1, self.app.cols-1-len(dateH_str), dateH_str, curses.color_pair(self.color))
            self.app.stdscr.addstr(self.app.rows-2, self.app.cols-1-len(dateD_str), dateD_str, curses.color_pair(self.color))




def init(app):
    return DatePlugin(app)
