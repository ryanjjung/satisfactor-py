import logging
logging.basicConfig()

import gi
gi.require_version('Gsk', '4.0')

from copy import copy
from enum import Enum
from gi.repository import Gsk
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
    'conveyance_radius': 16,
    'conveyance_width': 16,
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

    def __repr__(self):
        return f'<Coordinate2D ({self.x}, {self.y})>'


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

    def __repr__(self):
        return f'<Size2D ({self.width} x {self.height})>'


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

    @property
    def middle(self):
        return Coordinate2D(
            self.left + round(self.width / 2),
            self.top + round(self.height / 2)
        )

    def __repr__(self):
        return f'<Region2D({self.location}, {self.size})>'


class ComponentGeometry(object):
    '''
    Calculates and stores the geometry involved in drawing components on the screen. There are
    several pieces of a component icon, including:

        - background: A colored rectangle behind the icon and badges, which changes color when the
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
        '''
        Calculates the geometry for the bordered background behind the icon, badges, inputs, and
        outputs.
        '''

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
        '''
        Based on the state of the component, calculates the geometry of a series of small badge
        icons beneath the icon showing certain basic facts about the component.
        '''

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
        total_width = round(sizes['badges_x'] * len(self.badges) * scale)
        total_width += round(paddings['badges_x'] * (len(self.badges) - 1) * scale)

        # Calculate each badge's geometry
        i = 0
        for badge in self.badges.keys():
            left = round(self.location.x * scale)  # Start at the left edge
            left += round(sizes['component_x'] * scale / 2)  # Move right to the centerpoint
            left -= round(total_width / 2)  # Go back left by half the width of the whole row
            left += round(i * (sizes['badges_x'] + paddings['badges_x']) * scale ) # Offset from other badges
            left -= round(translate.x * scale)  # Translate

            top = round(self.location.y * scale) # Start at the top edge of the component
            top += round(offsets['badges_y'] * scale) # Move down by a hardcoded vertical offset
            top -= round(translate.y * scale) # Translate

            width = round(sizes['badges_x'] * scale)
            height = round(sizes['badges_y'] * scale)

            self.badges[badge] = Region2D(Coordinate2D(left, top), Size2D(width, height))
            i += 1

    def __calculate_icon(self,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        '''
        Calculates the geometry describing the component's icon.
        '''

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
        '''
        Calculates the geometry for a series of inputs running along the left side of the
        background.
        '''

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
        label_width: int,
        label_height: int,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        '''
        Calculates the geometry describing the textual label beneath the component. This requires
        that we already know the size of the label. That means using Pango to create the layout
        somewhere else, then using PangoLayout.get_pixel_size() to determine the label_width and
        label_height parameters to this function.
        '''

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
        '''
        Calculates the geometry for a series of outputs running along the right side of the
        background.
        '''

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
        label_width: int,
        label_height: int,
        scale: float = 1.0,
        translate: Coordinate2D = Coordinate2D()
    ):
        '''
        Calculates the full set of geometry describing the different pieces of a component icon.
        The dimensions of the label must already be known. That means using Pango to lay out the
        text and then running PangoLayout.get_pixel_size() to form the label_width and label_height
        parameters to this function.
        '''

        self.__calculate_background(scale, translate)
        self.__calculate_badges(scale, translate)
        self.__calculate_icon(scale, translate)
        self.__calculate_inputs(scale, translate)
        self.__calculate_label(
            label_width,
            label_height,
            scale,
            translate)
        self.__calculate_outputs(scale, translate)

    @property
    def bounds(self) -> Region2D:
        '''
        Returns a rectangle which encompasses the entire component.
        '''

        # The lowest x value will either be an input or the label
        if len(self.inputs) == 0:
            left = self.label.left
        else:
            left = min(self.label.left, self.inputs[0].left)

        # The highest x value will either be an output or the label
        if len(self.outputs) == 0:
            width = self.label.right - left
        else:
            width = max(self.label.right, self.outputs[0].right) - left

        # The lowest y value will always be the top of the background
        top = self.background.top

        # The highest y value will always be the bottom of the label
        height = self.label.bottom - top

        return Region2D(
            Coordinate2D(left, top),
            Size2D(width, height)
        )


class ConveyanceGeometry(object):
    '''
    Calculates the pathing used to draw conveyances on the screen.
    '''

    def __init__(self,
        conveyance: Conveyance = None,
        source_comp: Component = None,  # The component connected to the conveyance's input
        source_geo: ComponentGeometry = None,  # The source component's pre-calculated geometry
        source_output: int = None,  # The index of the source component's output this connects to
        target_comp: Component = None,  # The component connected to the conveyance's output
        target_geo: ComponentGeometry = None,  # The target component's pre-calculated geometry
        target_input: int = None,  # The index of the target component's input this connects to
    ):
        self.conveyance = conveyance
        self.geometry = None
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

    def __calculate_label(self,
        label_width: int,
        label_height: int,
    ):
        '''
        Calculate the geometry for the conveyance's label
        '''

        # TODO: Do we need to rotate the geometry here?
        left = self.geometry.midpoint.x - round(label_width / 2)
        top = self.geometry.midpoint.y - round(label_height / 2)
        self.label = Region2D(
            Coordinate2D(left, top),
            Size2D(label_width, label_height)
        )
        logging.debug(f'Label region: {self.label}')


    def __calculate_turns(self,
        scale: float = 1.0,
    ):
        if self.source_comp and self.target_comp:
            # Set up the "source point" - the place where the line starts at the conveyance's input
            self.source_pt = copy(self.source_geo.outputs[self.source_output].middle)

            # Set up the "target point" - the place where the line ends at the conveyance's output
            self.target_pt = copy(self.target_geo.inputs[self.target_input].middle)

            # Set the width of the line
            self.width = round(sizes['input_y'] * scale)

            # Build the two-turn geometry that describes the conveyance
            self.geometry = ConveyanceTwoTurnGeometry(
                    self.conveyance,
                    self.source_geo.outputs[self.source_output],
                    self.target_geo.inputs[self.target_input])
            self.geometry.calculate()

            # Build a Gsk.Path to draw the conveyance by constructing a string describing it.
            # https://docs.gtk.org/gsk4/type_func.Path.parse.html

            # Start at the source point
            path_str = f'M {self.source_pt.x} {self.source_pt.y} '

            # Focus on the first turn
            point1 = self.geometry.turns[0].point1
            point2 = self.geometry.turns[0].point2
            ctrl_pt = self.geometry.turns[0].control_point

            # Draw a line to the first turn
            path_str += f'L {point1.x} {point1.y} '

            # Draw a quadratic bezier curve around the turn radius
            path_str += f'Q {ctrl_pt.x} {ctrl_pt.y} {point2.x} {point2.y} '

            # Focus on the second turn
            point1 = self.geometry.turns[1].point1
            point2 = self.geometry.turns[1].point2
            ctrl_pt = self.geometry.turns[1].control_point

            # Draw a line to the second turn
            path_str += f'L {point1.x} {point1.y} '

            # Draw a bezier curve around the turn radius
            path_str += f'Q {ctrl_pt.x} {ctrl_pt.y} {point2.x} {point2.y} '

            # Draw a line to the target point
            path_str += f'L {self.target_pt.x} {self.target_pt.y}'   # Line to the target point

            # Try to parse the path string
            self.path = Gsk.Path.parse(path_str)
            success, path_bounds = self.path.get_bounds()
            if success:
                # Determine the rectangle representing the outer boundary of this path when drawn
                self.bounds = Region2D(
                    Coordinate2D(
                        path_bounds.get_x(),
                        path_bounds.get_y() - round(sizes['conveyance_width'] / 2 * scale),
                    ),
                    Size2D(
                        path_bounds.get_width(),
                        path_bounds.get_height() + round(sizes['conveyance_width'] * scale)
                    )
                )
            else:
                logging.debug(f'Failed to get the path bounds for "{self.conveyance}"')
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

    def calculate(self,
        label_width: int,
        label_height: int,
        scale: float = 1.0
    ):
        self.__calculate_turns(scale)
        self.__calculate_label(label_width, label_height)


class ConveyanceTurnDirection(Enum):
    '''
    Enum of values representing the flow of conveyance from one side of an imagined square to
    another which shares a right angle.
    '''

    TOP_TO_LEFT     = 1
    TOP_TO_RIGHT    = 2
    RIGHT_TO_TOP    = 3
    RIGHT_TO_BOTTOM = 4
    BOTTOM_TO_RIGHT = 5
    BOTTOM_TO_LEFT  = 6
    LEFT_TO_BOTTOM  = 7
    LEFT_TO_TOP     = 8


class ConveyanceTurnGeometry(object):
    '''
    Represents the points in a single right-angle conveyance turn.
    '''

    def __init__(self,
        control_point: Coordinate2D,
        midpoint: Coordinate2D,
        direction: ConveyanceTurnDirection,
    ):
        self.control_point = control_point
        self.midpoint = midpoint
        self.direction = direction
        self.point1 = None
        self.point2 = None

    def calculate(self,
        scale: float = 1.0,
    ):
        '''
        Calculates the geometry of a right-angle turn based on the points provided at construction
        time.

            - control_point: The control point of the bezier curve. This should be vertically
                aligned with the connection and horizontally centered between two components.
            - midpoint: The perfect center of the conveyance path.
        '''

        # Concieve of a circle of a certain radius
        radius = round(sizes['conveyance_radius'] * scale)

        # The perfect top-center point of this circle is aligned to the control and midpoints, etc.
        top = Coordinate2D(self.midpoint.x, self.control_point.y - radius)
        bottom = Coordinate2D(self.midpoint.x, self.control_point.y + radius)
        left = Coordinate2D(self.midpoint.x - radius, self.control_point.y)
        right = Coordinate2D(self.midpoint.x + radius, self.control_point.y)

        # The turn connects two adjacent sides which share a right angle. Set these up based on the
        # direction described by the enum.
        if self.direction == ConveyanceTurnDirection.TOP_TO_LEFT:
            self.point1 = top
            self.point2 = left
        elif self.direction == ConveyanceTurnDirection.TOP_TO_RIGHT:
            self.point1 = top
            self.point2 = right
        elif self.direction == ConveyanceTurnDirection.RIGHT_TO_TOP:
            self.point1 = right
            self.point2 = top
        elif self.direction == ConveyanceTurnDirection.RIGHT_TO_BOTTOM:
            self.point1 = right
            self.point2 = bottom
        elif self.direction == ConveyanceTurnDirection.BOTTOM_TO_RIGHT:
            self.point1 = bottom
            self.point2 = right
        elif self.direction == ConveyanceTurnDirection.BOTTOM_TO_LEFT:
            self.point1 = bottom
            self.point2 = left
        elif self.direction == ConveyanceTurnDirection.LEFT_TO_BOTTOM:
            self.point1 = left
            self.point2 = bottom
        elif self.direction == ConveyanceTurnDirection.LEFT_TO_TOP:
            self.point1 = left
            self.point2 = top


class ConveyanceTwoTurnGeometry(object):
    '''
    Contains the geometry that represents the right-angle turns in conveyance lines. Since a
    conveyance transports things from one component's output to another component's input, the
    `output_region` is the Region2D describing the source component's output which is hooked to the
    conveyance's input. The `input_region` is the Region2D describing the target component's input
    which is hooked to the conveyance's output.

    When this is drawn, it will show a path which extends from an output horizontally to a point
    halfway closer to the target input. A right angle turn is then drawn in the vertical direction
    toward the input. A vertical line is drawn, then a second turn in the horizontal direction of
    the input. A horizontal line is then drawn to complete the path to the input. `turn_1` is
    therefore the first of these turns (coming off the output), while `turn_2` is the second (going
    into the input).
    '''

    def __init__(self,
        conveyance: Conveyance,
        output_region: Region2D,  # Region of the output the conveyance is connected to
        input_region: Region2D,   # Region of the input the conveyance is connected to
        scale: float = 1.0
    ):
        self.conveyance = conveyance
        self.output_region = output_region
        self.input_region = input_region
        self.midpoint = Coordinate2D()
        self.turns = []
        self.scale = scale

    def calculate(self,
        scale: float = 1.0
    ):
        '''
        Calculates the geometry of the conveyance based on the orientation of its connected
        components.
        '''

        # Determine which kind of turns these will be
        turn1_dir = None
        turn2_dir = None

        # The target is to the right of the source
        if self.input_region.left >= self.output_region.left:
            # The target is above the source
            if self.input_region.top < self.output_region.top:
                turn1_dir = ConveyanceTurnDirection.LEFT_TO_TOP
                turn2_dir = ConveyanceTurnDirection.BOTTOM_TO_RIGHT
            else:  # The target is below the source
                turn1_dir = ConveyanceTurnDirection.LEFT_TO_BOTTOM
                turn2_dir = ConveyanceTurnDirection.TOP_TO_RIGHT
        # The target is to the left of the source
        else:
            # The target is above the source
            if self.input_region.top < self.output_region.top:
                turn1_dir = ConveyanceTurnDirection.RIGHT_TO_TOP
                turn2_dir = ConveyanceTurnDirection.BOTTOM_TO_LEFT
            else:  # The target is below the source
                turn1_dir = ConveyanceTurnDirection.RIGHT_TO_BOTTOM
                turn2_dir = ConveyanceTurnDirection.TOP_TO_LEFT

        # Determine the horizontal halfway point between the two connections
        middle_x = round((self.input_region.middle.x - self.output_region.middle.x) / 2)
        middle_x += self.output_region.middle.x

        # Determine the vertical halfway point
        middle_y = round((self.input_region.middle.y - self.output_region.middle.y) / 2)
        middle_y += self.input_region.middle.y

        # That is the perfect midpoint
        self.midpoint = Coordinate2D(middle_x, middle_y)

        # Generate the geometry of the two turns
        self.turns = [
            ConveyanceTurnGeometry(
                Coordinate2D(self.midpoint.x, self.output_region.middle.y),
                self.midpoint,
                turn1_dir
            ),
            ConveyanceTurnGeometry(
                Coordinate2D(self.midpoint.x, self.input_region.middle.y),
                self.midpoint,
                turn2_dir
            ),
        ]
        for turn in self.turns:
            turn.calculate(self.scale)
