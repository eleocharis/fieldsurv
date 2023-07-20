from kivy_garden.mapview import MapMarker
from kivy.animation import Animation


class GpsPointer(MapMarker):

    def point_anim(self):
        # Animation that changes the blink size and opacity
        anim = Animation(outer_opacity=0, outer_size=25, duration=1)
        # When the animation completes, reset the animation, then repeat
        anim.bind(on_complete=self.reset)
        anim.start(self)#

    def reset(self, *args):
        self.outer_opacity = 1
        self.outer_size = self.inner_size
        self.point_anim()
