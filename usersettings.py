from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from pathlib import Path
from collections import defaultdict
import json
import pandas as pd

# Looks up which for which taxon (species groups) lists are available.
p = Path('../fieldsurv/data/species_lists').glob("**/*.csv")
files = [x for x in p if x.is_file()]
TAXON_LIST = [str(x).split("_")[-1][:-4] for x in files]  # Creates a list of taxon out of the spec_country_taxon.csv
SPECIES_LISTS = {}  # Holds all species lists which are uploaded by the
SPEC_AUT_C_DICT = defaultdict(list)

Builder.load_file('usersettings.kv')


class UserSettings(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_buttons_from_tax_list()
        self.taxon_pull_list = []  # This list will
        self.load_user_settings()

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

    def create_buttons_from_tax_list(self):
        global TAXON_LIST
        self.taxon_button_list = {}  # this list stores all buttons references.

        # Prepere the widget structure:
        scroll_view = ScrollView(size_hint=(1, None), size=(self.width, "130dp"))
        stack_layout = StackLayout(size_hint_y=None, size=[self.width, self.height], padding=["8dp", 0], spacing="2dp")
        stack_layout.bind(minimum_height=stack_layout.setter('height'))

        for taxon in TAXON_LIST:
            taxon_button = MDFillRoundFlatIconButton(text=taxon, id=taxon, icon='circle', on_press=self.button_pressed)
            self.taxon_button_list[taxon] = taxon_button
            stack_layout.add_widget(taxon_button)

        scroll_view.add_widget(stack_layout)
        self.ids.taxon_buttons.add_widget(scroll_view)

    def button_pressed(self, button):
        if button.icon == 'circle':
            self.taxon_pull_list.append(button.text)
            button.icon = 'check-circle'
        else:
            self.taxon_pull_list.remove(button.text)
            button.icon = 'circle'

    def get_species_lists(self):
        # Uploads species lists for all selected taxon buttons. into a dictionary.
        # key = taxon, item = DataFrame (csv of the Taxon)
        global SPECIES_LISTS
        SPECIES_LISTS.clear()
        for taxon in self.taxon_pull_list:
            path = str("data/species_lists/spec_germany_" + taxon + ".csv")
            # Read the file into a dataframe
            df = pd.read_csv(path)
            # Store the dataframe in the dictionary using the filename as the key
            SPECIES_LISTS[taxon] = df

        print(SPECIES_LISTS.keys())

        # prepares the species lists into dictionaries, to filter for genus
        # and after only the species within the selected genus.
        global SPEC_AUT_C_DICT
        SPEC_AUT_C_DICT.clear()

        for taxon in SPECIES_LISTS:
            for index, row in SPECIES_LISTS[taxon].iterrows():
                sp = row["sciName"]
                try:
                    genus = sp.split(" ", maxsplit=1)[0]
                except:
                    genus = []
                try:
                    species = sp.split(" ", maxsplit=1)[1]
                except:
                    species = []
                try:
                    SPEC_AUT_C_DICT[genus].append(species)
                except:
                    pass

    def save_user_settings(self):
        # saves all the user settings to the user_settings.json - file.
        dump_user_settings = {"user_name": self.ids.user_name.text, "institution": self.ids.institution.text,
                              "country": self.ids.country.text, "language": self.ids.language.text,
                              "taxon": self.taxon_pull_list}

        # take all usersettings from the fields
        json_object = json.dumps(dump_user_settings, indent=4)

        # Writing to sample.json
        with open("user_settings.json", "w+") as outfile:
            outfile.write(json_object)

    def load_user_settings(self):
        # upload of user_settings at app startup
        if Path('user_settings.json').exists():
            with open('user_settings.json') as us:
                user_settings = json.load(us)

            self.ids.user_name.text = user_settings["user_name"]
            self.ids.institution.text = user_settings["institution"]
            self.ids.country.text = user_settings["country"]
            self.ids.language.text = user_settings["language"]
            self.taxon_pull_list = user_settings["taxon"]

            for taxon, button in self.taxon_button_list.items():
                if taxon in self.taxon_pull_list:
                    button.icon = 'check-circle'

            self.get_species_lists()


if __name__ == '__main__':
    class MainApp(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = 'Teal'
            self.theme_cls.primary_hue = '700'
            self.theme_cls.accent_palette = 'Orange'

            screen_manager = MDScreenManager()

            user_data = UserSettings(name='user_data')
            screen_manager.add_widget(user_data)

            return screen_manager

    MainApp().run()
