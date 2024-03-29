from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivymd.uix.button import MDFillRoundFlatButton
from usersettings import UserSettings
import sqlite3
import os


class AutoCompleteSp(Widget):
    """
    This module creates inline autocompletion for species filtered from species lists.
    It needs a TextInput or MDTextfield with the id: tf and
    a (MD)StackLayout (or an alternative layout but stack works best) will handel the suggestion buttons
    see autocomplete.kv
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("AutoCompleteSp.__init__ executed")


    def create_suggestions(self, instance, value):
        tf_input = value.split()  # Split tf_input text into separate words
        filtered_suggestions = []

        if len(tf_input) == 0:
            # input can be empty if all letters are removed
            pass

        elif len(tf_input) == 1:
            # Check if first word matches the beginning of any suggestion of e.g. genus
            filtered_suggestions = [key for key in UserSettings.genus_dict.keys()
                                    if key.lower().startswith(tf_input[0].lower())]
        else:
            try:  # Avoid crash when no "species value was given
                filtered_suggestions = [key for key in UserSettings.genus_dict[tf_input[0]]
                                        if key.startswith(tf_input[1])]
            except:
                pass

        # Create Database connection:
        conn = sqlite3.connect(os.path.join("data", "fsurv.db"))
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT vernacularName FROM species_list")
        except:
            print("sqlite3.OperationalError: no species list uploaded.")

        # Fetch all the values from the column directly as a list
        species_list = [row[0] for row in cursor.fetchall()]
        # print(species_list)
        conn.close()

        # filter the vernacular name list:
        if len(value) > 0:
            filtered_suggestions.extend([key for key in species_list
             if str(key).lower().startswith(str(value).lower())])

        # create suggestion buttons in the MDStackLayout with id 'word suggest':
        # by pressing the button the "paste" method is applied
        self.ids.word_suggests.clear_widgets()
        for suggestion in filtered_suggestions[:10]:
            button = MDFillRoundFlatButton(text=suggestion, id=suggestion, on_press=self.paste)
            self.ids.word_suggests.add_widget(button)
        print("AutoCompleteSp.create_suggestions executed")

    def paste(self, button):
        """ Bring the button text (which is the previously generated suggestion to the textfield).
        f-string is created from the first word (mostly genus) if present, and the text from the button.
        to prevent that already typed words and letters are not pasted two times, length of this text string
        is measured and subtracted from the "button.text" string. It cannot just be set. """
        self.ids.tf.text = f'{self.ids.tf.text}{button.text[len(self.ids.tf.text.split()[-1]):]} '.lstrip()
        self.ids.tf.text = self.ids.tf.text[0].upper() + self.ids.tf.text[1:]
        # set_focus back to the text field does not work alone. it has to be scheduled.
        Clock.schedule_once(self.set_focus, 0.2)
        Clock.schedule_once(self.set_focus, 0.6)  # to make sure that it is placed also on slow machines.
        print("AutoCompleteSp.paste executed")

    def set_focus(self, event):
        self.ids.tf.focus = True
        print("AutoCompleteSp.set_focus executed")
