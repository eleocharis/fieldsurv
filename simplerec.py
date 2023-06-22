from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy_garden.mapview import MapMarkerPopup, MapSource
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineIconListItem, IconLeftWidget
from kivy.animation import Animation
from pathlib import Path
from autocomplete_species import AutoCompleteSp
import datetime
import pandas as pd

Builder.load_file('simplerec.kv')


class PointCreator(MapMarkerPopup):
    def __init__(self, x, y, spec, abu, date, point_id, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.species = spec
        self.abundance = str(abu)
        self.date = date
        self.id = point_id
        print(f'{kwargs}')

    def info_popup(self):
        # Add info Popup
        sr = SimpleRec()
        layout = MDBoxLayout(size_hint=(None, None), size=[200, 100], orientation='vertical', md_bg_color=[1, 1, 1, .8])
        label = MDLabel(text=f'{self.species}\n {self.date}', theme_text_color="Custom",
                        text_color=[0, 0, 5, 1])
        layout.add_widget(label)
        button = MDFillRoundFlatButton(text="Delete Point?", on_release=sr.delete_point)
        layout.add_widget(button)
        self.add_widget(layout)


class SimpleRec(MDScreen, AutoCompleteSp):
    record_table = ObjectProperty(None)
    # records = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = 'data/simple_point_records.csv'
        self.next_id = None
        # self.points = {}
        self.records = pd.DataFrame
        # self.record_table = None
        self.table_items = {}
        self.ids.date.text = datetime.date.today().strftime("%Y-%m-%d")
        self.ids.time.text = datetime.datetime.now().strftime("%H:%M")
        self.map_dropdown = None

        self.map_source_management()
        self.read_point_records_file()
        Clock.schedule_interval(lambda dt: self.crosshair(), 1)

    def map_source_management(self):
        # add alternative map sources to the MapSource
        alternative_map_source = (0, 0, 19, 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                        'Kartendaten: © OpenStreetMap-Mitwirkende, SRTM | Kartendarstellung: © OpenTopoMap (CC-BY-SA)')
        MapSource.providers["opentopomap"] = alternative_map_source

        # Dropdown menu for maps.
        maps = [
            {"text": f'{key}',
             "viewclass": 'OneLineListItem',
             "on_release": lambda x=key: self.set_map_source(x)
             } for key in MapSource.providers.keys()
        ]
        self.map_dropdown = MDDropdownMenu(
            caller=self.ids.set_map_button,
            items=maps,
            width_mult=3,
            elevation=0,
            background_color=[1, 1, 1, .8])

    def crosshair(self):
        x, y = self.ids.map.center
        self.canvas.remove_group(u"cross")
        with self.canvas:
            Color(0, 0, 0, 1)
            Line(points=[x, y - self.width*0.03, x, y + self.width*0.03], width=1, group=u"cross")
            Line(points=[x - self.width*0.03, y, x + self.width*0.03, y], width=1, group=u"cross")

    def add_points(self):
        # Add points to the records DataFrame
        point_attributes = {"id": str(self.next_id),
                            "species": str(self.ids.tf.text).strip(),
                            "abundance": str(self.ids.abundance.text),
                            "timestamp": f'{self.ids.date.text} {self.ids.time.text}',
                            "lat": self.ids.map.lat,
                            "lon": self.ids.map.lon}
        self.records.loc[len(self.records.index)] = point_attributes
        print(self.records)

        # Add points to the Table
        self.fill_record_table(point_attributes)

        # Set the points on the map
        x = self.ids.map.lat
        y = self.ids.map.lon
        point = PointCreator(lat=self.ids.map.lat, lon=self.ids.map.lon, x=x, y=y, spec=self.ids.tf.text,
                             abu=self.ids.abundance, date=f'{self.ids.date.text} {self.ids.time.text}',
                             point_id=self.next_id)
        # self.points[self.next_id] = point #store all points in a dict.
        self.ids.map.add_widget(point)

        # Generate next id
        self.next_id = str("F" + str(int(self.records.iloc[-1]["id"][1:]) + 1))

        # Empty fields and set focus
        self.ids.tf.text = ""
        self.ids.abundance.text = "1"
        self.ids.time.text = datetime.datetime.now().strftime("%H:%M")
        self.ids.tf.focus = True
        return self.records, self.record_table

    def delete_point(self, button):
        # remove point from Table
        record_id = str(button.parent.parent.parent.id)
        print(record_id)
        print(self.record_table.children)
        print(self.table_items[record_id])
        self.record_table.remove_widget(self.table_items[record_id])
        self.table_items.pop(record_id)
        print(self.record_table.children)

        # remove point from records
        self.records = self.records.loc[self.records["id"].astype(str) != str(record_id)]
        print(self.records)

        # Remove point from map
        self.ids.map.remove_widget(button.parent.parent.parent)
        return self.records, self.record_table

    def read_point_records_file(self):
        # reads recorded data from the previous session and creates the points
        if Path(self.file).is_file():
            self.records = pd.read_csv(self.file)

            for index, row in self.records.iterrows():
                lat, lon = float(row["lat"]), float(row["lon"])
                point = PointCreator(lat=lat, lon=lon, x=lat, y=lon, spec=row["species"], abu=row["abundance"],
                                     date=row["timestamp"], point_id=row["id"])
                # self.points[row["id"]] = point  # store all points in a dict.
                self.ids.map.add_widget(point)

                # add points to the Table
                self.fill_record_table(row)

            # create next ID
            self.next_id = str("F" + str(int(self.records.iloc[-1]["id"][1:]) + 1))

        else:
            self.records = pd.DataFrame(columns=["id", "species", "abundance", "timestamp", "lat", "lon"])
            self.next_id = "F1"

    def save_records(self):
        # this saves the recordings on the drive
        self.records.to_csv(self.file, index=False)

    def show_date_picker(self):
        # Open date picker dialog.
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.get_date, on_cancel=self.on_cancel)
        date_dialog.open()

    def show_time_picker(self):
        # Open time picker dialog.
        time_dialog = MDTimePicker()
        time_dialog.bind(on_cancel=self.on_cancel, time=self.get_time)
        time_dialog.open()

    def get_time(self, instance, time):
        self.ids.time.text = str(time.strftime("%H:%M"))

    def get_date(self, instance, value, date_range):
        self.ids.date.text = str(value)

    def on_cancel(self, instance, value):
        # Events called when the "CANCEL" dialog box button is clicked.
        pass

    def show_input_field(self, input_field, show_input_button):
        # moves the input_field into the screen
        if self.ids.show_input_button.icon == 'plus':
            show_input = Animation(pos=[0, 0], duration=0.2)
            show_input.start(input_field)

            move_button = Animation(
                pos_hint={'center_x': 0.9, "center_y": self.ids.input_field.height/Window.size[1]*1.1},
                duration=0.2)
            move_button.start(show_input_button)
            self.ids.show_input_button.icon = 'chevron-down'
        else:
            show_input = Animation(pos=[0, -self.ids.input_field.height], duration=0.2)
            show_input.start(input_field)

            move_button = Animation(
                pos_hint={'center_x': 0.9, "center_y": 0.06},
                duration=0.2)
            move_button.start(show_input_button)
            self.ids.show_input_button.icon = 'plus'

    def set_map_source(self, selected_map):
        self.ids.map.map_source = selected_map
        self.map_dropdown.dismiss()
        print(MapSource.providers.values())

    def fill_record_table(self, last_entry):
        item = ThreeLineIconListItem(
            IconLeftWidget(icon='flower'),
            id=last_entry["id"],
            text=str(last_entry["species"]),
            secondary_text=str("Abundance " + str(last_entry["abundance"])),
            tertiary_text=str(last_entry["timestamp"]),
            on_release=lambda x: self.click_table_item()
        )
        self.ids.record_table.add_widget(item)
        self.table_items[last_entry["id"]] = item

    def click_table_item(self):
        print("Item clicked!")

    def show_record_table(self, record_table_layout, show_records_button):
        # moves the record list into the screen
        if self.ids.show_records_button.icon == 'view-headline':
            show_records = Animation(pos=[0, Window.size[1]-self.ids.record_table_layout.height], duration=0.2)
            show_records.start(record_table_layout)

            move_button = Animation(
                pos_hint={'center_x': 0.1, "center_y": (1 - self.ids.record_table_layout.height / Window.size[1]) * 0.92},
                duration=0.2)
            move_button.start(show_records_button)
            self.ids.show_records_button.icon = 'chevron-up'
        else:
            show_records = Animation(pos=[0, Window.size[1]], duration=0.2)
            show_records.start(record_table_layout)

            move_button = Animation(
                pos_hint={'center_x': 0.1, "center_y": 0.94},
                duration=0.2)
            move_button.start(show_records_button)
            self.ids.show_records_button.icon = 'view-headline'
