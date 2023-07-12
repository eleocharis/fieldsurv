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
from kivymd.uix.dialog import MDDialog
from kivy.animation import Animation
from autocomplete_species import AutoCompleteSp
import datetime
import pandas as pd
import sqlite3
import os

Builder.load_file('simplerec.kv')


class PointCreator(MapMarkerPopup):
    def __init__(self, x, y, spec, abu, date, point_id, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.sciName = spec
        self.abundance = str(abu)
        self.date = date
        self.id = point_id
        # print(f'{kwargs}')

    def info_popup(self):
        # Add info Popup
        sr = SimpleRec()
        layout = MDBoxLayout(size_hint=(None, None), size=[200, 100], orientation='vertical', md_bg_color=[1, 1, 1, .8])
        label = MDLabel(text=f'{self.sciName}\n {self.date}', theme_text_color="Custom",
                        text_color=[0, 0, 5, 1])
        layout.add_widget(label)
        button = MDFillRoundFlatButton(text="Delete Point?", on_release=sr.delete_point)
        layout.add_widget(button)
        self.add_widget(layout)


class SimpleRec(MDScreen, AutoCompleteSp):
    record_table = ObjectProperty()
    records = pd.DataFrame

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = 'data/simple_point_records.csv'
        self.next_id = None
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
                                  'Kartendaten: © OpenStreetMap-Mitwirkende, '
                                  'SRTM | Kartendarstellung: © OpenTopoMap (CC-BY-SA)')
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
        # Evaluate if vernacular or scientific name was input and add the other on respectively.

        # Create Database connection:
        conn = sqlite3.connect(os.path.join("data", "fsurv.db"))
        species_list = pd.read_sql_query("SELECT sciName, vernacularName FROM species_list", conn)
        conn.close()

        # get the input species
        species_input = self.ids.tf.text.strip()

        if species_input == "":
            self.open_feed_spec_input()
        else:
            if species_input in list(species_list["sciName"]):
                sciName = species_input
                species_row = species_list[species_list["sciName"] == species_input]
                vernacularName = species_row.iloc[0]["vernacularName"]

            elif species_input in list(species_list["vernacularName"]):
                vernacularName = species_input
                species_row = species_list[species_list["vernacularName"] == species_input]
                sciName = species_row.iloc[0]["sciName"]

            else:
                sciName = species_input
                vernacularName = "NA"

            point_attributes = {"records_id": str(self.next_id),
                                "sciName": sciName,
                                "vernacularName": vernacularName,
                                "abundance": str(self.ids.abundance.text),
                                "timestamp": f'{self.ids.date.text} {self.ids.time.text}',
                                "lat": self.ids.map.lat,
                                "lon": self.ids.map.lon}
            self.records.loc[len(self.records.index)] = point_attributes

            # add a row to the database
            conn = sqlite3.connect(os.path.join("data", "fsurv.db"))
            cursor = conn.cursor()
            columns = ", ".join(point_attributes.keys())
            placeholders = ":" + ", :".join(point_attributes.keys())
            query = f'INSERT INTO records ({columns}) VALUES ({placeholders})'
            # Iterate over the dictionary and insert the data
            cursor.execute(query, point_attributes)
            conn.commit()
            db_contents = cursor.execute("SELECT * FROM records")
            print(db_contents)
            for row in db_contents:
                print(row)
            conn.close()

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
            self.next_id = str("F" + str(int(self.records.iloc[-1]["records_id"][1:]) + 1))

            # Empty fields and set focus
            self.ids.tf.text = ""
            self.ids.abundance.text = "1"
            self.ids.time.text = datetime.datetime.now().strftime("%H:%M")
            self.ids.tf.focus = True

    def delete_point(self, button):
        # delete a species record
        records_id = str(button.parent.parent.parent.id)
        print(records_id)

        # remove point from records
        self.records = self.records.loc[self.records["records_id"].astype(str) != str(records_id)]
        #print(self.records)

        # remove point from records db
        # Create Database connection:
        conn = sqlite3.connect(os.path.join("data", "fsurv.db"))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM records WHERE records_id = ?', (records_id,))
        db_contents = cursor.execute("SELECT * FROM records")
        print(db_contents)
        for row in db_contents:
            print(row)
        conn.commit()
        conn.close()

        # remove point from Table
        # print(self.ids.record_table.children)
        # print(self.table_items[records_id])
        self.ids.record_table.remove_widget(self.table_items[records_id])
        self.table_items.pop(records_id)

        # Remove point from map
        self.ids.map.remove_widget(button.parent.parent.parent)

    def read_point_records_file(self):
        # reads recorded data from the previous session and creates the points
        conn = sqlite3.connect(os.path.join("data", "fsurv.db"))
        self.records = pd.read_sql_query("SELECT * FROM records", conn)
        conn.close()

        for index, row in self.records.iterrows():
            lat, lon = float(row["lat"]), float(row["lon"])
            point = PointCreator(lat=lat, lon=lon, x=lat, y=lon, spec=row["sciName"], abu=row["abundance"],
                                 date=row["timestamp"], point_id=row["records_id"])
            # self.points[row["records_id"]] = point  # store all points in a dict.
            self.ids.map.add_widget(point)

            # add points to the Table
            self.fill_record_table(row)

        # create next ID
        try:
            self.next_id = str("F" + str(int(self.records.iloc[-1]["records_id"][1:]) + 1))
        except:
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

    def open_feed_spec_input(self):
        dialog = FeedSpecInput()
        dialog.open()

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
            id=last_entry["records_id"],
            text=str(f'{last_entry["sciName"]} | {last_entry["vernacularName"]}'),
            secondary_text=str("Abundance " + str(last_entry["abundance"])),
            tertiary_text=str(last_entry["timestamp"]),
            on_release=lambda x: self.click_table_item()
        )
        self.ids.record_table.add_widget(item)
        self.table_items[last_entry["records_id"]] = item

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


class FeedSpecInput(MDDialog):
    def __init__(self, **kwargs):
        super().__init__(
            title="Nothing can not be add!",
            text="You have to fucking type in a species! Stupid!",
            radius = [20, 20, 20, 20],
            buttons=[
                MDFillRoundFlatButton(
                    text="OK",
                    on_release=self.close_feed_spec_input
                ),
            ],
            ** kwargs)

    def close_feed_spec_input(self, instance):
        self.dismiss()
