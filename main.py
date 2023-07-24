__version__ = "0.3.1"

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform
from android_permissions import AndroidPermissions
import sqlite3
import os

from menu import Menu
from simplerec import SimpleRec
from running_projects import RunningProjects
from create_project import CreateProject
from usersettings import UserSettings
from gpshelper import GpsHelper


class MainApp(MDApp):
    def build(self):
        # Theming:
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.primary_hue = '700'
        self.theme_cls.accent_palette = 'Orange'
        self.theme_cls.material_style = 'M2'

        # Create Database connection:
        conn = sqlite3.connect(os.path.join("data", "fsurv.db"))
        cursor = conn.cursor()
        # Create the Species lists table
        cursor.execute("CREATE TABLE if not exists species_list(sciName text, vernacularName text, RL_status)")
        # Create the records Table
        cursor.execute("""CREATE TABLE if not exists records(records_id text, sciName text, vernacularName text,
                                       abundance text, timestamp text, lat real, lon real)""")
        conn.commit()
        conn.close()

        # Screensize for Desktop
        if platform == 'linux' or platform == 'win' or platform == 'macosx':
            from kivy.core.window import Window
            Window.size = (450, 950)
            print(platform)

        # Screen Handling
        screen_manager = ScreenManager()

        menu = Menu(name='menu')
        screen_manager.add_widget(menu)

        simple_rec = SimpleRec(name='simple_rec')
        screen_manager.add_widget(simple_rec)

        running_projects = RunningProjects(name='running_projects')
        screen_manager.add_widget(running_projects)

        create_project = CreateProject(name='create_project')
        screen_manager.add_widget(create_project)

        settings = UserSettings(name='settings')
        screen_manager.add_widget(settings)

        print("MainApp.build executed")
        return screen_manager

    def on_start(self):
        # Handle Permissions
        self.dont_gc = AndroidPermissions(self.start_app)

    def start_app(self):
        # Delete Permission functions to get rid of garbage.
        self.dont_gc = None


if __name__ == '__main__':
    MainApp().run()
