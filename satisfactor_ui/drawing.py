import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gsk', '4.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Pango', '1.0')

import pickle
from gi.repository import Gdk, Graphene, Gsk, Gtk, Pango
from satisfactor_py.base import Building, Component, Conveyance
from satisfactor_py.factories import Factory
from satisfactor_ui.geometry import (
    sizes,
    ComponentGeometry,
    ConveyanceGeometry,
    Coordinate2D,
    Region2D,
    Size2D
)


BASE_IMAGE_FILE_PATH = './static/images'
FIRST_RUN=True

COLORS = {
    'comp_bg_deselected': None,
    'comp_bg_selected': None,
    'comp_bg_border': None,
    'comp_label': None,
    'conn_bg': None,
    'conn_deselected': None,
    'conn_selected': None,
    'conn_label': None,
}

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
        factory: Factory = Factory(),
        background_color: str = '#383875',
        component_bg_color: str = '#14132d',
        component_border_color: str = '#a3a8fa',
        connection_bg_color: str = '#403d7a',
        conveyance_label_color: str = '#383875',
        conveyance_font_family: str = 'Sans',
        conveyance_font_size: float = 8.0,
        label_color: str = '#a3a8fa',
        label_font_family: str = 'Sans',
        label_font_size: float = 10.0,
        line_color: str = '#a3a8fa',
        selected_component_bg_color: str = '#95d0ff',
        selected_line_color: str = '#95d0ff',
        viewport_region: Region2D = Region2D()
    ):
        self.factory = factory

        # Set up a few internals
        self.geometry = {} # Mapping of component UUIDs to ComponentGeometry objects
        self.selected = None  # Pointer to currently selected component, if any
        self.viewport = Viewport(region=viewport_region) # The currently visible area

        # Set up colors
        self.background_color = background_color
        self.component_bg_color = component_bg_color
        self.component_border_color = component_border_color
        self.connection_bg_color = connection_bg_color
        self.conveyance_label_color = conveyance_label_color
        self.conveyance_font_family = conveyance_font_family
        self.conveyance_font_size = conveyance_font_size
        self.label_color = label_color
        self.line_color = line_color
        self.selected_component_bg_color = selected_component_bg_color
        self.selected_line_color = selected_line_color

        # Set up fonts
        self.label_font_family = label_font_family
        self.label_font_size = label_font_size

        # Track whether the geometry needs to be recalculated
        self.__invalid_geo = False

    @staticmethod
    def load(filename: str):
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

    def invalidate_geometry(self):
        self.__invalid_geo = True

    def add_component(self,
        component: Component,
        canvas_location: Coordinate2D
    ):
        '''
        Adds a component to the factory and sets up its coordinate mapping
        '''

        self.factory.add([component])
        if isinstance(component, Conveyance):
            source_comp = None
            target_comp = None
            if component.inputs[0].source:
                source_comp = component.inputs[0].source.attached_to
            if component.outputs[0].target:
                target_comp = component.outputs[0].target.attached_to
            if source_comp and target_comp:
                self.geometry[component.id] = ConveyanceGeometry(
                    component,
                    source_comp,
                    self.geometry[source_comp.id],
                    source_comp.outputs.index(component.inputs[0].source),
                    target_comp,
                    self.geometry[target_comp.id],
                    target_comp.inputs.index(component.outputs[0].target),
                )
        else:
            self.geometry[component.id] = ComponentGeometry(component, canvas_location)

    def draw_widget_background(self,
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

        background_color = Gdk.RGBA()
        background_color.parse(self.background_color)
        rect = Graphene.Rect().init(0, 0, self.viewport.region.width, self.viewport.region.height)
        snapshot.push_clip(rect)
        snapshot.append_color(background_color, rect)
        snapshot.pop()

    def draw_component(self,
        widget: Gtk.Widget,
        snapshot: Gdk.Snapshot,
        component: Component,
        geometry: ComponentGeometry,
        label  # PangoTextLabel
    ):
        '''
        Draws a graphical representation of a factory component on the screen.
        '''

        self.draw_component_background(widget, snapshot, component, geometry, self.viewport.scale)
        self.draw_component_icon(widget, snapshot, component, geometry, self.viewport.scale)
        self.draw_component_badges(widget, snapshot, component, geometry, self.viewport.scale)
        self.draw_component_label(widget, snapshot, component, geometry, label, self.viewport.scale)
        self.draw_component_inputs(widget, snapshot, component, geometry, self.viewport.scale)
        self.draw_component_outputs(widget, snapshot, component, geometry, self.viewport.scale)

    def draw_component_background(self,
        widget: Gtk.Widget,
        snapshot: Gdk.Snapshot,
        component: Component,
        geometry: ComponentGeometry,
        scale: float
    ):
        # Set up the colors
        if not COLORS['comp_bg_selected']:
            COLORS['comp_bg_selected'] = Gdk.RGBA()
            COLORS['comp_bg_selected'].parse(self.selected_component_bg_color)
        if not COLORS['comp_bg_deselected']:
            COLORS['comp_bg_deselected'] = Gdk.RGBA()
            COLORS['comp_bg_deselected'].parse(self.selected_component_bg_color)
        if not COLORS['comp_bg_border']:
            COLORS['comp_bg_border'] = Gdk.RGBA()
            COLORS['comp_bg_border'].parse(self.component_border_color)

        # Set up the rounded rectangle
        geo = geometry.background
        rect = Graphene.Rect().init(geo.left, geo.top, geo.width, geo.height)
        rounded_rect = Gsk.RoundedRect()
        rounded_rect.init_from_rect(rect, radius=4)

        # Define the border
        border_colors = [
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
        ]
        border_sizes = [2.0, 2.0, 2.0, 2.0]

        # Define the background
        bg_color = COLORS['comp_bg_selected'] if component == self.selected \
            else COLORS['comp_bg_deselected']

        # Do the drawing
        snapshot.push_rounded_clip(rounded_rect)
        snapshot.append_color(bg_color, rect)
        snapshot.append_border(rounded_rect, border_sizes, border_colors)
        snapshot.pop()

    def draw_component_badges(self,
        widget: Gtk.Widget,
        snapshot: Gdk.Snapshot,
        component: Component,
        geometry: ComponentGeometry,
        scale: float
    ):
        '''
        Draws only the component's badges
        '''

        # Load up the badge textures
        for badge in geometry.badges.keys():
            badge_texture = widget.get_texture('badges', badge)
            if not badge_texture:
                badge_filename = f'{BASE_IMAGE_FILE_PATH}/badges/{badge}.svg'
                badge_texture = widget.load_texture(badge_filename, 'badges', badge)

        # And then draw the badges
        for badge, badge_region in geometry.badges.items():
            badge_rect = Graphene.Rect()
            badge_rect.init(
                badge_region.left, badge_region.top,
                badge_region.width, badge_region.height)
            snapshot.append_scaled_texture(
                widget.get_texture('badges', badge),
                Gsk.ScalingFilter.TRILINEAR,
                badge_rect)

    def draw_component_icon(self,
        widget: Gtk.Widget,
        snapshot: Gdk.Snapshot,
        component: Component,
        geometry: ComponentGeometry,
        scale: float
    ):
        '''
        Draws only the icon portion of a component
        '''

        # Load up the component icon texture
        icon_key = component.__class__.__name__
        icon_texture = widget.get_texture('components', icon_key)
        if not icon_texture:
            filename = f'{BASE_IMAGE_FILE_PATH}/components/{icon_key}.png'
            icon_texture = widget.load_texture(filename, 'components', icon_key)

        # Draw the icon
        icon_rect = Graphene.Rect()
        icon_rect.init(
            geometry.icon.left,
            geometry.icon.top,
            geometry.icon.width,
            geometry.icon.height)
        snapshot.append_scaled_texture(icon_texture, Gsk.ScalingFilter.TRILINEAR, icon_rect)

    def draw_component_inputs(self,
        widget: Gtk.Widget,
        snapshot: Gdk.Snapshot,
        component: Component,
        geometry: ComponentGeometry,
        scale: float
    ):
        '''
        Draws only the input icons for a component
        '''

        # Load up the input texture:
        input_texture = widget.get_texture('badges', 'input')
        if not input_texture:
            filename = f'{BASE_IMAGE_FILE_PATH}/badges/input.svg'
            input_texture = widget.load_texture(filename, 'badges', 'input')

        # Set up colors
        if not COLORS['conn_bg']:
            COLORS['conn_bg'] = Gdk.RGBA()
            COLORS['conn_bg'].parse(self.connection_bg_color)
        if not COLORS['comp_bg_border']:
            COLORS['comp_bg_border'] = Gdk.RGBA()
            COLORS['comp_bg_border'].parse(self.component_border_color)
        border_colors = [
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
        ]
        border_sizes = [1.0, 0.0, 1.0, 0.0]

        for input in geometry.inputs:
            input_rect = Graphene.Rect()
            input_rect.init(input.left, input.top, input.width, input.height)
            bg_rect = Gsk.RoundedRect()
            bg_rect.init_from_rect(input_rect, radius=0)

            snapshot.push_rounded_clip(bg_rect)
            snapshot.append_color(bg_color, input_rect)
            snapshot.append_border(bg_rect, border_sizes, border_colors)
            snapshot.pop()

            snapshot.append_scaled_texture(
                input_texture, Gsk.ScalingFilter.TRILINEAR,
                input_rect)

    def draw_component_outputs(self,
        widget: Gtk.Widget,
        snapshot: Gdk.Snapshot,
        component: Component,
        geometry: ComponentGeometry,
        scale: float
    ):
        '''
        Draws only the output icons for a component
        '''

        # Load up the output texture:
        output_texture = widget.get_texture('badges', 'output')
        if not output_texture:
            filename = f'{BASE_IMAGE_FILE_PATH}/badges/output.svg'
            output_texture = widget.load_texture(filename, 'badges', 'output')

        # Set up colors
        if not COLORS['conn_bg']:
            COLORS['conn_bg'] = Gdk.RGBA()
            COLORS['conn_bg'].parse(self.connection_bg_color)
        if not COLORS['comp_bg_border']:
            COLORS['comp_bg_border'] = Gdk.RGBA()
            COLORS['comp_bg_border'].parse(self.component_border_color)
        border_colors = [
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
            COLORS['comp_bg_border'],
        ]
        border_sizes = [1.0, 0.0, 1.0, 0.0]

        for output in geometry.outputs:
            output_rect = Graphene.Rect()
            output_rect.init(output.left, output.top, output.width, output.height)
            bg_rect = Gsk.RoundedRect()
            bg_rect.init_from_rect(output_rect, radius=0)

            snapshot.push_rounded_clip(bg_rect)
            snapshot.append_color(bg_color, output_rect)
            snapshot.append_border(bg_rect, border_sizes, border_colors)
            snapshot.pop()

            snapshot.append_scaled_texture(
                output_texture, Gsk.ScalingFilter.TRILINEAR,
                output_rect)

    def draw_component_label(self,
        widget: Gtk.Widget,
        snapshot: Gdk.Snapshot,
        component: Component,
        geometry: ComponentGeometry,
        label = None, # PangoTextLabel
        scale: float = 1.0
    ):
        # Set up the label and recalculate its geometry
        if not label:
            label = PangoTextLabel(
                component.name,
                self.label_font_family,
                self.label_font_size,
                widget,
                scale)
        geometry._ComponentGeometry__calculate_label(
            *label.layout.get_pixel_size(),
            scale,
            self.viewport.region.location)

        # Set up color
        if not COLORS['comp_label']:
            COLORS['comp_label'] = Gdk.RGBA()
            COLORS['comp_label'].parse(self.label_color)

        # Set up positioning
        point = Graphene.Point()
        point.x = geometry.label.left
        point.y = geometry.label.top

        # Draw the text, translate it, color it
        snapshot.save()
        snapshot.translate(point)
        snapshot.append_layout(label.layout, label_color)
        snapshot.restore()

    def draw_conveyance(self,
        widget: Gtk.Widget,
        snapshot: Gtk.Snapshot,
        conveyance: Conveyance,
        geometry: ConveyanceGeometry,
    ):
        # Set up colors
        if not COLORS['conn_deselected']:
            COLORS['conn_deselected'] = Gdk.RGBA()
            COLORS['conn_deselected'].parse(self.line_color)
        if not COLORS['conn_selected']:
            COLORS['conn_selected'] = Gdk.RGBA()
            COLORS['conn_selected'].parse(self.selected_line_color)
        if not COLORS['conn_label']:
            COLORS['conn_label'] = Gdk.RGBA()
            COLORS['conn_label'].parse(self.conveyance_label_color)

        if self.selected == conveyance:
            line_color = COLORS['conn_selected']
        else:
            line_color = COLORS['conn_deselected']

        # Draw the twice-curving line of the conveyance
        stroke = Gsk.Stroke.new(geometry.width)

        bounds = Graphene.Rect().init(
            geometry.bounds.left,
            geometry.bounds.top,
            geometry.bounds.width,
            geometry.bounds.height
        )
        path = Gsk.Path.parse(geometry.path_str)
        snapshot.push_stroke(path, stroke)
        snapshot.append_color(line_color, bounds)
        snapshot.pop()

        # Draw the label
        text = conveyance.conveyance_type.name.title()
        label = PangoTextLabel(
            text,
            self.conveyance_font_family,
            self.conveyance_font_size,
            widget,
            font_weight=Pango.Weight.MEDIUM,
            scale=self.viewport.scale)
        geometry._ConveyanceGeometry__calculate_label(
            *label.layout.get_pixel_size(),
        )

        # Set up positioning
        point = Graphene.Point()
        point.x = geometry.label.left
        point.y = geometry.label.top

        # Draw the text, translate it, rotate it, color it
        target_top = geometry.target_geo.inputs[geometry.target_input].top
        source_top = geometry.source_geo.outputs[geometry.source_output].top
        if target_top < source_top:
            angle = -90.0
        else:
            angle = 90.0
        snapshot.save()
        snapshot.translate(point)
        snapshot.rotate(angle)
        snapshot.append_layout(label.layout, COLORS['conn_label'])
        snapshot.restore()

    def draw_frame(self,
        widget: Gtk.Widget,
        snapshot: Gtk.Snapshot
    ):
        '''
        Draws a single frame of the contents of the viewport.
        '''

        global FIRST_RUN

        # Make sure the components have geometry
        for id, geometry in self.geometry.items():
            component = self.factory.get_component_by_id(id)
            if not isinstance(component, Conveyance):
                label = PangoTextLabel(
                    component.name,
                    self.label_font_family,
                    self.label_font_size,
                    widget,
                    self.viewport.scale)
                if FIRST_RUN or self.__invalid_geo:
                    logging.debug(f'Forcing geometry calculation for component {id}')
                    geometry.calculate(
                        *label.layout.get_pixel_size(),
                        scale=self.viewport.scale,
                        translate=self.viewport.region.location)
                elif not geometry.background \
                    or not geometry.badges \
                    or not geometry.icon \
                    or not geometry.inputs \
                    or not geometry.label \
                    or not geometry.outputs:
                        geometry.calculate(
                            *label.layout.get_pixel_size(),
                            scale=self.viewport.scale,
                            translate=self.viewport.region.location)

        self.draw_widget_background(snapshot=snapshot)
        visible_component_geometry = self.get_visible_component_geometry()
        visible_components = [component[0] for component in visible_component_geometry]

        # Determine if any components which are offscreen are attached to any onscreen components.
        # If so, we'll need to include them in the drawing so we can later draw the conveyance.
        # NOTE: Do we actually have to do this? We build the geometry for everything, and that
        # should be all we need. Maybe we can delete this code.
        offscreen_components = self.get_offscreen_component_geometry(visible_components)

        # Draw those components
        for component, geometry in visible_component_geometry:
            self.draw_component(widget, snapshot, component, geometry, label)

        # Make sure the conveyances have geometry
        for id, geometry in self.geometry.items():
            conveyance = self.factory.get_component_by_id(id)
            if isinstance(conveyance, Conveyance):
                if geometry.source_comp and geometry.target_comp:
                    label = PangoTextLabel(
                        conveyance.conveyance_type.name.title(),
                        self.conveyance_font_family,
                        self.conveyance_font_size,
                        widget,
                        self.viewport.scale)
                    if FIRST_RUN or self.__invalid_geo:
                        logging.debug(f'Forcing geometry calculation for conveyance {id}')
                        geometry.calculate(
                            *label.layout.get_pixel_size(),
                            self.viewport.scale)
                    elif not geometry.source_pt \
                        or not geometry.target_pt \
                        or not geometry.midpoint \
                        or not geometry.source_cp \
                        or not geometry.target_cp \
                        or not geometry.path:
                            geometry.calculate(
                                *label.layout.get_pixel_size(),
                                self.viewport.scale)

        visible_conveyances = self.get_conveyances_from_components(visible_components)
        # Draw the conveyances between the components
        for component in visible_conveyances:
            if isinstance(component, Conveyance):
                geometry = self.geometry.get(component.id)
                self.draw_conveyance(widget, snapshot, component, geometry)

        if FIRST_RUN: FIRST_RUN = False
        self.__invalid_geo = False

    def get_visible_component_geometry(self) -> list[tuple]:
        '''
        Returns a list of tuples like so:
            (satisfactor_py.base.Component, satisfactor_ui.geometry.ComponentGeometry)

        These components are the ones which are partially or fully visible within the frame of the
        viewport and must be drawn when updating the widget.
        '''

        # Filter out components without coordinate mappings
        drawable_components = [ (component, self.geometry[component.id]) \
            for component in self.factory.components
            if component.id in self.geometry.keys()
            and not isinstance(component, Conveyance) ]

        # Find components which are visible based on canvas location and size
        canvas_region = self.viewport.get_visible_canvas_region()
        visible_components = []
        for component, geometry in drawable_components:
            if (geometry.location.x + sizes['component_x'] >= canvas_region.left
                and geometry.location.y + sizes['component_y'] >= canvas_region.top) \
            and (geometry.location.x <= canvas_region.right
                and geometry.location.y <= canvas_region.top + canvas_region.height):
                    visible_components.append((component, geometry))
        return visible_components

    def get_offscreen_component_geometry(self, visible_components) -> list[tuple]:
        '''
        Returns a list of tuples like so:
            (satisfactor_py.base.Component, satisfactor_ui.geometry.ComponentGeometry)

        These components are ones which are outside of the viewport, but which are connected to
        components which are within the viewport.
        '''

        offscreen_components = []
        if len(visible_components) > 0:
            for component in visible_components:
                for input in component.inputs:
                    if input.source:
                        input_attachment = input.source.attached_to
                        if isinstance(input_attachment, Conveyance):
                            input_attachment = input_attachment.inputs[0].source.attached_to
                            if input_attachment not in visible_components:
                                if input_attachment.id in self.geometry.keys():
                                    offscreen_components.append((input_attachment,
                                        self.geometry.get(input_attachment.id)))
                for output in component.outputs:
                    if output.target:
                        output_attachment = output.target.attached_to
                        if isinstance(output_attachment, Conveyance):
                            output_attachment = output_attachment.outputs[0].target.attached_to
                            if output_attachment not in visible_components:
                                if output_attachment.id in self.geometry.keys():
                                    offscreen_components.append((output_attachment,
                                        self.geometry.get(output_attachment.id)))
        return offscreen_components

    def get_conveyances_from_components(self, components) -> list[tuple]:
        conveyances = []
        for component in components:
            if isinstance(component, Conveyance):
                conveyances.append(component)
            if len(component.inputs) > 0:
                for input in component.inputs:
                    if input.source:
                        if isinstance(input.source.attached_to, Conveyance):
                            if not input.source.attached_to in conveyances:
                                conveyances.append(input.source.attached_to)
            if len(component.outputs) > 0:
                for output in component.outputs:
                    if output.target:
                        if isinstance(output.target.attached_to, Conveyance):
                            if not output.target.attached_to in conveyances:
                                conveyances.append(output.target.attached_to)
        return conveyances

    def get_component_location(self,
        component: Component
    ) -> Coordinate2D:
        '''
        Returns the Coordinate2D mapped to the given component, or (0, 0) if there is no mapping.

            - component: The component whose location you wish to retrieve
        '''

        return self.coordinateMap.get(component.id, Coordinate2D())

    def get_components_under_coordinate(self,
        coordinate: Coordinate2D
    ) -> list[Component]:
        '''
        Returns a list of Components whose geometry contains the given coordinate.
        '''

        components = []
        for id, geometry in self.geometry.items():
            if geometry.bounds.contains(coordinate):
                components.append(self.factory.get_component_by_id(id))
        return components


class PangoTextLabel(object):
    '''
    Represents a textual label drawn with Pango. Used to render text and get its geometry.
    '''

    def __init__(self,
        text: str,
        font_family: str,
        font_size: float,
        widget: Gtk.Widget,
        scale: float = 1.0,
        font_style: Pango.Style = Pango.Style.NORMAL,
        font_weight: Pango.Weight = Pango.Weight.NORMAL,
    ):
        # Set up the font
        self.font = Pango.FontDescription.new()
        self.font.set_family(font_family)
        self.font.set_size(font_size * scale * Pango.SCALE)
        self.font.set_style(font_style)
        self.font.set_weight(font_weight)

        # Set up a layout
        self.pango_ctx = widget.get_pango_context()
        self.layout = Pango.Layout(self.pango_ctx)
        self.layout.set_font_description(self.font)
        self.layout.set_text(text)


class Viewport(object):
    '''
    A 2-dimensional rectangle through which a user views a portion of a Blueprint.

        - location: A 2D coordinate representing the location of the top-left corner of the viewport
            within a blueprint
        - size: A 2D size representing the pixel width and height of the viewport
        - zoom: A factor by which the factory components are made larger or smaller in the viewport
    '''

    def __init__(self,
        region: Region2D = Region2D(),
        scale: float = 1.0
    ):
        self.region = region
        self.scale = scale

    def get_visible_canvas_region(self) -> Region2D:
        return Region2D(self.region.location, Size2D(
            round(self.region.width / self.scale),
            round(self.region.height / self.scale)
        ))
