import logging
logging.basicConfig()

import gi
gi.require_version('Pango', '1.0')

from gi.repository import Pango
from satisfactor_py.base import Building, Component

# Hardcoded layout data
offsets = {
    'badges_y': 78,
    'icon_x': 32,
    'icon_y': 8,
    'label_y': 100
}
paddings = {
    'badges_x': 8
}
sizes = {
    'badges_x': 16,
    'badges_y': 16,
    'component_x': 128,
    'component_y': 128,
    'icon_x': 64,
    'icon_y': 64
}


class Coordinate2D(object):
    '''
    A simple class used to pass around 2-dimensional coordinates.

        - x: Location on the left-to-right x axis
        - y: Location on the top-to-bottom y axis
    '''

    def __init__(self,
        x: int = 0,
        y: int = 0
    ):
        self.x = x
        self.y = y


class Size2D(object):
    '''
    A simple class used to pass around 2-dimensional size data.

        - width: Length of the size on the left-to-right x axis
        - height: Length of the size on the top-to-bottom y axis
    '''

    def __init__(self,
        width: int = 1,
        height: int = 1
    ):
        self.width = width
        self.height = height


class Region2D(object):
    '''
    Convenience class for storing rectangular region geometry
    '''

    def __init__(self,
        location: Coordinate2D = Coordinate2D(),
        size: Size2D = Size2D()
    ):
        self.location = location
        self.size = size
    
    @property
    def left(self):
        return self.location.x
    
    @property
    def top(self):
        return self.location.y
    
    @property
    def width(self):
        return self.size.width
    
    @property
    def height(self):
        return self.size.height
    
    @property
    def right(self):
        return self.left + self.width
    
    @property
    def bottom(self):
        return self.top + self.height
    
    def to_string(self):
        return f'({self.left}, {self.top}); ({self.width} x {self.height})'


class ComponentGeometry(object):
    '''
    Calculates and stores the geometry involved in drawing components on the screen. There are
    several pieces of a component icon, including:

        - background: A colored rectangle behind the icon and badges which changes color when the
            component is selected.
        - icon: An image of the component
        - badges: A series of small graphics in a row beneath the icon which indicate basic info
            about the component, such as whether it has been constructed in a real game, has errors,
            or is in standby mode.
        - inputs: Icons overlapping the background on the left indicating the component's inputs.
        - outputs: Icons overlapping the background on the right indicating the component's outputs.
        - label: Text running beneath the background displaying the component's name.
    
    Refer to static/images/component-layout.svg for a visual guide.
    '''
    
    def __init__(self,
        component: Component,
        location: Coordinate2D,
        font_family: str = 'Sans',
        font_size: int = 10,
    ):
        self.component = component
        self.location = location
        
        # The things we'll calculate
        self.badges = None
        self.icon = None
        self.label = None

    def __calculate_background(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        pass

    def __calculate_badges(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        # Determine which badges to include
        self.badges = {}
        if self.component.constructed:
            self.badges['constructed-true'] = Region2D()
        else:
            self.badges['constructed-false'] = Region2D()
        if issubclass(self.component.__class__, Building):
            if self.component.standby:
                self.badges['standby-true'] = Region2D()
            else:
                self.badges['standby-false'] = Region2D()
        if len(self.component.errors) > 0:
            self.badges['errors-true'] = Region2D()
        logging.debug(f'badges: {self.badges}')
        
        # The badges must be centered below the icon; calculate the total width
        total_width = round(sizes['badges_x'] * len(self.badges)
            + paddings['badges_x'] * (len(self.badges) - 1)
            * scale)

        # Calculate each badge's geometry
        i = 0
        for badge in self.badges.keys():
            left = self.location.x               # Start at the left edge of the component
            left += sizes['component_x'] / 2 # Right to the centerpoint of the component
            left -= total_width / 2              # Left by half the width of the whole row
            left += i * (sizes['component_x'] + paddings['badges_x']) # Offset to the right
            left -= translate.x                  # Translate and scale
            left = round(left * scale)

            top = self.location.y                # Start at the top edge of the component
            top += offsets['badges_y']           # Down by a hardcoded vertical offset
            top -= translate.y                   # Translate and scale
            top = round(top * scale)

            self.badges[badge] = Region2D(Coordinate2D(left, top),
                Size2D(sizes['badges_x'], sizes['badges_y']))
            logging.debug(f'Badge {badge} for component {self.component} has region: {self.badges[badge].to_string()}')
            i += 1

    def __calculate_icon(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        left = self.location.x + offsets['icon_x']
        left -= translate.x
        left = round(left * scale)

        top = self.location.y + offsets['icon_y']
        top -= translate.y
        top = round(top * scale)

        self.icon = Region2D(Coordinate2D(left, top),
            Size2D(sizes['icon_x'], sizes['icon_y']))

    def __calculate_inputs(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        pass

    def __calculate_label(self,
        pango_context: Pango.Context,
        font_family: str = 'Sans',
        font_size: int = 10,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        # We can only determine the size of the label by actually laying it out with Pango
        font = Pango.FontDescription.new()
        font.set_family(font_family)
        font.set_size(font_size * Pango.SCALE)
        pango_layout = Pango.Layout(pango_context)
        pango_layout.set_font_description(font)
        pango_layout.set_text(self.component.name)
        label_width, label_height = pango_layout.get_pixel_size()
        label_size = Size2D(
            round(label_width * scale),
            round(label_height * scale))

        # Center the text under the icon
        left = self.location.x  # Start at the canvas location
        left += sizes['component_x'] / 2  # Move right to the center of the component
        left -= label_size.width / 2  # Left by half the width of the label to center it
        left -= translate.x     # Translate and scale
        left = round(left * scale)

        top = self.location.y  # Start at the canvas location
        top += offsets['label_y']  # Move down by a hardcoded offset
        top -= translate.y  # Translate and scale
        top = round(top * scale)

        self.label = Region2D(Coordinate2D(left, top), label_size)

    def __calculate_outputs(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D
    ):
        pass

    def calculate(self,
        pango_context: Pango.Context,
        font_family: str = 'Sans',
        font_size: int = 10,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        self.__calculate_background(scale, translate)
        self.__calculate_badges(scale, translate)
        self.__calculate_icon(scale, translate)
        self.__calculate_inputs(scale, translate)
        self.__calculate_label(
            pango_context,
            font_family,
            font_size,
            scale,
            translate)
        self.__calculate_outputs(scale, translate)
