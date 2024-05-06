import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

from enum import Enum
from gi.repository import Gdk, Gtk, Gio, GObject
from pathlib import Path
from satisfactor_py import (
    base,
    buildings,
    conveyances,
    items,
    recipes,
    storages
)
from satisfactor_ui import (
    drawing,
    geometry
)


def build_test_blueprint():
    '''
    Builds a simple blueprint that we can test with
    '''

    # Build and connect the factory components
    oreSupply = base.InfiniteSupplyNode(
        item=items.IronOre,
        conveyance_type=base.ConveyanceType.BELT,
        name='Infinite Iron Ore Supply',
    )
    smelter = buildings.Smelter(
        name='Iron Ore Smelter',
        recipe=recipes.IronIngot
    )
    convOreToSmelter = conveyances.ConveyorBeltMk1()
    oreSupply.outputs[0].connect(convOreToSmelter.inputs[0])
    oreSupply.constructed = True
    convOreToSmelter.outputs[0].connect(smelter.inputs[0])
    storage = storages.StorageContainer(name='Iron Ore Storage')
    convIngotsToStorage = smelter.connect(storage, conveyances.ConveyorBeltMk1)

    # Add them to a blueprint with coordinates, except for Conveyances, which don't need them
    blueprint = drawing.Blueprint()
    blueprint.factory.name = 'Test Blueprint'
    blueprint.add_component(oreSupply, geometry.Coordinate2D(50, 20))
    blueprint.add_component(smelter, geometry.Coordinate2D(225, 100))
    blueprint.add_component(convOreToSmelter, geometry.Coordinate2D())
    blueprint.add_component(storage, geometry.Coordinate2D(380, 20))
    blueprint.add_component(convIngotsToStorage, geometry.Coordinate2D())
    return blueprint

def get_texture_from_file(filename: str) -> Gdk.Texture:
    '''
    Given the filename of an image, returns a Gdk.Texture object for it
    '''
    if Path(filename).exists():
        texture = Gdk.Texture.new_from_filename(filename)
        return texture

    return None


class ComponentGrabEvent(object):
    '''
    Contains the state we need to remember in order to complete a drag-n-drop of a component.
    '''
    
    def __init__(self,
        component: base.Component,              # What component is being dragged?
        geometry: geometry.ComponentGeometry,   # What does it look like when drawn?
        pointer_offset: geometry.Coordinate2D,  # How far away is the pointer from the origin?
    ):
        self.component = component
        self.geometry = geometry
        self.origin = geometry.location         # Remember the original location
        self.pointer_offset = pointer_offset

class InteractionMode(Enum):
    '''
    Discrete set of states the widget can be in with regards to user interaction.

        - NORMAL: The "default" state of the app, as though it has just launched.
        - NEW_COMPONENT_SELECTED: A component has been selected in the building list. Next, either
            the component will be placed on the blueprint, or the action will be canceled.
        - EXISTING_COMPONENT_SELECTED: A component already placed in the blueprint has been
            selected. Details of the component have been displayed.
        - EXISTING_COMPONENT_GRABBED: A component in the blueprint has had a mouse-down event, then
            a mouse-move event without a mouse-up, indicating we want to move the component.
    '''
    
    NORMAL = 0
    NEW_COMPONENT_SELECTED = 1
    EXISTING_COMPONENT_SELECTED  = 1
    EXISTING_COMPONENT_GRABBED = 2


class PointerState(Enum):
    '''
    Represents the two states of a pointer: either up (not pressed) or down (pressed), used for
    tracking the state of things across events.
    '''

    UP   = 0
    DOWN = 1

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
        self.textures = {}
        self.blueprint = blueprint if blueprint else drawing.Blueprint()
        self.mode = InteractionMode.NORMAL
        self.pointer_state = PointerState.UP
        self.window = window

        click_controller = Gtk.GestureClick()
        click_controller.connect('pressed', self.on_button_press)
        click_controller.connect('released', self.on_button_release)
        self.add_controller(click_controller)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect('motion', self.on_motion)
        self.add_controller(motion_controller)

        self.component_grab_event = None

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
        if category not in self.textures.keys():
            self.textures[category] = {}
        self.textures[category][key] = texture
        logging.debug(f'Loaded texture: {category}/{key}')
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
        logging.debug(f'Texture cache miss for {category}/{key}')
        return None

    def do_snapshot(self,
        snapshot: Gtk.Snapshot
    ):
        '''
        Draws the entire factory designer widget
        '''

        self.blueprint.viewport.region.size = drawing.Size2D(self.get_width(), self.get_height())
        self.blueprint.viewport.scale = 1.0
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

        x += self.blueprint.viewport.region.left
        y += self.blueprint.viewport.region.top

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
    
    def on_button_press(self,
        gesture_click: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float,
    ):
        logging.debug(f'on_button_press -- n_press: {n_press}, x: {x}, y: {y}')
        self.__update_selection(x, y)
        self.pointer_state = PointerState.DOWN
        self.queue_draw()

    def on_button_release(self,
        gesture_click: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float,
    ):
        logging.debug(f'on_button_release -- n_press: {n_press}, x: {x}, y: {y}')
        if self.blueprint.selected:
            self.mode = InteractionMode.EXISTING_COMPONENT_SELECTED
        else:
            self.mode = InteractionMode.NORMAL
        self.pointer_state = PointerState.UP
        self.component_grab_event = None
        self.queue_draw()
        self.window.unsaved_changes = True
        self.window.update_window()

    def on_motion(self,
        motion_controller: Gtk.EventControllerMotion,
        x: float,
        y: float,
    ):
        if self.mode in [InteractionMode.NORMAL, InteractionMode.EXISTING_COMPONENT_SELECTED]:
            if self.pointer_state == PointerState.DOWN \
                and self.blueprint.selected \
                and not isinstance(self.blueprint.selected, base.Conveyance):
                    geo = self.blueprint.geometry[self.blueprint.selected.id]
                    self.component_grab_event = ComponentGrabEvent(
                        self.blueprint.selected,
                        geo,
                        geometry.Coordinate2D(
                            x / self.blueprint.viewport.scale - geo.location.x,
                            y / self.blueprint.viewport.scale - geo.location.y
                        )
                    )
                    self.mode = InteractionMode.EXISTING_COMPONENT_GRABBED
        
        if self.mode == InteractionMode.EXISTING_COMPONENT_GRABBED:
            self.component_grab_event.geometry.location = geometry.Coordinate2D(
                x / self.blueprint.viewport.scale - self.component_grab_event.pointer_offset.x,
                y / self.blueprint.viewport.scale - self.component_grab_event.pointer_offset.y)
            self.component_grab_event.geometry.calculate(
                label_height=None,
                label_width=None,
                scale=self.blueprint.viewport.scale)
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

            self.queue_draw()