from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy_garden.mapview import MapMarkerPopup, MapSource
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.button import Button
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList
from kivy.animation import Animation
from pathlib import Path
from autocomplete_species import AutoCompleteSp
import datetime
import pandas as pd


Builder.load_file('simplerec.kv')


class SpeedDialButton(MDFloatingActionButtonSpeedDial):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = {
            'Python': 'language-python',
            'PHP': 'language-php',
            'C++': 'language-cpp',
        }

class PointCreator(MapMarkerPopup):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y


class SimpleRec(MDScreen, AutoCompleteSp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = 'data/simple_point_records.csv'
        self.read_point_records_file()
        # self.fill_records_table()
        self.ids.date.text = datetime.date.today().strftime("%Y-%m-%d")
        self.ids.time.text = datetime.datetime.now().strftime("%H:%M")
        Clock.schedule_interval(lambda dt: self.crosshair(), 1)

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
            elevation=0)

    def crosshair(self):
        x, y = self.ids.map.center
        self.canvas.remove_group(u"cross")
        with self.canvas:
            Color(0, 0, 0, 1)
            Line(points=[x, y - self.width*0.03, x, y + self.width*0.03], width=1, group=u"cross")
            Line(points=[x - self.width*0.03, y, x + self.width*0.03, y], width=1, group=u"cross")

    def add_points(self):
        # print(f'{self.ids.map.lat} | {self.ids.map.lon}')
        # add points to the records DataFrame
        point_attributes = {"species": self.ids.tf.text,
                            "abundance": self.ids.abundance.text,
                            "timestamp": f'{self.ids.date.text} {self.ids.time.text}',
                            "lat": self.ids.map.lat,
                            "lon": self.ids.map.lon}
        self.records.loc[len(self.records.index)] = point_attributes
        print(self.records)

        # Set the points on the map
        x = self.ids.map.lat
        y = self.ids.map.lon
        point = PointCreator(lat=self.ids.map.lat, lon=self.ids.map.lon, x=x, y=y)
        point_information = Button(text=str(x + y))  # Does not work jet
        point.add_widget(point_information)
        self.ids.map.add_widget(point)

        # empty fields and set focus
        self.ids.tf.text = ""
        self.ids.abundance.text = "1"
        self.ids.time.text = datetime.datetime.now().strftime("%H:%M")
        self.ids.tf.focus = True

        # add points to the Table
        # print(list(self.records.iloc[-1]))
        # Clock.schedule_once(lambda dt: self.table.add_row(list(self.records.iloc[-1])))  #

    def read_point_records_file(self):
        # reads previously recorded and saved species data from the drive
        if Path(self.file).is_file():
            self.records = pd.read_csv(self.file)
            for index, row in self.records.iterrows():
                lat, lon = float(row["lat"]), float(row["lon"])
                point = PointCreator(lat=lat, lon=lon, x=lat, y=lon)
                point_information = Button(size=(self.width*0.2, self.height*0.1),
                                           text=f'{row["species"]} {row["abundance"]}') # Does not work jet
                point.add_widget(point_information)
                self.ids.map.add_widget(point)
        else:
            self.records = pd.DataFrame(columns=["species", "abundance", "timestamp", "lat", "lon"])

    def fill_records_table(self):
        records_for_table = self.records
        records_for_table["lat"] = records_for_table["lat"].round(decimals=4)
        records_for_table["lon"] = records_for_table["lon"].round(decimals=4)
        records_for_table = records_for_table.values.tolist()
        headers_for_table = list(self.records.columns)
        self.table = MDDataTable(
            column_data = [(header, dp(20)) for header in headers_for_table],
            row_data = records_for_table,
            rows_num = len(records_for_table),
            #check = True,
            elevation = 0,
            background_color = [1, 1, 1, .8]
        )
        self.ids.record_table.add_widget(self.table)
        self.table.bind(on_row_press=self.on_row_press)

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

    def show_record_table(self, record_table, show_records_button):
        # moves the record list into the screen
        if self.ids.show_records_button.icon == 'view-headline':
            show_records = Animation(pos=[0, Window.size[1]-self.ids.record_table.height], duration=0.2)
            show_records.start(record_table)

            move_button = Animation(
                pos_hint={'center_x': 0.1, "center_y": (1 - self.ids.record_table.height / Window.size[1]) * 0.95},
                duration=0.2)
            move_button.start(show_records_button)
            self.ids.show_records_button.icon = 'chevron-up'
        else:
            show_records = Animation(pos=[0, Window.size[1]], duration=0.2)
            show_records.start(record_table)

            move_button = Animation(
                pos_hint={'center_x': 0.1, "center_y": 0.94},
                duration=0.2)
            move_button.start(show_records_button)
            self.ids.show_records_button.icon = 'view-headline'

    def on_row_press(self, instance_table, instance_row):
        print(f'{instance_table} | {instance_row}')

    def set_map_source(self, selected_map):
        self.ids.map.map_source = selected_map
        self.map_dropdown.dismiss()
        #print(MapSource.providers.get(selected_map))




