from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from pathlib import Path
import pandas as pd

from menu import Menu
from simplerec import SimpleRec
from running_projects import RunningProjects
from create_project import CreateProject
from user_data import UserData


# Load species lists.
p = Path('data/species_lists').glob("**/*.csv")
files = [x for x in p if x.is_file()]

SPECIES_LISTS = {}

for file in files:
    # Read the file into a dataframe
    df = pd.read_csv(file)
    # Store the dataframe in the dictionary using the filename as the key
    SPECIES_LISTS[file] = df

# Set app size
Window.size = (450, 950)


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.primary_hue = '700'
        self.theme_cls.accent_palette = 'Orange'

        screen_manager = ScreenManager()

        menu = Menu(name='menu')
        screen_manager.add_widget(menu)

        simple_rec = SimpleRec(name='simple_rec')
        screen_manager.add_widget(simple_rec)

        running_projects = RunningProjects(name='running_projects')
        screen_manager.add_widget(running_projects)

        create_project = CreateProject(name='create_project')
        screen_manager.add_widget(create_project)

        user_data = UserData(name='user_data')
        screen_manager.add_widget(user_data)

        return screen_manager


if __name__ == '__main__':
    MainApp().run()
