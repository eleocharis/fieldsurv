from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField


class TextFieldApp(MDApp):
    def build(self):
        # Create a root layout
        layout = MDBoxLayout(orientation='vertical')

        # Create a list of text fields
        text_fields = []
        num_fields = 3  # Number of text fields to create

        for i in range(num_fields):
            text_field = MDTextField()
            text_field.bind(on_text_validate=self.on_enter)
            text_fields.append(text_field)
            layout.add_widget(text_field)

        return layout

    def on_enter(self, instance):
        text_fields = instance.parent.children  # Get all the text fields

        # Find the current text field
        current_index = text_fields.index(instance)
        current_field = text_fields[current_index]

        if current_index < len(text_fields) - 1:
            # Switch focus to the next text field
            next_index = current_index + 1
            next_field = text_fields[next_index]
            next_field.focus = True

        current_field.focus = False  # Remove focus from the current text field


if __name__ == '__main__':
    TextFieldApp().run()
