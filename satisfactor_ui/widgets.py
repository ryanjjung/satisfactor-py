import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

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
    blueprint.add_component(convOreToSmelter, geometry.Coordinate2D())
    blueprint.add_component(smelter, geometry.Coordinate2D(220, 20))
    blueprint.add_component(convIngotsToStorage, geometry.Coordinate2D())
    blueprint.add_component(storage, geometry.Coordinate2D(370, 20))
    blueprint.viewport.scale = 1.0
    return blueprint

def get_texture_from_file(filename: str) -> Gdk.Texture:
    '''
    Given the filename of an image, returns a Gdk.Texture object for it
    '''
    if Path(filename).exists():
        texture = Gdk.Texture.new_from_filename(filename)
        return texture

    return None


class FactoryDesignerWidget(Gtk.Widget):
    '''
    A FactoryDesginerWidget is a GTK Widget that draws a factory's components in a 2D visible space
    and allows a user to interact with those components.
    '''

    def __init__(self,
        blueprint: drawing.Blueprint = None
    ):
        super().__init__()
        self.textures = {}
        self.blueprint = blueprint if blueprint else drawing.Blueprint()

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
        logging.debug(f'Loaded texture: {texture}')
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
