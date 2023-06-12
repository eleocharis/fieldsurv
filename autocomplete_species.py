from kivymd.app import MDApp
from kivy.uix.widget import Widget
# from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.button import MDFillRoundFlatButton
from usersettings import SPEC_AUT_C_DICT

# Builder.load_file('autocomplete.kv')


class AutoCompleteSp(Widget):
    '''
    This module creates inline autocompletion for species filtered from species lists.
    It needs a TextInput or MDTextfield with the id: tf and
    a (MD)StackLayout (or an alternative layout but stack works best) will handel the suggestion buttons
    see autocomplete.kv
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_suggestions(self, instance, value):
        tf_input = value.split()  # Split tf_input text into separate words
        filtered_suggestions = []

        if len(tf_input) == 0:
            # input can be empty if all letters are removed
            pass

        elif len(tf_input) == 1:
            # Check if first word matches the beginning of any suggestion of e.g. genus
            filtered_suggestions = [key for key in SPEC_AUT_C_DICT.keys()
                                    if key.lower().startswith(tf_input[0].lower())]
        else:
            try:  # Avoid crash when no "species value was given
                filtered_suggestions = [key for key in SPEC_AUT_C_DICT[tf_input[0]]
                                        if key.startswith(tf_input[1])]
            except:
                pass

        # create suggestion buttons in the MDStackLayout with id 'word suggest':
        # by pressing the button the "paste" method is applied
        self.ids.word_suggests.clear_widgets()
        for suggestion in filtered_suggestions[:10]:
            button = MDFillRoundFlatButton(text=suggestion, id=suggestion, on_press=self.paste)
            self.ids.word_suggests.add_widget(button)

    def paste(self, button):
        ''' Bring the button text (which is the previously generated suggestion to the textfield).
        f-string is created from the first word (mostly genus) if present, and the text from the button.
        to prevent that already typed words and letters are not pasted two times, length of this text string
        is measured and subtracted from the "button.text" string. It cannot just be set. '''
        self.ids.tf.text = f'{self.ids.tf.text}{button.text[len(self.ids.tf.text.split()[-1]):]} '.lstrip()
        self.ids.tf.text = self.ids.tf.text[0].upper() + self.ids.tf.text[1:]
        # set_focus back to the text field does not work alone. it has to be scheduled.
        Clock.schedule_once(self.set_focus, 0.2)
        Clock.schedule_once(self.set_focus, 0.6)  # to make sure that it is placed also on slow machines.

    def set_focus(self, event):
        self.ids.tf.focus = True


if __name__ == '__main__':
    class MainApp(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = 'Teal'
            self.theme_cls.primary_hue = '700'
            self.theme_cls.accent_palette = 'Orange'

            auto_comp = AutoCompleteSp()
            return auto_comp
    MainApp().run()
