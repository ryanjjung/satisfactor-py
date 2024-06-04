import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

from enum import Enum
from gi.repository import Gdk, Gtk, Gio, GObject
from pathlib import Path
from satisfactory import (
    base,
    buildings,
    conveyances,
    items,
    recipes,
    storages
)
from factory_designer_gtk import (
    drawing,
    geometry
)
from typing import Any, Callable


# These functions provide support for testing and the widgets in this file

def build_test_blueprint():
    '''
    Builds a simple blueprint that we can test with
    '''

    # Build the factory components
    oreSupply = base.ResourceNode(
        purity=base.Purity.NORMAL,
        name='Iron Ore Resource',
        item=items.IronOre
    )
    miner = buildings.MinerMk1(
        name='Iron Miner',
        recipe=recipes.IronOreMk1,
    )
    smelter = buildings.Smelter(
        name='Iron Ore Smelter',
        recipe=recipes.IronIngot,
        tags={
            'foo': 'bar'
        }
    )
    constructor = buildings.Constructor(
        name='Iron Plate Constructor',
        recipe=recipes.IronPlate
    )
    storage = storages.StorageContainer(name='Plate Storage')

    # Connect them up
    oreSupply.outputs[0].connect(miner.inputs[0])
    convMinerToSmelter = miner.connect(smelter, conveyances.ConveyorBeltMk1)
    convSmelterToConstructor = smelter.connect(constructor, conveyances.ConveyorBeltMk1)
    convConstructorToStorage = constructor.connect(storage, conveyances.ConveyorBeltMk1)

    # Add them to a blueprint with coordinates, except for Conveyances, which don't need them
    blueprint = drawing.Blueprint()
    blueprint.factory.name = 'Test Blueprint'
    blueprint.factory.availability = base.Availability(0, 5)
    blueprint.add_component(oreSupply, geometry.Coordinate2D(50, 20))
    blueprint.add_component(miner, geometry.Coordinate2D(225, 150))
    blueprint.add_component(smelter, geometry.Coordinate2D(380, 100))
    blueprint.add_component(convMinerToSmelter, geometry.Coordinate2D())
    blueprint.add_component(constructor, geometry.Coordinate2D(500, 20))
    blueprint.add_component(convSmelterToConstructor, geometry.Coordinate2D())
    blueprint.add_component(storage, geometry.Coordinate2D(630, 20))
    blueprint.add_component(convConstructorToStorage, geometry.Coordinate2D())
    blueprint.factory.simulate()
    return blueprint

def get_texture_from_file(filename: str) -> Gdk.Texture:
    '''
    Given the filename of an image, returns a Gdk.Texture object for it
    '''
    if Path(filename).exists():
        texture = Gdk.Texture.new_from_filename(filename)
        return texture

    return None


# These classes provide support to the widgets in this file

class ComponentGrabEvent(object):
    '''
    Contains the state we need to remember in order to complete a drag-n-drop of a component.
    '''

    def __init__(self,
        component: base.Component,              # What component is being dragged?
        geometry: geometry.ComponentGeometry,   # What does it look like when drawn?
        pointer_position: geometry.Coordinate2D,  # How far away is the pointer from the origin?
    ):
        self.component = component
        self.geometry = geometry
        self.pointer_position = pointer_position


class InteractionMode(Enum):
    '''
    Discrete set of states the widget can be in with regards to user interaction.

        - NORMAL: The "default" state of the app, as though it has just launched.
        - EXISTING_COMPONENT_SELECTED: A component already placed in the blueprint has been
            selected. Details of the component have been displayed.
        - EXISTING_COMPONENT_GRABBED: A component in the blueprint has had a mouse-down event, then
            a mouse-move event without a mouse-up, indicating we want to move the component.
    '''

    NORMAL                      = 0
    EXISTING_COMPONENT_SELECTED = 1
    EXISTING_COMPONENT_GRABBED  = 2


class PointerState(Enum):
    '''
    Represents the two states of a pointer: either up (not pressed) or down (pressed), used for
    tracking the state of things across events.
    '''

    UP   = 0
    DOWN = 1


# Actual widgets follow here

class FactoryDesignerWidget(Gtk.Widget):
    '''
    A FactoryDesginerWidget is a GTK Widget that draws a factory's components in a 2D visible space
    and allows a user to interact with those components.
    '''

    def __init__(self,
        window: Gtk.ApplicationWindow,
        blueprint: drawing.Blueprint = None
    ):
        super().__init__()

        self.textures = {}  # Texture cache, to be populated as textures become necessary
        self.blueprint = blueprint if blueprint else drawing.Blueprint()
        self.mode = InteractionMode.NORMAL  # Always start in the "normal" state of user interaction
        self.window = window  # Reference to the GTK Window containing this widget, allowing us to
                              # make calls back to its update_window function

        # Mouse pointer state tracking
        self.pointer_down_at = None
        self.pointer_state = PointerState.UP
        self.pointer_position = geometry.Coordinate2D()

        # How far we zoom with each scroll event
        self.zoom_factor = 0.05

        # We must set up special controllers to capture various pointer events
        click_controller = Gtk.GestureClick()
        click_controller.connect('pressed', self.on_button_press)
        click_controller.connect('released', self.on_button_release)
        self.add_controller(click_controller)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect('motion', self.on_motion)
        motion_controller.connect('leave', self.on_leave)
        self.add_controller(motion_controller)

        scroll_controller = Gtk.EventControllerScroll()
        scroll_controller.set_flags(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect('scroll', self.on_scroll)
        self.add_controller(scroll_controller)

        # Data structure used during click-n-drag operations, tracking the state of the motion
        self.component_grab_event = None

        # A component created when user clicks "Build" and should be placed in the blueprint next
        self.new_component = None

    def load_texture(self,
        filename: str,
        category: str,
        key: str,
    ) -> Gdk.Texture:
        '''
        Loads an image into memory and stores it under the given key in the given category.
        '''

        texture = get_texture_from_file(filename)
        if category not in self.textures.keys():
            self.textures[category] = {}
        self.textures[category][key] = texture
        return texture

    def get_texture(self,
        category: str,
        key: str
    ) -> Gdk.Texture:
        '''
        Retrieves a texture from the cache, or returns None
        '''

        if category in self.textures.keys() and key in self.textures[category]:
            return self.textures[category][key]
        return None

    def do_snapshot(self,
        snapshot: Gtk.Snapshot
    ):
        '''
        Draws the entire factory designer widget
        '''

        self.blueprint.viewport.region.size = drawing.Size2D(self.get_width(), self.get_height())
        self.blueprint.draw_frame(self, snapshot)

    def __update_selection(self,
        x: float,
        y: float,
    ):
        '''
        Given the coordinates of a pointer, changes the widget's selected component. If no widgets
        exist at that coordinate, all components are deselected. If only one component exists there,
        it is be selected. If multiple components are present, multiple calls to this function will
        cycle through those components.
        '''

        components = self.blueprint.get_components_under_coordinate(
            geometry.Coordinate2D(x, y))

        if len(components) == 0:
            self.blueprint.selected = None
            self.mode = InteractionMode.NORMAL
        elif len(components) == 1:
            self.blueprint.selected = components[0]
            self.mode = InteractionMode.EXISTING_COMPONENT_SELECTED
        elif len(components) > 1:
            if self.blueprint.selected:
                index = components.index(self.blueprint.selected)
                if index < len(components) - 1:
                    index += 1
                else:
                    index = 0
            else:
                index = 0
            self.blueprint.selected = components[index]
            self.mode = InteractionMode.EXISTING_COMPONENT_SELECTED

        if self.blueprint.selected:
            geo = self.blueprint.geometry.get(self.blueprint.selected.id)

    def on_leave(self, motion_controller):
        self.blueprint.pointer_position = None

    def on_button_press(self,
        gesture_click: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float,
    ):
        self.__update_selection(x, y)
        if self.blueprint.selected:
            self.mode = InteractionMode.EXISTING_COMPONENT_SELECTED
        else:
            self.mode = InteractionMode.NORMAL
        self.pointer_state = PointerState.DOWN
        self.pointer_down_at = geometry.Coordinate2D(x, y)
        self.queue_draw()
        self.window.update_window()

    def on_button_release(self,
        gesture_click: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float,
    ):
        if self.blueprint.selected:
            self.mode = InteractionMode.EXISTING_COMPONENT_SELECTED
        else:
            self.mode = InteractionMode.NORMAL
        self.pointer_state = PointerState.UP
        self.pointer_down_at = None
        self.component_grab_event = None
        self.queue_draw()
        self.window.unsaved_changes = True
        self.window.update_window()

    def on_motion(self,
        motion_controller: Gtk.EventControllerMotion,
        x: float,
        y: float,
    ):
        redraw = False

        self.pointer_position = geometry.Coordinate2D(x, y)

        # If the mouse is moving and we've already got a component selected and the mouse button is
        # down, then we have to move a component. Set the current grab event to start tracking it.
        if self.mode == InteractionMode.EXISTING_COMPONENT_SELECTED:
            if self.pointer_state == PointerState.DOWN \
                and self.blueprint.selected \
                and not isinstance(self.blueprint.selected, base.Conveyance):
                    geo = self.blueprint.geometry[self.blueprint.selected.id]
                    self.component_grab_event = ComponentGrabEvent(
                        self.blueprint.selected,     # The selected component
                        geo,                         # Geometry for the selected component
                        geometry.Coordinate2D(x, y)  # Pixel location of the mouse event
                    )
                    self.mode = InteractionMode.EXISTING_COMPONENT_GRABBED
                    redraw = True

        # If the mouse is moving and a component has already been grabbed, then we have to move that
        # component.
        elif self.mode == InteractionMode.EXISTING_COMPONENT_GRABBED:
            # Get the canvas location of the component
            comp_x = self.component_grab_event.geometry.canvas_location.x
            comp_y = self.component_grab_event.geometry.canvas_location.y

            # Get the location of the original mousedown event
            mousedown_x = self.component_grab_event.pointer_position.x
            mousedown_y = self.component_grab_event.pointer_position.y

            # Get the difference between the mousedown event and the current mouse position
            offset_x = x - mousedown_x
            offset_y = y - mousedown_y

            # Convert that into a difference in canvas position
            offset_x /= self.blueprint.viewport.scale
            offset_y /= self.blueprint.viewport.scale

            # Update the component's canvas_location and force recalculation of its geometry
            self.component_grab_event.geometry.canvas_location = geometry.Coordinate2D(
                comp_x + offset_x,
                comp_y + offset_y
            )
            # import pdb; pdb.set_trace()
            self.component_grab_event.geometry.calculate(
                label_height=None,
                label_width=None,
                scale=self.blueprint.viewport.scale,
                translate=self.blueprint.viewport.region.location)

            # Update the grab event's coordinates
            self.component_grab_event.pointer_position = geometry.Coordinate2D(x, y)

            # When the component moves, we have to redraw any conveyances attached to it
            for input in self.component_grab_event.component.inputs:
                if input.source:
                    if isinstance(input.source.attached_to, base.Conveyance):
                        conv_src = input.source.attached_to.inputs[0].source.attached_to
                        if conv_src:
                            conv_geo = self.blueprint.geometry[input.source.attached_to.id]
                            conv_geo.calculate(scale=self.blueprint.viewport.scale)
            for output in self.component_grab_event.component.outputs:
                if output.target:
                    if isinstance(output.target.attached_to, base.Conveyance):
                        conv_tgt = output.target.attached_to.outputs[0].target.attached_to
                        if conv_tgt:
                            conv_geo = self.blueprint.geometry[output.target.attached_to.id]
                            conv_geo.calculate(scale=self.blueprint.viewport.scale)
            redraw = True

        # If the mouse moves and the mouse button is down, but we have not grabbed a component, then
        # we must be moving the viewport.
        elif self.pointer_state == PointerState.DOWN and self.mode == InteractionMode.NORMAL:
            # Determine the distance between where the mouse is now and where the pointer was last
            # tracked. This is the distance we need to shift the viewport.
            shift_x = (x - self.pointer_down_at.x) / self.blueprint.viewport.scale
            shift_y = (y - self.pointer_down_at.y) / self.blueprint.viewport.scale
            self.blueprint.viewport.region.location = geometry.Coordinate2D(
                self.blueprint.viewport.region.left - shift_x,
                self.blueprint.viewport.region.top - shift_y
            )

            # Update the pointer position
            self.pointer_down_at = geometry.Coordinate2D(x, y)

            # Force all geometry to be recalculated, then redraw the widget
            self.blueprint.invalidate_geometry()
            redraw = True

        if redraw: self.queue_draw()

    def on_scroll(self,
        scroll_controller: Gtk.EventControllerScroll,
        x: float,
        y: float,
    ):
        '''
        Handles scroll events, which change the viewport scale.
        '''

        # When y is positive, we have a "scroll down" event, which means "zoom out" in this context
        zoom_out = True if y > 0 else False

        if zoom_out:
            zoom_factor = -self.zoom_factor
        else:
            zoom_factor = self.zoom_factor
        self.blueprint.viewport.scale += zoom_factor

        # Center the viewport
        shift_x = self.pointer_position.x * zoom_factor
        shift_y = self.pointer_position.y * zoom_factor
        self.blueprint.viewport.region.location = geometry.Coordinate2D(
            self.blueprint.viewport.region.left + shift_x,
            self.blueprint.viewport.region.top + shift_y,
        )

        # Force all geometry to be recalculated, then draw a new frame
        self.blueprint.invalidate_geometry()
        self.queue_draw()


class Taggable(object):
    '''
    Because GObject bindings for Python do not allow access to the data layer and the get/set_data()
    functions in the underlying C library, we must implement that ourselves. This class is intended
    to be used as a mixin to create arbitrarily taggable widgets.
    '''

    def __init__(self,
        tags: dict[str: str] = {}
    ):
        self.tags = tags

    def set_tag(self,
        key: str,
        value: Any,
        value_type: type
    ):
        try:
            val = value_type(value)
            self.tags[key] = value
        except:
            raise ValueError(f'Value {value} is not of type {value_type}')

    def get_tag(self,
        key: str
    ) -> Any:
        if key in self.tags.keys():
            return self.tags[key]
        else:
            raise KeyError(f'Taggable object has no such key {key}')


class TaggableButton(Gtk.Button, Taggable):
    '''
    An arbitrarily taggable GTK Button widget
    '''

    def __init__(self,
        tags: dict[str: str] = {}
    ):
        Gtk.Button.__init__(self)
        Taggable.__init__(self, tags=tags)


class TaggableEntryBuffer(Gtk.EntryBuffer, Taggable):
    '''
    An arbitrarily taggable GTK EntryBuffer
    '''

    def __init__(self,
        tags: dict[str: str] = {}
    ):
        Gtk.EntryBuffer.__init__(self)
        Taggable.__init__(self, tags=tags)


class TagBox(Gtk.Box):
    '''
    A TagGrid is a Gtk.Box containing a Gtk.Grid of controls built specifically to modify the tags
    for a component. The grid has four columns:

        - A "remove" button to delete a tag
        - A label for the tag key, which cannot be chanced once built
        - A simple label that says, "="
        - A text entry for the tag value

    Surrounding the grid are some labels for clarity and controls to add new tags.
    '''

    def __init__(self,
        component: base.Component = None,
        callback: Callable = None
    ):
        '''
        Construct the tag grid based on the tags applied to the provided component.

            - component: The component whose tags are being viewed/edited
            - callback: A function which will be called anytime a change is made to the tags. It
                accepts no arguments.

        If either of these arguments is `None`, we construct an empty instance. This allows us to
        create a "blank" object at init time which gets fixed at update time.
        '''

        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.callback = callback
        self.__component = component

        # Set up the outer box for packing
        self.set_halign(Gtk.Align.CENTER)

        self.__build()

    @property
    def component(self):
        return self.__component

    @component.setter
    def component(self, component: base.Component):
        self.__component = component
        self.repopulate()

    def __build(self):
        # Set up the top-side labels
        lblTags = Gtk.Label()
        lblTags.set_markup('<b>Tags</b>')
        lblTags.set_margin_bottom(5)
        self.append(lblTags)

        # Set up a four-column grid
        self.gridTags = Gtk.Grid()
        for i in range(4):
            self.gridTags.insert_column(0)
        self.gridTags.set_baseline_row(0)
        self.gridTags.set_row_homogeneous(True)
        self.gridTags.set_column_spacing(10)
        self.append(self.gridTags)

        # This function populates the grid with component data
        self.repopulate()

        # Set up widgets for adding a new tag. Start with a header.
        lblNewTagHeader = Gtk.Label()
        lblNewTagHeader.set_markup('<b>New Tag</b>')

        # Add a row of controls to add the new tag
        boxNewTag = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        boxNewTag.set_halign(Gtk.Align.CENTER)
        boxNewTag.set_spacing(5)
        self.entryNewTagKey = Gtk.Entry()
        lblNewTagEquals = Gtk.Label(label='=')
        self.entryNewTagValue = Gtk.Entry()
        btnNewTag = Gtk.Button()
        btnNewTag.set_icon_name('list-add')
        btnNewTag.connect('clicked', self.__btnNewTag_clicked)

        # Pack the box in a row
        boxNewTag.append(self.entryNewTagKey)
        boxNewTag.append(lblNewTagEquals)
        boxNewTag.append(self.entryNewTagValue)
        boxNewTag.append(btnNewTag)

        # Pack these elements into this widget
        self.append(lblNewTagHeader)
        self.append(boxNewTag)

    def repopulate(self):
        '''
        Call this function sometime after calling __build to force the reconstruction of all widgets
        which show component data.
        '''

        logging.debug('Repopulate called')
        # Remove all rows in the grid
        remove = 0
        while remove is not None:
            remove = self.gridTags.remove_row(0)

        if not self.component:
            return

        # Add a row for each key. We have to iterate over indices instead of typical dict iteration
        # here because the indices are needed by the base class for row counting.
        sorted_keys = sorted(self.component.tags)
        for i in range(len(sorted_keys)):
            # Extract the key and value
            key = sorted_keys[i]
            value = self.component.tags[sorted_keys[i]]

            # Create a row
            self.gridTags.insert_row(i)

            # Add the "remove" button
            btnRemoveTag = TaggableButton(tags={'tag_key': key, 'row_id': i})
            btnRemoveTag.set_icon_name('list-remove')
            btnRemoveTag.connect('clicked', self.__btnRemoveTag_clicked)

            # The labels for the key name and "=" sign. The "=" label is separate because it helps
            # line the grid up better.
            lblKey = Gtk.Label(label=key)
            lblEquals = Gtk.Label(label='=')

            # Add the value entry
            entryValue = Gtk.Entry()
            bufferValue = TaggableEntryBuffer(tags={'tag_key': key})
            bufferValue.set_text(value, -1)
            bufferValue.connect_after('deleted-text', self.__bufferValue_deleted)
            bufferValue.connect_after('inserted-text', self.__bufferValue_inserted)
            entryValue.set_buffer(bufferValue)

            # Attach all these widgets to the grid. Function accepts these args in this order:
            #     (widget, column, row, width, height)
            self.gridTags.attach(btnRemoveTag, 0, i, 1, 1)
            self.gridTags.attach(lblKey, 1, i, 1, 1)
            self.gridTags.attach(lblEquals, 2, i, 1, 1)
            self.gridTags.attach(entryValue, 3, i, 1, 1)

    def __btnNewTag_clicked(self, btn):
        key = self.entryNewTagKey.get_buffer().get_text()
        value = self.entryNewTagValue.get_buffer().get_text()
        if key == '':
            dlgError = Gtk.AlertDialog()
            dlgError.set_modal(True)
            dlgError.set_message('The tag name cannot be empty.')
            dlgError.choose(self)
            return
        if key in self.component.tags.keys():
            dlgError = Gtk.AlertDialog()
            dlgError.set_modal(True)
            dlgError.set_message(f'A tag called "{key}" already exists')
            dlgError.choose(self)
            return
        self.component.tags[key] = value
        self.entryNewTagKey.get_buffer().set_text('', -1)
        self.entryNewTagValue.get_buffer().set_text('', -1)
        self.callback()

    def __btnRemoveTag_clicked(self, btn):
        # The button is a TaggableButton containing the key of the removed tag and the row of the
        # Grid that we need to remove.
        del(self.component.tags[btn.tags['tag_key']])
        self.gridTags.remove_row(btn.tags['row_id'])
        self.callback()

    def __bufferValue_changed(self, key, value):
        self.component.tags[key] = value
        callback()

    def __bufferValue_deleted(self, buffer, position, chars):
        self.__bufferValue_changed(buffer.tags['tag_key'], buffer.get_text())

    def __bufferValue_inserted(self, buffer, position, chars, nchars):
        self.__bufferValue_changed(buffer.tags['tag_key'], buffer.get_text())
