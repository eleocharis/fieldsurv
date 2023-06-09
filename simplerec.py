from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy_garden.mapview import MapMarkerPopup
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.uix.button import Button
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.animation import Animation
from pathlib import Path
from autocomplete import AutoComplete
import datetime
import pandas as pd


Builder.load_file('simplerec.kv')


class PointCreator(MapMarkerPopup):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y


class SimpleRec(Screen, AutoComplete):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = 'data/simple_point_records.csv'
        self.read_point_records_file()
        self.ids.date.text = datetime.date.today().strftime("%Y-%m-%d")
        self.ids.time.text = datetime.datetime.now().strftime("%H:%M")
        Clock.schedule_interval(lambda dt: self.crosshair(), 1)

    def crosshair(self):
        x, y = self.ids.smap.center
        self.canvas.remove_group(u"cross")
        with self.canvas:
            Color(0, 0, 0, 1)
            Line(points=[x, y - self.width*0.03, x, y + self.width*0.03], width=1, group=u"cross")
            Line(points=[x - self.width*0.03, y, x + self.width*0.03, y], width=1, group=u"cross")

    def add_points(self):
        print(f'{self.ids.smap.lat} | {self.ids.smap.lon}')
        # add points to the records DataFrame
        point_attributes = {"species": self.ids.tf.text,
                            "abundance": self.ids.abundance.text,
                            "timestamp": f'{self.ids.date.text} {self.ids.time.text}',
                            "lat": self.ids.smap.lat,
                            "lon": self.ids.smap.lon}
        self.records.loc[len(self.records.index)] = point_attributes
        print(self.records)

        # Set the points on the map
        x = self.ids.smap.lat
        y = self.ids.smap.lon
        point = PointCreator(lat=self.ids.smap.lat, lon=self.ids.smap.lon, x=x, y=y)
        point_information = Button(text=str(x + y))  # Does not work jet
        point.add_widget(point_information)
        self.ids.smap.add_widget(point)

        # empty fields and set focus
        self.ids.tf.text = ""
        self.ids.abundance.text = "1"
        self.ids.time.text = datetime.datetime.now().strftime("%H:%M")
        self.ids.tf.focus = True

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
                self.ids.smap.add_widget(point)
        else:
            self.records = pd.DataFrame(columns=["species", "abundance", "timestamp", "lat", "lon"])

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
        #
        if self.ids.show_input_button.icon == 'plus':
            show_input = Animation(pos_hint={'x': 0, 'y': 0}, duration=0.2)
            show_input.start(input_field)

            move_button = Animation(pos_hint={'center_x': 0.9,
                                              "center_y": self.ids.input_field.height/Window.size[1]*1.1}, duration=0.2)
            move_button.start(show_input_button)
            self.ids.show_input_button.icon = 'minus'
        else:
            show_input = Animation(pos_hint={'x': 0, 'y': -self.ids.input_field.height}, duration=0.2)
            show_input.start(input_field)

            move_button = Animation(
                pos_hint={'center_x': 0.9, "center_y": 0.06},
                duration=0.2)
            move_button.start(show_input_button)
            self.ids.show_input_button.icon = 'plus'

