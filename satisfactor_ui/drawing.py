import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

import pickle
from gi.repository import Gdk, Graphene, Gsk, Gtk
from pathlib import Path
from satisfactor_py.base import Building, Component, Conveyance
from satisfactor_py.factories import Factory
from satisfactor_ui.geometry import Coordinate2D, Size2D


BASE_IMAGE_FILE_PATH = './static/images'


def get_texture_from_file(filename: str) -> Gdk.Texture:
    '''
    Given the filename of an image, returns a Gdk.Texture object for it
    '''
    if Path(filename).exists():
        texture = Gdk.Texture.new_from_filename(filename)
        return texture

    return None

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
        background_color: str = '#383875',
        line_color: str = '#a3a8fa',
        viewport_size: Size2D = Size2D()
    ):
        # Build a new factory if we weren't given one
        self.factory = factory if factory else Factory()

        # Set up some data we need to lay out components visually
        self.comp_icon_offset = Size2D(32, 8)
        self.comp_icon_size = Size2D(64, 64)
        self.comp_size = Size2D(128, 128)
        self.comp_badge_offset_y = 78
        self.comp_badge_padding_x = 8
        self.comp_badge_size = Size2D(16, 16)
        self.comp_label_offset_y = 100
        self.comp_label_size = Size2D(112, 20)

        # Set up a few internals
        self.coordinateMap = {}    # Mapping of component UUIDs to Coordinate2Ds
        self.selected = None       # Pointer to currently selected component, if any
        self.__textures = {}       # Collection of pre-loaded images to draw with
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
        location: Coordinate2D
    ):
        '''
        Draws a graphical representation of a factory component on the screen.
        '''

        scale = self.viewport.scale  # Makes later code tidier

        # Load up the component icon texture
        icon_key = component.__class__.__name__
        icon_texture = self.get_texture('components', icon_key)
        if not icon_texture:
            filename = f'{BASE_IMAGE_FILE_PATH}/components/{icon_key}.png'
            icon_texture = self.load_texture(filename, 'components', icon_key)

        # Draw the icon
        icon_left = round(location.x * scale)
        icon_left -= round(self.viewport.location.x * scale)
        icon_left += round(self.comp_icon_offset.width * scale)
        icon_top = round(location.y * scale)
        icon_top -= round(self.viewport.location.y * scale)
        icon_top += round(self.comp_icon_offset.height * scale)
        icon_width = round(self.comp_icon_size.width * scale)
        icon_height = round(self.comp_icon_size.height * scale)
        icon_rect = Graphene.Rect()
        icon_rect.init(icon_left, icon_top, icon_width, icon_height)
        snapshot.append_scaled_texture(icon_texture, Gsk.ScalingFilter.TRILINEAR, icon_rect)

        # Determine which badges to draw
        badges = []
        if component.constructed:
            badges.append('constructed-true')
        else:
            badges.append('constructed-false')
        if component.__class__ == Building:
            if component.standby:
                badges.append('standby-true')
            else:
                badges.append('standby-false')
        if len(component.errors) > 0:
            badges.append('errors-true')

        # Load up the badge textures
        for badge in badges:
            badge_texture = self.get_texture('badges', badge)
            if not badge_texture:
                badge_filename = f'{BASE_IMAGE_FILE_PATH}/badges/{badge}.svg'
                self.load_texture(badge_filename, 'badges', badge)

        # And then draw the badges
        badges_width = self.comp_badge_size.width * len(badges) + \
            self.comp_badge_padding_x * (len(badges) - 1)
        for i in range(len(badges)):
            badge_left = round(self.comp_size.width * scale / 2) - round(badges_width * scale / 2)
            badge_left += round(i * (self.comp_badge_size.width + self.comp_badge_padding_x) * scale)
            badge_left += round(location.x * scale)
            badge_left -= round(self.viewport.location.x * scale)
            badge_top = round(self.comp_badge_offset_y * scale)
            badge_top -= round(self.viewport.location.y * scale)
            badge_top += round(location.y * scale)
            badge_rect = Graphene.Rect()
            badge_width = self.comp_badge_size.width * scale
            badge_height = self.comp_badge_size.height * scale
            badge_rect.init(
                badge_left, badge_top,
                badge_width, badge_height)
            snapshot.append_scaled_texture(
                self.get_texture('badges', badges[i]),
                Gsk.ScalingFilter.TRILINEAR,
                badge_rect)


    def draw_frame(self, snapshot):
        '''
        Draws a single frame of the contents of the viewport.
        '''

        self.draw_background(snapshot=snapshot)
        visible_components = self.get_visible_components()
        comps_without_locations = [component[0] for component in visible_components]

        # Determine if any components which are offscreen are attached to any onscreen components.
        # If so, we'll need to include them in the drawing so we can later draw the conveyance.
        offscreen_components = []
        if len(visible_components) > 0:
            for component in comps_without_locations:
                for input in component.inputs:
                    if input.source:
                        input_attachment = input.source.attached_to
                        if isinstance(input_attachment, Conveyance):
                            input_attachment = input_attachment.inputs[0].source.attached_to
                            if input_attachment not in comps_without_locations:
                                if input_attachment.id in self.coordinateMap.keys():
                                    offscreen_components.append((input_attachment,
                                        self.coordinateMap.get(input_attachment.id)))
                for output in component.outputs:
                    if output.target:
                        output_attachment = output.target.attached_to
                        if isinstance(output_attachment, Conveyance):
                            output_attachment = output_attachment.outputs[0].target.attached_to
                            if output_attachment not in comps_without_locations:
                                if output_attachment.id in self.coordinateMap.keys():
                                    offscreen_components.append((output_attachment,
                                        self.coordinateMap.get(output_attachment.id)))

            # Draw those components
            for component, component_location in visible_components:
                self.draw_component(snapshot, component, component_location)

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
            if component.id in self.coordinateMap.keys()
            and not isinstance(component, Conveyance) ]

        # Find components which are visible based on canvas location and size
        canvas_location, canvas_size = self.viewport.get_visible_canvas_region()
        visible_components = []
        for component, component_location in drawable_components:
            if (component_location.x + self.comp_size.width >= canvas_location.x
                and component_location.y + self.comp_size.height >= canvas_location.y) \
            and (component_location.x <= canvas_location.x + canvas_size.width
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

    def load_texture(self,
        filename: str,
        category: str,
        key: str,
    ) -> Gdk.Texture:
        '''
        Loads an image into memory and stores it under the given key in the given category.
        '''

        logging.debug(f'Loading texture from filename: {filename} into {category}/{key}')
        texture = get_texture_from_file(filename)
        if category not in self.__textures.keys():
            self.__textures[category] = {}
        self.__textures[category][key] = texture
        logging.debug(f'Loaded texture: {texture}')
        return texture

    def get_texture(self,
        category: str,
        key: str
    ) -> Gdk.Texture:
        '''
        Retrieves a texture from the cache, or returns None
        '''

        if category in self.__textures.keys() and key in self.__textures[category]:
            return self.__textures[category][key]
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
