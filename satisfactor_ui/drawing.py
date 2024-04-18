import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gdk, Graphene, Gsk, Gtk
from pathlib import Path
from satisfactor_py.base import Component
from satisfactor_py.buildings import Foundry


BASE_IMAGE_FILE_PATH = './static/images'
COLOR_BACKGROUND = '#bbbbcc'


class Blueprint(Gtk.Widget):
    '''
    A Blueprint is a GTK Widget that draws a factory's components in a 2D visible space and allows a
    user to interact with those components.
    '''

    def __init__(self):
        super().__init__()
        self.textures = {}
        self.zoom = 1.0

        self.testComponent = Foundry()
    
    def do_snapshot(self,
        snapshot: Gtk.Snapshot
    ):
        '''
        Draws the entire factory designer widget
        '''
        self.__draw_background(snapshot)
        self.__draw_component(snapshot, self.testComponent, 50, 50)

    def __draw_background(self,
        snapshot: Gtk.Snapshot
    ):
        '''
        Draws the background color
        '''

        background_color = Gdk.RGBA()
        background_color.parse('#bbbbcc')
        width = self.get_width()
        height = self.get_height()
        rect = Graphene.Rect().init(0, 0, width, height)
        snapshot.push_clip(rect)
        snapshot.append_color(background_color, rect)
        snapshot.pop()

    def __draw_component(self,
        snapshot: Gtk.Snapshot,
        component: Component,
        x: int,
        y: int
    ):
        '''
        Draws a single component to the snapshot at position (x, y)
        '''

        width = round(64 * self.zoom)
        height = round(64 * self.zoom)
        texture = self.__get_component_texture(component)

        if texture:
            rect = Graphene.Rect()
            rect.init(x, y, width, height)
            snapshot.append_texture(texture, rect)

    def __get_component_texture(self, component):
        texture = self.textures.get(component.__class__.__name__, None)

        if texture:
            return texture

        texFile = Path(f'{BASE_IMAGE_FILE_PATH}/{component.__class__.__name__}.png')
        if texFile.exists():
            texture = Gdk.Texture.new_from_filename(str(texFile))
            self.textures[component.__class__.__name__] = texture
            return texture
        
        return None
