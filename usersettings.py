from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from collections import defaultdict
import pandas as pd
import threading
import sqlite3
import json
import os

Builder.load_file('usersettings.kv')


class UserSettings(Screen):
    # collected buttons which go into the Card
    taxon_button_card = ObjectProperty()
    # this dictionary stores all button references.
    taxon_button_list = {}
    # Dict of genus keys with species epithet as values.
    genus_dict = defaultdict(list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # all available species lists uploaded by the user
        self.taxon_list = []
        # By user selected Taxon for autocompletion
        self.taxon_pull_list = []
        self.create_buttons_from_tax_list(self.taxon_button_card, self.height, self.width)
        self.load_taxon_selections()
        self.load_user_settings()
        print("UserSettings.__init__ executed")

    def create_buttons_from_tax_list(self, taxon_button_card, width, height):
        # This method loads up all available Species lists in the "species_lists" folder
        # and creates buttons which can be selected by the user.

        # Looks up, for which taxon (species groups) lists are available.
        for root, dirs, files in os.walk(os.path.join("data", "species_lists")):
            for file in files:
                if file.endswith(".csv"):
                    # spec_lists_full_path.append(os.path.join(root, file))
                    self.taxon_list.append(file)
        self.taxon_list = [spec_list[:-4] for spec_list in self.taxon_list]
        print(self.taxon_list)

        # Prepare the widget structure:
        button_scroll_view = ScrollView(size_hint=(1, None), size=(width, "130dp"))
        stack_layout = StackLayout(size_hint_y=None, size=[width, height], padding=["8dp", 0], spacing="2dp")
        stack_layout.bind(minimum_height=stack_layout.setter('height'))

        for taxon in self.taxon_list:
            taxon_button = MDFillRoundFlatIconButton(text=taxon, id=taxon, icon='circle',
                                                     on_press=self.button_pressed)
            self.taxon_button_list[taxon] = taxon_button
            # print(self.taxon_button_list[taxon])
            stack_layout.add_widget(taxon_button)

        button_scroll_view.add_widget(stack_layout)
        taxon_button_card.add_widget(button_scroll_view)
        
        print("UserSettings.create_buttons_from_tax_list executed")
        return self.taxon_button_list

    def button_pressed(self, button):
        if button.icon == 'circle':
            self.taxon_pull_list.append(button.text)
            button.icon = 'check-circle'
        else:
            self.taxon_pull_list.remove(button.text)
            button.icon = 'circle'
        print("UserSettings.button_pressed executed")

    def load_taxon_selections(self):
        # upload of species lists from user_settings.json.
        if os.path.exists(os.path.join("data", "user_settings.json")):
            with open(os.path.join("data", "user_settings.json")) as us:
                user_settings = json.load(us)

            self.taxon_pull_list = user_settings["taxon"]
            # check if csv is still available, update if user deleted one which was saved in user_settings.json
            self.taxon_pull_list = [taxon for taxon in self.taxon_pull_list if taxon in self.taxon_list]

            # Check buttons for selected species lists.
            for taxon, button in self.taxon_button_list.items():
                if taxon in self.taxon_pull_list:
                    button.icon = 'check-circle'

            threading.Thread(target=self.get_species_lists).start()
        print("UserSettings.load_taxon_selections executed")

    def get_species_lists(self):
        # Uploads species lists for all selected taxon buttons into a dictionary and the database.
        species_df = pd.DataFrame()

        for spec_list in self.taxon_pull_list:
            path = os.path.join("data", "species_lists",  spec_list + ".csv")
            new_list = pd.read_csv(path)
            species_df = pd.concat([species_df, new_list], ignore_index = True, sort = False)
        # species_df.to_csv("see_whats_loaded.csv", index=False)

        # Save the DataFrame to the SQLite database
        conn = sqlite3.connect(os.path.join("data", "fsurv.db"))
        species_df.to_sql('species_list', conn, if_exists='replace')
        conn.commit()
        conn.close()

        # prepares the species lists into dictionaries, to filter for genus
        # and after only the species within the selected genus.
        self.genus_dict.clear()

        for index, row in species_df.iterrows():
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
        print("UserSettings.get_species_lists executed")

    def load_user_settings(self):
        # upload user_settings at app startup
        if os.path.exists(os.path.join("data", "user_settings.json")):
            with open(os.path.join("data", "user_settings.json")) as us:
                user_settings = json.load(us)

            self.ids.user_name.text = user_settings["user_name"]
            self.ids.institution.text = user_settings["institution"]
            self.ids.country.text = user_settings["country"]
            self.ids.language.text = user_settings["language"]
        print("UserSettings.load_user_settings executed")

    def save_user_settings(self):
        print(self.taxon_pull_list)
        # saves all the user settings to the user_settings.json - file.
        dump_user_settings = {"user_name": self.ids.user_name.text, "institution": self.ids.institution.text,
                              "country": self.ids.country.text, "language": self.ids.language.text,
                              "taxon": self.taxon_pull_list}

        # take all usersettings from the settings fields
        json_object = json.dumps(dump_user_settings, indent=4)

        # Writing to sample.json
        with open(os.path.join("data", "user_settings.json"), 'w+') as outfile:
            outfile.write(json_object)
        print("UserSettings.save_user_settings executed")
