import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject
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


def build_test_blueprint(widget: Gtk.Widget):
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
    convOreToSmelter.outputs[0].connect(smelter.inputs[0])
    storage = storages.StorageContainer(name='Iron Ore Storage')
    convIngotsToStorage = smelter.connect(storage, conveyances.ConveyorBeltMk1)

    # Add them to a blueprint with coordinates, except for Conveyances, which don't need them
    blueprint = drawing.Blueprint(widget)
    blueprint.add_component(oreSupply, geometry.Coordinate2D(0, 0))
    blueprint.add_component(convOreToSmelter, geometry.Coordinate2D())
    blueprint.add_component(smelter, geometry.Coordinate2D(170, 20))
    blueprint.add_component(convIngotsToStorage, geometry.Coordinate2D())
    blueprint.add_component(storage, geometry.Coordinate2D(320, 20))
    blueprint.factory.simulate()
    blueprint.viewport.scale = 1.0
    return blueprint


class FactoryDesignerWidget(Gtk.Widget):
    '''
    A FactoryDesginerWidget is a GTK Widget that draws a factory's components in a 2D visible space
    and allows a user to interact with those components.
    '''

    def __init__(self,
        blueprint: drawing.Blueprint = None
    ):
        super().__init__()
        self.blueprint = blueprint if blueprint else drawing.Blueprint(self)

        # Test components
        self.blueprint = build_test_blueprint(self)

    def do_snapshot(self,
        snapshot: Gtk.Snapshot
    ):
        '''
        Draws the entire factory designer widget
        '''

        self.blueprint.viewport.size = drawing.Size2D(self.get_width(), self.get_height())
        self.blueprint.draw_frame(snapshot)
