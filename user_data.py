from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.animation import Animation
from kivymd.uix.chip import MDChip
from pathlib import Path
import pandas as pd

# Load species lists.
p = Path('../fieldsurv/data/species_lists').glob("**/*.csv")
files = [x for x in p if x.is_file()]
df_names = [str(x).split("_")[-1][:-4] for x in files]

SPECIES_LISTS = {}

for file in files:
    for name in df_names:
        # Read the file into a dataframe
        df = pd.read_csv(file)
        # Store the dataframe in the dictionary using the filename as the key
        SPECIES_LISTS[name] = df

Builder.load_file('user_data.kv')


class UserData(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_chips_from_av_lists()

        country_list = pd.read_csv('data/country_lists_joined_adapted.csv')

        # print(country_list)

        countries = [
            {"text": f'{item}',
             "viewclass": 'OneLineListItem',
             "on_release": lambda x=item: self.country_dropdown_callback(x)
             } for item in country_list["title"]

        ]
        self.country_dropdown = MDDropdownMenu(
            caller=self.ids.country_button,
            items=countries,
            width_mult=4)

        languages = [
            {"text": f'{item}',
             "viewclass": 'OneLineListItem',
             "on_release": lambda x=item: self.language_dropdown_callback(x)
             } for item in pd.unique(country_list.language)

        ]
        self.language_dropdown = MDDropdownMenu(
            caller=self.ids.language_button,
            items=languages,
            width_mult=4)

    def country_dropdown_callback(self, text_item):
        self.ids.country.text = text_item

    def language_dropdown_callback(self, text_item):
        self.ids.language.text = text_item

    def removes_marks_all_chips(self):
        for instance_chip in self.ids.chip_box.children:
            if instance_chip.active:
                instance_chip.active = False

    def create_chips_from_av_lists(self):
        global SPECIES_LISTS
        for taxon in SPECIES_LISTS:
            taxon_chip = MyChip(text=taxon, id=taxon)
            self.ids.taxon_chips.add_widget(taxon_chip)


class MyChip(MDChip):
    icon_check_color = (0, 0, 0, 1)
    text_color = (0, 0, 0, 0.5)
    _no_ripple_effect = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(active=self.set_chip_bg_color)
        self.bind(active=self.set_chip_text_color)

    def set_chip_bg_color(self, instance_chip, active_value: int):
        '''
        Will be called every time the chip is activated/deactivated.
        Sets the background color of the chip.
        '''

        self.md_bg_color = (
            self.theme_cls.primary_palette
            if active_value
            else (
                self.theme_cls.accent_palette
                if self.theme_cls.theme_style == "Light"
                else (
                    self.theme_cls.bg_light
                    if not self.disabled
                    else self.theme_cls.disabled_hint_text_color
                )
            )
        )

    def set_chip_text_color(self, instance_chip, active_value: int):
        Animation(
            color=(0, 0, 0, 1) if active_value else (0, 0, 0, 0.5), d=0.2
        ).start(self.ids.label)




if __name__ == '__main__':
    class MainApp(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = 'Teal'
            self.theme_cls.primary_hue = '700'
            self.theme_cls.accent_palette = 'Orange'

            screen_manager = ScreenManager()

            user_data = UserData(name='user_data')
            screen_manager.add_widget(user_data)

            return screen_manager
    MainApp().run()
