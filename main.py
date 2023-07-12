__version__ = "0.2.1"

# import logfile_redirect
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
from working_dir import working_dir
import sqlite3
import os

from menu import Menu
from simplerec import SimpleRec
from running_projects import RunningProjects
from create_project import CreateProject
from usersettings import UserSettings

# Set app size
Window.size = (450, 950)


class MainApp(MDApp):
    def build(self):
        # Theming:
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.primary_hue = '700'
        self.theme_cls.accent_palette = 'Orange'

        # File path handling
        # handle android folder system:
        if platform == 'android':
            self.working_dir = self.user_data_dir
        else:
            self.working_dir = os.getcwd()

            # Create Database connection:
        conn = sqlite3.connect(os.path.join(working_dir, "data/fsurv.db"))
        # Create a Cursor:
        cursor = conn.cursor()
        # Create the Species table
        cursor.execute("CREATE TABLE if not exists species_list(sciName text, vernacularName text, RL_status)")
        # Create the record Table
        cursor.execute("""CREATE TABLE if not exists records(records_id text, sciName text, vernacularName text,
                       abundance text, timestamp text, lat real, lon real)""")
        # Commit our changes and close connection.
        conn.commit()
        conn.close()

        # Screen Handling
        screen_manager = MDScreenManager()

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

        return screen_manager


if __name__ == '__main__':
    MainApp().run()
