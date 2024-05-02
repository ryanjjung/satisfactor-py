import logging
logging.basicConfig()

import gi
gi.require_version('Pango', '1.0')

from gi.repository import Gsk, Pango
from satisfactor_py.base import Building, Component, Conveyance

# Hardcoded layout data
offsets = {
    'background_x': 12,
    'background_y': 4,
    'badges_y': 78,
    'icon_x': 32,
    'icon_y': 8,
    'input_x': 4,
    'label_y': 100,
    'output_x': 106,
}
paddings = {
    'badges_x': 8,
    'inputs_y': 4,
    'outputs_y': 4,
}
sizes = {
    'background_x': 104,
    'background_y': 94,
    'badges_x': 16,
    'badges_y': 16,
    'component_x': 128,
    'component_y': 128,
    'conveyance_width': 4,
    'icon_x': 64,
    'icon_y': 64,
    'input_x': 16,
    'input_y': 16,
    'output_x': 16,
    'output_y': 16,
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
        self.background = None
        self.badges = None
        self.icon = None
        self.inputs = None
        self.label = None
        self.outputs = None

    def __calculate_background(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        left = round(self.location.x * scale)
        left += round(offsets['background_x'] * scale)
        left -= round(translate.x * scale)

        top = round(self.location.y * scale)
        top += round(offsets['background_y'] * scale)
        top -= round(translate.y * scale)

        width = round(sizes['background_x'] * scale)
        height = round(sizes['background_y'] * scale)

        self.background = Region2D(Coordinate2D(left, top), Size2D(width, height))

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

        # The badges must be centered below the icon; calculate the total width
        total_width = round(sizes['badges_x'] * len(self.badges)
            + paddings['badges_x'] * (len(self.badges) - 1)
            * scale)

        # Calculate each badge's geometry
        i = 0
        for badge in self.badges.keys():
            left = round(self.location.x * scale)               # Start at the left edge of the component
            left += round(sizes['component_x'] * scale / 2)     # Right to the centerpoint of the component
            left -= round(total_width * scale / 2)              # Left by half the width of the whole row
            left += round(i * (sizes['badges_x'] + paddings['badges_x']) * scale ) # Offset to the right
            left -= round(translate.x * scale)                  # Translate and scale

            top = round(self.location.y * scale)                # Start at the top edge of the component
            top += round(offsets['badges_y'] * scale)           # Down by a hardcoded vertical offset
            top -= round(translate.y * scale)                   # Translate and scale

            width = round(sizes['badges_x'] * scale)
            height = round(sizes['badges_y'] * scale)

            self.badges[badge] = Region2D(Coordinate2D(left, top), Size2D(width, height))
            i += 1

    def __calculate_icon(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        left = round(self.location.x * scale)
        left += round(offsets['icon_x'] * scale)
        left -= round(translate.x * scale)

        top = round(self.location.y * scale)
        top += round(offsets['icon_y'] * scale)
        top -= round(translate.y * scale)

        width = round(sizes['icon_x'] * scale)
        height = round(sizes['icon_y'] * scale)

        self.icon = Region2D(Coordinate2D(left, top), Size2D(width, height))

    def __calculate_inputs(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        total_height = max(round(sizes['input_y'] * len(self.component.inputs)
            + paddings['inputs_y'] * (len(self.component.inputs) - 1)
            * scale), 0)

        left = round(self.location.x * scale)
        left += round(offsets['input_x'] * scale)
        left -= round(translate.x * scale)

        width = round(sizes['input_x'] * scale)
        height = round(sizes['input_y'] * scale)

        self.inputs = []
        i = 0
        for input in self.component.inputs:
            top = round(self.location.y * scale)
            top += round(offsets['icon_y'] * scale)  # Start at the top of the icon
            top += round(sizes['icon_y'] * scale / 2)  # Move down by half the height of the icon
            top -= round(total_height * scale / 2)  # Move back up by half the height of the full input bar
            top += round(i * (sizes['input_y'] + paddings['inputs_y']) * scale)  # Offset down
            top -= round(translate.y * scale)

            self.inputs.append(Region2D(Coordinate2D(left, top), Size2D(width, height)))
            i += 1

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
        font.set_size(font_size * scale * Pango.SCALE)
        pango_layout = Pango.Layout(pango_context)
        pango_layout.set_font_description(font)
        pango_layout.set_text(self.component.name)
        label_width, label_height = pango_layout.get_pixel_size()
        label_size = Size2D(label_width, label_height)

        # Center the text under the icon
        left = round(self.location.x * scale)  # Start at the canvas location
        left += round(sizes['component_x'] * scale / 2)  # Move right to the center of the component
        left -= round(label_size.width / 2)  # Left by half the width of the label to center it
        left -= round(translate.x)     # Translate and scale

        top = round(self.location.y * scale)  # Start at the canvas location
        top += round(offsets['label_y'] * scale)  # Move down by a hardcoded offset
        top -= round(translate.y)  # Translate and scale

        self.label = Region2D(Coordinate2D(left, top), label_size)

    def __calculate_outputs(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D
    ):
        total_height = max(round(sizes['output_y'] * len(self.component.outputs)
            + paddings['outputs_y'] * (len(self.component.outputs) - 1)
            * scale), 0)

        left = round(self.location.x * scale)
        left += round(offsets['output_x'] * scale)
        left -= round(translate.x * scale)

        self.outputs = []
        i = 0
        for output in self.component.outputs:
            top = round(self.location.y * scale)
            top += round(offsets['icon_y'] * scale)  # Start at the top of the icon
            top += round(sizes['icon_y'] * scale / 2)  # Move down by half the height of the icon
            top -= round(total_height * scale / 2)  # Move back up by half the height of the full output bar
            top += round(i * (sizes['output_y'] + paddings['outputs_y']) * scale)  # Offset down
            top -= round(translate.y * scale)

            width = round(sizes['output_x'] * scale)
            height = round(sizes['output_y'] * scale)

            self.outputs.append(Region2D(Coordinate2D(left, top), Size2D(width, height)))
            i += 1

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


class ConveyanceGeometry(object):
    '''
    Calculates the pathing used to draw conveyances on the screen.
    '''

    def __init__(self,
        conveyance: Conveyance,
        source_comp: Component,
        source_geo: ComponentGeometry,
        source_output: int,
        target_comp: Component,
        target_geo: ComponentGeometry,
        target_input: int,
    ):
        self.conveyance = conveyance
        self.source_comp = source_comp
        self.source_geo = source_geo
        self.source_output = source_output
        self.target_comp = target_comp
        self.target_geo = target_geo
        self.target_input = target_input
        self.width = sizes['conveyance_width']

        self.path = None
        self.source_pt = Coordinate2D()  # The point to start the path at
        self.source_cp = Coordinate2D()  # The control point for the curve leaving the source
        self.target_pt = Coordinate2D()  # The point to end the path at
        self.target_cp = Coordinate2D()  # The control point for the curve entering the target
        self.midpoint = Coordinate2D()   # The middle point of the vertical portion of the line

    def calculate(self,
        scale: float = 1.0
    ):
        self.width = round(4 * scale)
        if self.source_comp and self.target_comp:
            self.source_pt = self.source_geo.outputs[self.source_output].location
            self.target_pt = self.target_geo.inputs[self.target_input].location

            midpoint_x = round((self.target_pt.x - self.source_pt.x) / 2) + self.source_pt.x
            midpoint_y = round((self.target_pt.y - self.source_pt.y) / 2) + self.source_pt.y

            self.source_cp = Coordinate2D(midpoint_x, self.source_pt.y)
            self.target_cp = Coordinate2D(midpoint_x, self.target_pt.y)
            self.midpoint = Coordinate2D(midpoint_x, midpoint_y)

            path_str = f'M {self.source_pt.x} {self.source_pt.y} '
            path_str += f'Q {self.source_cp.x} {self.source_cp.y} {midpoint_x} {midpoint_y}'
            path_str += f'Q {self.target_cp.x} {self.target_cp.y} {self.target_pt.x} {self.target_pt.y}'
            logging.debug(f'Path string: {path_str}')
            self.path = Gsk.Path.parse(path_str)
        else:
            self.source_geo = None
            self.source_output = None
            self.source_pt = None
            self.source_cp = None
            self.target_geo = None
            self.target_input = None
            self.target_pt = None
            self.target_cp = None
            self.midpoint = None
