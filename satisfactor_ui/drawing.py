import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

import pickle
from gi.repository import Gdk, Graphene, Gsk, Gtk
from pathlib import Path
from satisfactor_py.base import Component
from satisfactor_py.factories import Factory
from satisfactor_ui.geometry import Coordinate2D, Size2D


BASE_IMAGE_FILE_PATH = './static/images'
COLOR_BACKGROUND = '#383875'
COLOR_LINES = '#a3a8fa'
SIZE_COMPONENT = Size2D(128, 128)
SIZE_COMPONENT_BADGE = Size2D(24, 24)
SIZE_COMPONENT_IMAGE = Size2D(96, 96)


class Blueprint(object):
    '''
    A Blueprint is a mapping of factory components to a physical pixel grid. Orientation values here
    refer to an offset of an imaginary origin point at (0, 0). There is no outer boundary or size
    maximum.

        - factory: A Factory object containing the component to draw and simulate
        - background_color: A string describing the background color of the blueprint
        - line_color: A string describing the color of flow lines in the foreground
    '''

    def __init__(self,
        factory: Factory = None,
        background_color: str = None,
        line_color: str = None,
        viewport_size: Size2D = Size2D()
    ):
        # Build a new factory if we weren't given one
        self.factory = factory if factory else Factory()

        # Set up a few internals
        self.coordinateMap = {}    # Mapping of component UUIDs to Coordinate2Ds
        self.selected = None       # Pointer to currently selected component, if any
        self.textures = {}         # Collection of pre-loaded images to draw with
        self.viewport = Viewport(size=viewport_size) # The currently visible area of the blueprint

        # Set up colors
        self.background_color = Gdk.RGBA()
        self.background_color.parse(background_color if background_color else COLOR_BACKGROUND)
        self.line_color = Gdk.RGBA()
        self.line_color.parse(line_color if line_color else COLOR_LINES)

    @staticmethod
    def load(self,
        filename: str
    ):
        '''
        Static method which loads a blueprint from a file previously saved by the `save` function.

            - filename: Path to the file to load
        '''

        with open(filename, 'rb') as fh:
            blueprint = pickle.load(fh)
        return blueprint


    def save(self,
        filename: str
    ):
        '''
        Serializes the blueprint using pickle and saves that content to the specified file

            - filename: Path to the file to save
        '''

        with open(filename, 'wb') as fh:
            pickle.dump(self, fh, pickle.HIGHEST_PROTOCOL)

    def add_component(self,
        component: Component,
        location: Coordinate2D
    ):
        '''
        Adds a component to the factory and sets up its coordinate mapping
        '''

        self.factory.add([component])
        self.coordinateMap[component.id] = location

    def draw_background(self,
        snapshot: Gdk.Snapshot,
        background_color: Gdk.RGBA = None
    ):
        '''
        Paints a rectangle over the entire visible area of the widget using the preferred background
        color.

            - snapshot: The Gdk.Snapshot object to draw onto
            - background_color: An optional Gdk.RGBA color to use instead of the one defined for the
                blueprint, if you need that for some reason.
        '''

        color = background_color if background_color else self.background_color
        rect = Graphene.Rect().init(0, 0, self.viewport.size.width, self.viewport.size.height)
        snapshot.push_clip(rect)
        snapshot.append_color(color, rect)
        snapshot.pop()

    def draw_component(self,
        snapshot: Gdk.Snapshot,
        component: Component,
        component_location: Coordinate2D
    ):
        '''
        Draws a graphical representation of a factory component on the screen.
        '''

        scale = self.viewport.scale
        texture = self.get_component_texture(component)

        if texture:
            rect = Graphene.Rect()
            rect.init(
                round(component_location.x * scale) - round(self.viewport.location.x * scale),
                round(component_location.y * scale) - round(self.viewport.location.y * scale),
                round(SIZE_COMPONENT.width * scale),
                round(SIZE_COMPONENT.height * scale)
            )
            snapshot.append_texture(texture, rect)

    def draw_frame(self, snapshot):
        '''
        Draws a single frame of the contents of the viewport.
        '''
        
        self.draw_background(snapshot=snapshot)
        visible_components = self.get_visible_components()
        for component, component_location in visible_components:
            self.draw_component(snapshot, component, component_location)
        

        # Is anything not in the viewport that is connected to something in the viewport? If so,
        # we'll have to figure out the target of conveyance lines that come off such a component
        # and draw it appropriately.

        pass

    def get_visible_components(self) -> list[Component]:
        '''
        Returns a list of tuples like so:
            (component, coordinates).

        The types are like so:
            (satisfactor_py.base.Component, satisfactor_ui.geometry.Coordinate2D)
        
        These components are the ones which are partially or fully visible within the frame of the
        viewport and must be drawn when updating the widget.
        '''

        # Filter out components without coordinate mappings
        drawable_components = [ (component, self.coordinateMap[component.id]) \
            for component in self.factory.components
            if component.id in self.coordinateMap.keys() ]

        # Find components which are visible based on canvas location and size
        canvas_location, canvas_size = self.viewport.get_visible_canvas_region()
        visible_components = []
        for component, component_location in drawable_components:
            if (component_location.x + SIZE_COMPONENT.width >= canvas_location.x
                and component_location.y + SIZE_COMPONENT.height >= canvas_location.y) \
            or (component_location.x <= canvas_location.x + canvas_size.width
                and component_location.y <= canvas_location.y + canvas_size.height):
                    visible_components.append((component, component_location))
        return visible_components

    def get_component_location(self,
        component: Component
    ) -> Coordinate2D:
        '''
        Returns the Coordinate2D mapped to the given component, or (0, 0) if there is no mapping.

            - component: The component whose location you wish to retrieve
        '''

        return self.coordinateMap.get(component.id, Coordinate2D())

    def get_component_texture(self,
        component: Component
    ):
        '''
        Retrieves the texture for the given component if it has been loaded. Otherwise, loads that
        texture into memory and returns it. Will return None or throw an exception if the texture
        cannot be loaded.

            - component: The component to load the texture for
        '''

        texture = self.textures.get(component.__class__.__name__, None)
        if texture:
            return texture

        file = Path(f'{BASE_IMAGE_FILE_PATH}/{component.__class__.__name__}.png')
        if file.exists():
            texture = Gdk.Texture.new_from_filename(str(file))
            self.textures[component.__class__.__name__] = texture
            return texture

        return None


class Viewport(object):
    '''
    A 2-dimensional rectangle through which a user views a portion of a Blueprint.

        - location: A 2D coordinate representing the location of the top-left corner of the viewport
            within a blueprint
        - size: A 2D size representing the pixel width and height of the viewport
        - zoom: A factor by which the factory components are made larger or smaller in the viewport
    '''

    def __init__(self,
        location: Coordinate2D = Coordinate2D(),
        size: Size2D = Size2D(),
        scale: float = 1.0
    ):
        self.location = location
        self.size = size
        self.scale = scale
    
    def get_visible_canvas_region(self):
        return (self.location, Size2D(
            round(self.size.width / self.scale), 
            round(self.size.height / self.scale)
        ))
