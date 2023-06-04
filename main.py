from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from menu import Menu
from simplerec import SimpleRec
from create_project import CreateProject


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

        create_project = CreateProject(name='create_project')
        screen_manager.add_widget(create_project)

        return screen_manager


if __name__ == '__main__':
    MainApp().run()
