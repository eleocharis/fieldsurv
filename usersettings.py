from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivy.utils import platform
from collections import defaultdict
import pandas as pd
import sqlite3
import json
import os


Builder.load_file('usersettings.kv')


class UserSettings(MDScreen):
    prep_spec_lists = ObjectProperty()
    # collected buttons which go into the Card
    taxon_button_card = ObjectProperty()
    # this dictionary stores all button references.
    taxon_button_list = {}
    # Holds all species lists which are uploaded by the user
    species_list = pd.DataFrame()
    # Dict of genus keys with species epithet as values.
    genus_dict = defaultdict(list)
    # By user selected Taxon for autocompletion
    taxon_pull_list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # handle android folder system:
        if platform == 'android':
            self.working_dir = self.user_data_dir
        else:
            self.working_dir = os.getcwd()  # Set a fallback directory for other platforms

        self.create_buttons_from_tax_list(self.taxon_button_card, self.height, self.width)
        self.load_taxon_selections()
        self.load_user_settings()

        country_list = pd.read_csv(os.path.join(self.working_dir, 'data/country_lists_joined_adapted.csv'))

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
        # print(country_list)

    def create_buttons_from_tax_list(self, taxon_button_card, width, height):
        # This method loads up all available Species lists in the "species_lists" folder

        # Looks up, for which taxon (species groups) lists are available.
        spec_lists = []
        for root, dirs, files in os.walk(os.path.join(self.working_dir, 'data/species_lists')):
            for file in files:
                if file.endswith('.csv'):
                    spec_lists.append(os.path.join(root, file))

        print(spec_lists)
        # Creates a list of taxon out of the spec_country_taxon.csv
        taxon_list = [str(x).split("_")[-1][:-4] for x in spec_lists]

        # Prepare the widget structure:
        button_scroll_view = ScrollView(size_hint=(1, None), size=(width, "130dp"))
        stack_layout = StackLayout(size_hint_y=None, size=[width, height], padding=["8dp", 0], spacing="2dp")
        stack_layout.bind(minimum_height=stack_layout.setter('height'))

        for taxon in taxon_list:
            taxon_button = MDFillRoundFlatIconButton(text=taxon, id=taxon, icon='circle',
                                                     on_press=self.button_pressed)
            self.taxon_button_list[taxon] = taxon_button
            # print(self.taxon_button_list[taxon])
            stack_layout.add_widget(taxon_button)

        button_scroll_view.add_widget(stack_layout)
        taxon_button_card.add_widget(button_scroll_view)

        return self.taxon_button_list

    def button_pressed(self, button):
        if button.icon == 'circle':
            self.taxon_pull_list.append(button.text)
            button.icon = 'check-circle'
        else:
            self.taxon_pull_list.remove(button.text)
            button.icon = 'circle'

    def load_taxon_selections(self):
        # upload of user_settings at app startup
        if os.path.exists(os.path.join(self.working_dir, 'data/user_settings.json')):
            with open(os.path.join(self.working_dir, 'data/user_settings.json')) as us:
                user_settings = json.load(us)

            self.taxon_pull_list = user_settings["taxon"]

            # Check buttons for selected species lists.
            for taxon, button in self.taxon_button_list.items():
                if taxon in self.taxon_pull_list:
                    button.icon = 'check-circle'
                    print(taxon)
                    self.get_species_lists()

    def get_species_lists(self):
        # Uploads species lists for all selected taxon buttons into a dictionary.

        # Remove all previously loaded data_frames
        self.species_list = self.species_list.iloc[0:0]

        for taxon in self.taxon_pull_list:
            print(taxon)
            path = os.path.join(self.working_dir, "data/species_lists/spec_germany_" + taxon + ".csv")

            # Read the file into a dataframe (try because someone could delete a list while it is
            # still in the settingsfile than it crashes.
            try:
                new_lists = pd.read_csv(path)
            except:
                continue
            # Store the dataframe in the dictionary using the filename as the key
            # SPECIES_LISTS[taxon] = df
            self.species_list = pd.concat([self.species_list, new_lists], ignore_index = True, sort = False)

            # self.species_list.to_csv("test.csv", index=False)

        # Create Database connection:
        conn = sqlite3.connect(os.path.join(self.working_dir, "data/fsurv.db"))
        # Save the DataFrame to the SQLite database
        self.species_list.to_sql('species_list', conn, if_exists='replace')
        # Close connection.
        conn.commit()
        conn.close()

        # prepares the species lists into dictionaries, to filter for genus
        # and after only the species within the selected genus.
        self.genus_dict.clear()

        for index, row in self.species_list.iterrows():
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
                self.genus_dict[genus].append(species)
            except:
                pass
    def country_dropdown_callback(self, text_item):
        self.ids.country.text = text_item

    def language_dropdown_callback(self, text_item):
        self.ids.language.text = text_item


    def load_user_settings(self):
        # upload user_settings at app startup
        if os.path.exists(os.path.join(self.working_dir, 'data/user_settings.json')):
            with open(os.path.join(self.working_dir, 'data/user_settings.json')) as us:
                user_settings = json.load(us)

            self.ids.user_name.text = user_settings["user_name"]
            self.ids.institution.text = user_settings["institution"]
            self.ids.country.text = user_settings["country"]
            self.ids.language.text = user_settings["language"]

    def save_user_settings(self):
        print(self.taxon_pull_list)
        # saves all the user settings to the user_settings.json - file.
        dump_user_settings = {"user_name": self.ids.user_name.text, "institution": self.ids.institution.text,
                              "country": self.ids.country.text, "language": self.ids.language.text,
                              "taxon": self.taxon_pull_list}

        # take all usersettings from the settings fields
        json_object = json.dumps(dump_user_settings, indent=4)

        # Writing to sample.json
        with open(os.path.join(self.working_dir, 'data/user_settings.json'), 'w+') as outfile:
            outfile.write(json_object)

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
