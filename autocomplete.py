'''
This module creates inline autocompletion for species filtered from species lists.
It needs a TextInput or MDTextfield with the id: tf and
a (MD)StackLayout (or an alternative layout but stack works best) will handel the suggestion buttons
see autocomplete.kv
'''

from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.button import MDFillRoundFlatButton
from collections import defaultdict
import pandas as pd

Builder.load_file('autocomplete.kv')


class AutoComplete(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.species_dict = defaultdict(list)
        self.prepare_species_list()

    def prepare_species_list(self):
        # prepares the species lists into dictionaries, to filter for genus
        # and after only the species within the selected genus.
        file = str('data/species_lists/spec_germany_Pflanzen.csv')
        species_df = pd.read_csv(file)
        for index, row in species_df.iterrows():
            sp = row["sciName"]
            genus, species = sp.split(" ", maxsplit=1)
            self.species_dict[genus].append(species)

    def create_suggestions(self, instance, value):
        tf_input = value.split()  # Split tf_input text into separate words
        filtered_suggestions = []

        if len(tf_input) == 0:
            # input can be empty if all letters are removed
            pass

        elif len(tf_input) == 1:
            # Check if first word matches the beginning of any suggestion of e.g. genus
            filtered_suggestions = [key for key in self.species_dict.keys()
                                    if key.lower().startswith(tf_input[0].lower())]
        else:
            filtered_suggestions = [key for key in self.species_dict[tf_input[0]]
                                    if key.startswith(tf_input[1])]

        # create suggestion buttons in the MDStackLayout with id 'word suggest':
        # by pressing the button the "paste" method is applied
        self.ids.word_suggests.clear_widgets()
        for suggestion in filtered_suggestions[:20]:
            button = MDFillRoundFlatButton(text=suggestion, id=suggestion, on_press=self.paste)
            self.ids.word_suggests.add_widget(button)

    def paste(self, button):
        # Bring the button text (which is the previously generated suggestion to the textfield).
        # f-string is created from the first word (mostly genus) if present, and the text from the button.
        # to prevent that already typed words and letters are not pasted two times, length of this text string
        # is measured and subtracted from the button.text string. It cannot just be set.
        self.ids.tf.text = f'{self.ids.tf.text}{button.text[len(self.ids.tf.text.split()[-1]):]} '.lstrip()
        self.ids.tf.text = self.ids.tf.text[0].upper() +  self.ids.tf.text[1:]# Bug: should upper first word but not lower other words
        # set_focus back to the text field does not work alone. it has to be scheduled.
        Clock.schedule_once(self.set_focus, 0.1)

    def set_focus(self, event):
        self.ids.tf.focus = True


if __name__ == '__main__':
    class MainApp(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = 'Teal'
            self.theme_cls.primary_hue = '700'
            self.theme_cls.accent_palette = 'Orange'

            screen_manager = ScreenManager()
            auto = AutoComplete(name='auto')
            screen_manager.add_widget(auto)
            return screen_manager
    MainApp().run()
