from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
class GpsHelper:
    has_centered_map = False

    def run(self):
        # Get a reference to the GpsBlinker
        gps_blinker = App.get_running_app().root.ids.map.ids.blinker

        # Starting the GpsBlinker
        gps_blinker.blink()

        # Request permissions on Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission

            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all GPS permissions")
                else:
                    print("Did not got all GPS permissions")

            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.ACCESS_FINE_LOCATION], callback)

        # Configure GPS
        if platform == 'android' or platform == 'ios':
            from plyer import gps
            gps.configure(on_location=self.update_blinker_position,
                          on_status=self.on_auth_status)
            gps.start(minTime=1000, minDistance=0)

    def update_blinker_position(self, *args, **kwargs):
        my_lat = kwargs['lat']
        my_lon = kwargs['lon']

        gps_blinker = App.get_running_app().root.ids.map.ids.blinker
        gps_blinker.lat = my_lat
        gps_blinker.lon = my_lon
        print("GPS position ", my_lat, my_lon)

        # Center map on GPS position on startup
        if not self.has_centered_map:
            map = App.get_running_app().root.ids.map
            map.center_on(my_lat, my_lon)
            self.has_centered_map = True


    def on_auth_status(self, general_status, status_message):
        if general_status == 'provider-enabled':
            pass
        else:
            self.open_gps_access_popup()

    def open_gps_access_popup(self):
        dialog = MDDialog(title="GPS Error", text="Enable GPS Access on mobile")
