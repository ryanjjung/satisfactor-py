'''
Contains all data required to track in-game items affecting production.
'''

import logging
logging.basicConfig(level=logging.DEBUG)

import math
import random

from enum import Enum
from inspect import isclass, isfunction
from typing import Type
from uuid import uuid4


# The indices of this list line up with tiers. See the Milestones wiki page
# (https://satisfactory.wiki.gg/wiki/Milestones) for a complete tier list (which is zero-based).
# The values are the number of upgrade levels within each tier.
TIERS = [ 6, 3, 5, 4, 5, 4, 4, 5, 4 ]
IMAGE_URL_BASE = 'https://satisfactory.wiki.gg/images'
WIKI_URL_BASE = 'https://satisfactory.wiki.gg/wiki'


# Helper functions go here

def generate_id():
    '''
    Generates a random ID for the purpose of unique reference
    '''

    return str(uuid4())


# Enums and helper classes go here

class Availability(object):
    '''
    A combo of tier and hub upgrade depicting when the resource becomes unlocked. For resources that
    are unlocked by MAM research, set tier/upgrade to None, them set mam to True when it's unlocked.
    '''

    def __init__(self,
        tier: int,
        upgrade: int,
        mam: bool = False
    ):
        self.tier = tier
        self.upgrade = upgrade
        self.mam = mam

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        return {
            'tier': self.tier,
            'upgrade': self.upgrade
        }

    @staticmethod
    def get_tier_strings():
        '''
        Returns a list of tier numbers in stringified form; that is, "1" instead of 1. This is
        primarily used by factory_designer_gtk to populate widgets.
        '''

        return [str(i) for i in range(len(TIERS))]

    @staticmethod
    def get_upgrade_strings(tier: int):
        '''
        Returns strigified versions of upgrade levels for the given tier; that is "1" instead of 1.
        This is primarily used by factory_designer_gtk to populate widgets.
        '''

        return [str(i + 1) for i in range(TIERS[tier])]


class BuildingCategory(Enum):
    '''
    A categorization of buildings, to match the categorization in the game's build menu.
    '''

    SPECIAL      = 1
    PRODUCTION   = 2
    POWER        = 3
    LOGISTICS    = 4
    ORGANIZATION = 5
    TRANSPORT    = 6
    FOUNDATIONS  = 7
    WALLS        = 8
    ARCHITECTURE = 9


class BuildingType(Enum):
    '''
    A constraint for Recipes, which can only be built by certain types of Buildings.
    '''

    ASSEMBLER                 = 1
    AWESOME_SINK              = 2
    BIOMASS_GENERATOR         = 3
    BLENDER                   = 4
    BUILD_GUN                 = 5
    COAL_GENERATOR            = 6
    CONSTRUCTOR               = 7
    CONVEYANCE                = 8
    FOUNDRY                   = 9
    MANUFACTURER              = 10
    MINER                     = 11
    OIL_EXTRACTOR             = 12
    PACKAGER                  = 13
    PARTICLE_ACCELERATOR      = 14
    POWER_POLE                = 15
    REFINERY                  = 16
    RESOURCE_WELL_PRESSURIZER = 17
    SMELTER                   = 18
    SPACE_ELEVATOR            = 19
    STORAGE                   = 20
    WATER_EXTRACTOR           = 21
    WORKSHOP                  = 22
    OTHER                     = 23


class ConveyanceType(Enum):
    '''
    A way that two factory components can be connected. There may be different degrees of
    conveyance. For example, you may transport items with an Explorer, Tractor, Truck, Factory Cart,
    or Drone. These affect the rate of transfer, but all four of these are VEHICLE type conveyances.
    '''

    BELT          = 1
    VEHICLE       = 2
    PIPE          = 3
    POWER_LINE    = 4
    RESOURCE_NODE = 5
    AWESOME_SINK  = 6


class Dimension(object):
    '''
    Represents the dimensions of a rectangular prism such as that which encompasses a building.
    '''

    def __init__(self,
        width: float,
        length: float,
        height: float
    ):
        self.width = width
        self.length = length
        self.height = height

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        return {
            'width': self.width,
            'length': self.length,
            'height': self.height
        }

    def area(self) -> float:
        return self.width * self.length

    def volume(self) -> float:
        return self.area() * self.height


class Purity(Enum):
    '''
    The game terms for purity line up with these multipliers applied to Miner production rates.
    '''

    IMPURE = 0.5
    NORMAL = 1.0
    PURE   = 2.0


# Classes defining basic component types go here

class Base(object):
    '''
    Base object from which to build all other objects.

        - id: A unique ID used for reference; will be randomly generated if not supplied
        - name: A user-friendly name for the object
        - availability: The point at which the resource is unlocked
        - wiki_path: The URL path where the entry for this object can be found in the online wiki
        - image_path: The URL path where an image representing this item can be found in the wiki
        - tags: A dictionary of arbitrary key:value pairs used as additional descriptors
    '''

    def __init__(self,
        id: str = None,
        name: str = '',
        availability: Availability = Availability(0, 0),
        wiki_path: str = '/Satisfactory_Wiki',
        image_path: str = None,
        tags: dict[str, str] = None,
        **kwargs
    ):
        if not tags:
            tags = {}
        logging.debug(f'tags: {tags}')
        if not id:
            self.id = generate_id()
        else:
            self.id = id
        self.name = name
        self.availability = availability
        self.image_path = image_path
        self.wiki_path = wiki_path
        self.tags = tags

    @property
    def image_url(self) -> str:
        return f'{IMAGE_URL_BASE}{self.image_path}'

    def programmatic_name(self, source_str: str = None) -> str:
        if not source_str:
            source_str = self.name

        source_str = source_str.title()
        illegal_chars = ' .'
        for char in illegal_chars:
            source_str = source_str.replace(char, '')
        return source_str


    @property
    def wiki_url(self) -> str:
        return f'{WIKI_URL_BASE}{self.wiki_path}'

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        return {
            'id': self.id,
            'name': self.name,
            'availability': self.availability.to_dict(),
            'wiki_path': self.wiki_path,
            'wiki_url': self.wiki_url,
            'image_path': self.image_path,
            'image_url': self.image_url,
            'tags': self.tags
        }

    def __repr__(self):
        return f'<{type(self).__name__} "{self.name or self.id}">'


class ComponentErrorLevel(Enum):
    '''
    Different levels of problems that can arise when testing factories.

        - DEBUG: Used only for emitting debugging information
        - WARNING: Indicates a scenario that is possible to achieve in the game but which should be
            considered misconfigured for the purposes of running a factory, such as a Building with
            no assigned recipe or a detectable inefficiency.
        - IMPOSSIBLE: Indicates a scenario that is not possible to achieve in the game but which
            might be possible through the incorrect use of this library.
    '''

    DEBUG      = 0
    WARNING    = 1
    IMPOSSIBLE = 2


class ComponentError(Exception):
    '''
    Base class for any kind of error in a factory
    '''

    def __init__(self,
        level: ComponentErrorLevel,
        message: str = '',
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.level = level
        self.message = message

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        return {
            'level': self.level.name,
            'message': self.message
        }


class Component(Base):
    '''
    Anything that can be built as part of a Factory is a Component.

        - constructed: User-togglable boolean indicating whether they've built this component in an
            actual game of Satisfactory.
        - traversed: Used internally to determine if a component is actually connected to a larger
            factory.
        - blueprint_left: The location of this component's left edge in a factory blueprint
        - blueprint_top: The location of this component's top edge in a factory blueprint
    '''

    def __init__(self,
        constructed: bool = False,
        traversed: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._errors = []
        self.constructed = constructed
        self.traversed = traversed

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        base = super().to_dict()
        base.update({
            'constructed': self.constructed,
            'traversed': self.traversed,
            'errors': [error.to_dict() for error in self.errors]
        })
        return base

    # Error management functions -- These ensure that component errors are always the right type
    # and therefore meaningful to anything examining these errors later.
    def add_error(self,
        error: ComponentError
    ):
        '''
        Simple helper to ensure that errors are of the right type
        '''

        self._errors.append(error)

    @property
    def errors(self):
        '''
        Getter for component errors
        '''

        return self._errors

    @errors.setter
    def errors(self,
        value: list[ComponentError]
    ):
        '''
        Setter for the entire list of errors, should one need to set the whole list at once
        '''

        self._errors = value

    def clear_errors(self):
        '''
        Disposes of all errors
        '''

        self._errors.clear()

    def process(self):
        '''
        Most Components should clear out their errors before being processed. This is because
        Components may be traversed multiple times during a single factory traversal. The first
        traversal may bring, for example, iron rods to an Assembler fitted with a recipe for
        Reinforced Iron Plates. Without the iron plates, it can't be processed and may generate an
        error when it's first traversed. Later, a separate traversal thread may bring the iron
        plates, enabling the Assembler to process it. Errors from the first traversal are
        meaningless, and should therefore be disposed of.

        Because this is ordinarily the desired behavior, we do it here anytime an inheriting class
        calls `super().process()`.
        '''

        self.clear_errors()


class Item(Base):
    '''
    An Item is something which can be held in an inventory slot, used in a Recipe, or used to build
    a factory component. An item with `None` for a `stack_size` cannot be held in inventory. An item
    with `None` for a `sink_value` cannot be consumed by the Awesome Sink. A `None` for a
    `conveyance_type` cannot be conveyed, such as a Smelter, which is an "Item" to the extent that
    it is the product of a recipe and so must be defined as such.

        - conveyance_type: The mechanism by which the item can be transported automatically. Used to
            prevent, for example, a liquid material being transported on a conveyor belt.
        - stack_size: The number of this item which can be held in one inventory slot.
        - sink_value: The number of points this item generates when destroyed in the Awesome Sink.
    '''

    def __init__(self,
        conveyance_type: ConveyanceType = ConveyanceType.BELT,
        stack_size: int = 0,
        sink_value: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.conveyance_type = conveyance_type
        self.stack_size = stack_size
        self.sink_value = sink_value

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        base = super().to_dict()
        base.update({
            'conveyance_type': self.conveyance_type.name if self.conveyance_type else None,
            'stack_size': self.stack_size if self.stack_size else None,
            'sink_value': self.sink_value if self.sink_value else None,
            'programmatic_name()': self.programmatic_name()
        })
        return base

    def stacks(self,
        count: int
    ) -> int:
        '''
        Returns the number of inventory stacks it takes to hold the given number of this item.
        '''

        return math.ceil(count / self.stack_size)


class Ingredient(object):
    '''
    This is a measure of an Item, used to define Recipes. The `amount` is used when calculating
    single recipe builds (such as building one item at a workbench). The `rate` is the amount of the
    Item consumed per minute when the Recipe is processed in a factory.
    '''

    def __init__(self,
        item: Item,
        amount: int,
        rate: float
    ):
        self.item = item
        self.amount = amount
        self.rate = rate

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        return {
            'item': self.item.to_dict(),
            'amount': self.amount,
            'rate': self.rate
        }


class Recipe(Base):
    '''
    When Items are consumed to produce a different set of Items, you have a Recipe for those Items.
    This class sets up a common interface for Recipes.

        - building_type: The type of building that this Recipe can be built in (such as Iron Ingots
            only being craftable in Smelters, or Smelters being craftable in a build gun).
        - consumes: A list of Ingredients that go into the Recipe.
        - produces: A list of Ingredients that come out of the Recipe.
    '''

    def __init__(self,
        building_type: BuildingType,
        consumes: list[Ingredient] = [],
        produces: list[Ingredient] = [],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.building_type = building_type
        self.consumes = consumes
        self.produces = produces

    @property
    def consumed_items(self):
        '''
        Convenience function returning a list of items consumed by the recipe, regardless of their
        amount or rate.
        '''

        return [ingredient.item for ingredient in self.consumes]

    @property
    def produced_items(self):
        '''
        Convenience function returning a list of items produced by the recipe, regardless of their
        amount or rate.
        '''

        return [ingredient.item for ingredient in self.produces]

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        consumes = [ingredient.to_dict() for ingredient in self.consumes] if self.consumes else None
        produces = [ingredient.to_dict() for ingredient in self.produces] if self.produces else None
        base = super().to_dict()
        base.update({
            'building_type': self.building_type.name,
            'consumes': consumes,
            'produces': produces
        })
        return base


class ConveyanceRecipe(Recipe):
    '''
    A special Recipe where the inputs and outputs are always identical. This is used for Conveyances
    like conveyor belts and pipelines which cannot transform their contents and are only used to
    transport Items from one Building to another.

        - ingredients: A list of Ingredients that must be consumed and produced at identical rates.
    '''

    def __init__(self,
        max_rate: int,
        ingredients: list[Ingredient] = []
    ):
        super().__init__(building_type=BuildingType.CONVEYANCE)
        self.max_rate = max_rate
        self.set_ingredients(ingredients)

    def set_ingredients(self,
        ingredients: list[Ingredient]
    ):
        self._ingredients = ingredients
        self.consumes = self._ingredients
        self.produces = self._ingredients
        for ingredient in self.produces:
            ingredient.amout = None
            ingredient.rate = min(ingredient.rate, self.max_rate)


class Connection(Component):
    '''
    A Connection represents a linkage between two connectable points, such as the output of a
    Smelter and the input of a ConveyorBelt. It is essentially a constraint to ensure that we don't
    allow connections between incompatible parts and a way of determining rate changes through a
    factory.

    A Connection is not functional on its own, so you should not create an instance of this class.
    Instead, create an instance of an Input or Output, both derived from this but specialized to
    indicate direction. The properties defined here are universal to all Connections.

        - attached_to: The Component this Connection is attached to. Used for factory traversal.
        - conveyance_type: The type of conveyance this Connection represents. Used to prevent, say,
            a Pipeline from being attached to a Smelter, since the Smelter only supports Conveyor
            Belts.
        - ingredients: A list of Ingredients passing through the Connection.
        - source: The Connection on the incoming side
        - target: The Connection on the outgoing side
    '''

    def __init__(self,
        attached_to: Component = None,
        conveyance_type: ConveyanceType = ConveyanceType.BELT,
        ingredients: list[Ingredient] = list(),
        source = None,  # Type: Connection   # We cannot specify type here without creating a
        target = None,  # Type: Connection   # problem of self-dependency.
        **kwargs
    ):
        super().__init__(**kwargs)
        self.attached_to = attached_to
        self.conveyance_type = conveyance_type
        self.ingredients = ingredients
        self.source = source
        self.target = target

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        ingredients = [ingredient.to_dict() for ingredient in self.ingredients]
        base = super().to_dict()
        base.update({
            'attached_to': self.attached_to.id,
            'conveyance_type': self.conveyance_type.name if self.conveyance_type else None,
            'ingredients': ingredients,
            'source': self.source.id if self.source else None,
            'target': self.target.id if self.target else None
        })
        return base

    def disconnect(self):
        '''
        Inheriting classes must implement `disconnect` to nullify its source or target.
        '''
        raise NotImplementedError

    @property
    def remote(self):
        '''
        Inheriting classes must implement `remote` to return either the source or target, depending
        on the type of Connection.
        '''
        raise NotImplementedError

    def connected_to(self,
        skip_conveyances: bool = False
    ):
        '''
        Returns a tuple of three values: (component, connection, connection_index)

            - component: The Component this Connection is connected to.
            - connection: The Input or Output this Connection is connected to on the remote
                Component.
            - connection_index: The index of the remote Component's `inputs` or `outputs` list where
                the remote Connection can be found.

        When skip_conveyances is False, this function typically returns a Conveyance of some kind
        because that's what most components typically connect to. When True, this function will
        traverse conveyances until it finds a different kind of Component, then return that instead.
        '''

        component = None
        conn_id = None
        connection = self
        if self.remote:
            component = self.remote.attached_to
            connection = self.remote

            if skip_conveyances:
                while issubclass(component.__class__, Conveyance):
                    if self.is_output():
                        connection = component.outputs[0].remote
                    else:
                        connection = component.inputs[0].remote
                    component = connection.attached_to
        else:
            connection = None

        if component is not None:
            if self.is_input():
                conn_id = component.outputs.index(connection)
            else:
                conn_id = component.inputs.index(connection)

        return (component, connection, conn_id)

    def is_input(self) -> bool:
        '''
        Inheriting classes must implement `is_input` to return True or False, which indicates the
        direction of item flow through this Connection.
        '''

        raise NotImplementedError

    def is_output(self):
        '''
        Convenience function that simply negates the output of `is_input` so inheriting classes
        don't also have to reimplement this.
        '''

        return not self.is_input()

    def connect(self) -> bool:
        '''
        Inheriting classes must implement `connect` to ensure proper Input/Output flow.
        '''

        raise NotImplementedError

    def process(self):
        '''
        An unimplemented Connection doesn't do anything, but if an inheriting class calls this
        (`super().process()`), we should call the same function up the chain to the Component this
        Connection inherits from (which clears out component errors).
        '''

        super().process()
        if not self.attached_to:
            self.add_error(ComponentError(
                ComponentErrorLevel.IMPOSSIBLE,
                'Connection is not attached to anything'
            ))


class Input(Connection):
    '''
    Connections must have direction, and this derived class indicates an incoming connection.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def remote(self):
        return self.source

    def is_input(self) -> bool:
        '''
        Implementation of Connection.is_input
        '''

        return True

    def connect(self,
        connection: Connection
    ) -> bool:
        '''
        Connect this Input to an Output.
        '''

        # Both ends of the connection must support the same conveyance type
        if connection.conveyance_type != self.conveyance_type:
            raise TypeError(f'Connection target does not support the same conveyance type')

        # The target end must be the opposite direction of this end
        if connection.is_input():
            raise TypeError(f'Cannot connect two inputs')

        # Connect them
        self.source = connection
        connection.target = self

    def disconnect(self):
        self.source = None

    def process(self):
        '''
        Pass the incoming ingredients on to whatever this Input is attached to.
        '''

        super().process()
        # If the input is attached...
        if self.attached_to:
            # If the thing we're attached to only has one input, then we must set the ingredients
            input_ct = len(self.attached_to.inputs)
            if input_ct == 1:
                self.attached_to.ingredients = self.ingredients
            # If it has multiple inputs, then we must *append* our ingredients
            else:
                for input_ing in self.ingredients:
                    already_here = False
                    for target_ing in self.attached_to.ingredients:
                        if input_ing.item == target_ing.item:
                            already_here = True
                            target_ing.rate += input_ing.rate
                    if not already_here:
                        self.attached_to.ingredients.append(input_ing)


class Output(Connection):
    '''
    Connections must have direction, and this derived class indicates an outgoing connection.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_input(self) -> bool:
        '''
        Implementation of Component.is_input()
        '''

        return False

    @property
    def remote(self):
        return self.target

    def connect(self,
        connection: Connection
    ) -> bool:
        '''
        Connect this Output to an Input.
        '''

        # Both ends of the connection must support the same conveyance type
        if connection.conveyance_type != self.conveyance_type:
            raise TypeError(f'Connection target does not support the same conveyance type')

        # The target end must be the opposite direction of this end
        if connection.is_output():
            raise TypeError(f'Cannot connect two outputs')

        # Connect them
        self.target = connection
        connection.source = self

    def disconnect(self):
        self.target = None

    def process(self):
        '''
        Pass the incoming ingredients on to the target Input
        '''

        super().process()
        if not self.target:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                'Output is not connected to a target'
            ))
        else:
            # An output can only connect to an input, so just pass the ingredients along
            self.target.ingredients = self.ingredients


class ResourceNode(Component):
    '''
    A ResourceNode is a place in the world which will produce Items if some kind of extraction
    Building is placed on it. That Building's production rate will vary based on the purity.

        - purity: A multiplicative factor applied to the rate of production in Miners.
        - item: The type of Item that this produces. Used as a constraint to prevent, for example, a
            Miner being placed on an iron resource node and then given a Recipe to produce Copper
            Ore instead.
    '''

    def __init__(self,
        purity: Purity = Purity.NORMAL,
        wiki_path: str = '/Resource_Node',
        name: str = 'Resource Node',
        item: Item = None,
        **kwargs
    ):
        super().__init__(
            wiki_path=wiki_path,
            image_path='/8/87/Iron_Ore.png',
            name=name,
            **kwargs
        )
        self.purity = purity
        self.item = item
        self.inputs = []
        self.outputs = [Output(
            conveyance_type=ConveyanceType.RESOURCE_NODE,
            attached_to=self
        )]
        self.building_category = BuildingCategory.PRODUCTION

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        base = super().to_dict()
        base.update({
            'purity': self.purity.name,
            'item': self.item.to_dict(),
            'outputs': [output.id for output in self.outputs]
        })
        return base

    def process(self):
        '''
        A ResourceNode can't really process anything, but there are still some configuration errors
        to check for.
        '''

        super().process()

        # ResourceNodes cannot have inputs
        input_ct = len(self.inputs)
        if input_ct > 0:
            self.add_error(ComponentError(
                f'ResourceNodes cannot have any inputs, but this has {input_ct}.'
            ))

        # ResourceNodes must be connected to Miners whose Recipes match the Item the ResourceNode
        # emits. They can also not have multiple outputs.
        output_ct = len(self.outputs)
        if output_ct > 1 or output_ct < 1:
            self.add_error(ComponentError(
                ComponentErrorLevel.IMPOSSIBLE,
                f'ResourceNodes must have exactly one output, but this has {output_ct}.'
            ))
        else:
            if not self.outputs[0].target:
                self.add_error(ComponentError(
                    ComponentErrorLevel.WARNING,
                    'This ResourceNode is not connected'
                ))
            else:
                target_bldg = self.outputs[0].target.attached_to
                if target_bldg.building_type not in (BuildingType.MINER, BuildingType.WATER_EXTRACTOR):
                    self.add_error(ComponentError(
                        ComponentErrorLevel.IMPOSSIBLE,
                        'ResourceNodes must be connected to miners or water extractors, but this is connected to a '
                        f'{self.target.building_type.name}'
                    ))
                else:
                    if target_bldg.recipe is None:
                        self.add_error(ComponentError(
                            ComponentErrorLevel.WARNING,
                            'The connected Miner has no recipe'
                        ))
                    else:
                        target_production = [ ingredient.item.programmatic_name() \
                            for ingredient in target_bldg.recipe.produces ]
                        if self.item.programmatic_name() not in target_production:
                            self.add_error(ComponentError(
                                ComponentErrorLevel.IMPOSSIBLE,
                                f'The connected Miner must produce {self.item.name}, but it does not.'
                            ))


class InfiniteSupplyNode(ResourceNode):
    '''
    An InfiniteSupplyNode is a "fake" ResourceNode capable of producing an infinite amount of any
    Item in the game. This does not represent a real in-game building. Instead, it is used as a
    stand-in for other factories that might exist in the actual game but which we do not want to
    fully design in this tool.

        - item: The item this node supplies
        - rate: The rate at which the node supplies the item. If set to `None`, this will output the
            item at the fastest rate it can convey it along the connected conveyance.
    '''

    def __init__(self,
        item: Item = None,
        rate: float = None,
        conveyance_type: ConveyanceType = None,
        wiki_path: str = '/Resource_Node',
        name: str = 'Infinite Supply Node',
        **kwargs
    ):
        super().__init__(
            purity=Purity.NORMAL,
            item=item,
            wiki_path=wiki_path,
            name=name,
            **kwargs
        )
        self.rate = rate
        self.outputs = [Output(
            conveyance_type=conveyance_type,
            attached_to=self
        )]

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        base = super().to_dict()
        base.update({
            'rate': self.rate
        })
        return base

    def can_process(self) -> bool:
        '''
        Determines if the conditions required for processing are present.
        '''

        can_process = True
        if not self.item:
            self.add_error(ComponentError(
                level=ComponentErrorLevel.IMPOSSIBLE,
                message='Node doesn\'t supply an item.'
            ))
            self.can_process = False

        if not self.rate:
            self.add_error(ComponentError(
                level=ComponentErrorLevel.IMPOSSIBLE,
                message='Node has no rate set.'
            ))
            self.can_process = False

        if not self.outputs[0].target:
            self.add_error(ComponentError(
                level=ComponentErrorLevel.WARNING,
                message='Node is not connected to a conveyance.'
            ))
            self.can_process = False

        return can_process

    def process(self) -> bool:
        '''
        Set the ingredients on the output to the desired item and either the defined rate or the
        fastest rate the attached conveyance can carry it.
        '''

        self.clear_errors()

        if not self.can_process():
            return False

        rate = self.rate
        if not rate:
            if self.outputs[0].target:
                rate = self.outputs[0].target.attached_to.rate
        else:
            rate = min(rate, self.outputs[0].target.attached_to.rate)

        self.outputs[0].ingredients = [
            Ingredient(
                item=self.item,
                amount=None,
                rate=rate
            )
        ]

        return True


class Building(Component):
    '''
    A Building is anything which can be built or installed in the world which processes a Recipe of
    some kind. A Smelter is a Building, as are a Constructor, an Assembler, a Manufacturer, etc.
    Each one has a certain number of Input and Output Connections which can be bound to the
    consumer/producer flows of a factory.

        - building_type: The type of building this is, such as a Miner or Constructor. Used to
            ensure you can't load a recipe that can't be processed by this Building.
        - recipe: The recipe set to be processed
        - clock_rate: The multiplicative factor by which production is modified, as through reducing
            the production rate or overclocking it with power cells.
        - standby: Whether or not the machine is in standby mode.
        - dimensions: The three-dimensional space this Building occupies.
        - inputs: A list of Input Connections on the Building.
        - outputs: A list of Output Connections on the Building.
    '''

    def __init__(self,
        building_category: BuildingCategory,
        building_type: BuildingType,
        recipe: Recipe = None,
        overclockable: bool = True,
        clock_rate: float = 1.0,
        standby: bool = False,
        dimensions: Dimension = Dimension(0, 0, 0),
        inputs: list[Input] = list(),
        outputs: list[Output] = list(),
        power_connections: int = 1,
        base_power_usage: float = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.building_category = building_category
        self.building_type = building_type
        self.recipe = recipe
        self.clock_rate = clock_rate
        self.standby = standby
        self.dimensions = dimensions
        self.inputs = inputs
        self.outputs = outputs
        self.base_power_usage = base_power_usage
        self.ingredients = list()

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        inputs = [input.id for input in self.inputs]
        outputs = [output.id for output in self.outputs]
        base = super().to_dict()
        base.update({
            'building_type': self.building_type.name,
            'recipe': self.recipe.to_dict() if self.recipe else None,
            'clock_rate': self.clock_rate,
            'standby': self.standby,
            'dimensions': self.dimensions.to_dict(),
            'inputs': inputs,
            'outputs': outputs,
        })
        return base

    def can_process(self) -> bool:
        '''
        Determines if the conditions are met for the recipe to be processed.
        '''

        import json
        success = True
        # Can't process if there's no recipe to process
        if self.recipe is None:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                'Building has no recipe'
            ))
            success = False

        # Can't process in standby mode
        if self.standby:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                'Building is in standby mode'
            ))
            success = False

        # Make sure recipes which consume can be processed in this building
        if self.recipe and self.recipe.consumes:
            # Can't process if there aren't enough inputs to supply the recipe's ingredients
            if len(self.inputs) < len(self.recipe.consumes):
                self.add_error(ComponentError(
                    ComponentErrorLevel.IMPOSSIBLE,
                    'Building has fewer inputs than its recipe requires'
                ))
                success = False

            # Can't process if the inputs don't match the recipe
            requirements = [ingredient.item for ingredient in self.recipe.consumes]
            requirement_names = [item.name for item in requirements]
            ing_items = [ingredient.item for ingredient in self.ingredients]
            ing_names = [item.name for item in ing_items]

            for ingredient in requirements:
                if ingredient.name not in ing_names:
                    self.add_error(ComponentError(
                        ComponentErrorLevel.WARNING,
                        f'Recipe ingredient {ingredient.name} is not available'
                    ))
                    success = False

            for ingredient in ing_names:
                if ingredient not in requirement_names:
                    self.add_error(ComponentError(
                        ComponentErrorLevel.WARNING,
                        f'Ingredient {ingredient} is not required for the recipe'
                    ))

        # Some recipes don't consume; those can be processed without additional checks
        return success

    def process(self) -> bool:
        '''
        Sets the ingredients of this Building's outputs based on its settings.
        '''

        super().process()

        if not self.can_process():
            return False

        # Always clear the outputs; we don't know when this function is run whether all of the
        # building's inputs have been processed. The output should always be based on the most
        # up to date understanding of the inputs.
        for output in self.outputs:
            output.ingredients = []

        # Determine if the rates of the incoming ingredients mismatch the demand by the recipe
        if self.recipe and self.recipe.consumes:
            for recipe_ingredient in self.recipe.consumes:
                for input_ingredient in self.ingredients:
                    if recipe_ingredient.item.name == input_ingredient.item.name:
                        if input_ingredient.rate < recipe_ingredient.rate * self.clock_rate:
                            self.add_error(ComponentError(
                                ComponentErrorLevel.WARNING,
                                f'Recipe consumes {recipe_ingredient.item.name} '\
                                'faster than it is being supplied. '\
                                f'Supply rate: {input_ingredient.rate}; '\
                                f'Consumption rate: {recipe_ingredient.rate * self.clock_rate}'
                            ))
                        if input_ingredient.rate > recipe_ingredient.rate * self.clock_rate:
                            self.add_error(ComponentError(
                                ComponentErrorLevel.WARNING,
                                f'Ingredient {recipe_ingredient.item.name} is supplied '\
                                'faster than the recipe can consume it. '\
                                f'Supply rate: {input_ingredient.rate}; '\
                                f'Consumption rate: {recipe_ingredient.rate * self.clock_rate}'
                            ))

        success = True
        for recipe_ingredient in self.recipe.produces:
            for output in self.outputs:
                # If the output isn't already occupied and it has the right conveyance type, use it
                if len(output.ingredients) == 0 and output.conveyance_type == recipe_ingredient.item.conveyance_type:
                    output.ingredients = [
                        Ingredient(
                            recipe_ingredient.item,
                            None,
                            recipe_ingredient.rate * self.clock_rate
                        )
                    ]
                else:
                    success = False

        if not success:
            self.add_error(ComponentError(
                ComponentErrorLevel.IMPOSSIBLE,
                'Building doesn\'t have sufficient outputs for what its recipe produces'
            ))

        return success

    def connect(self,
        target,  # Type: Building             # Cannot use typing here because it creates a problem
        conveyance, # Type: Type[Conveyance]  # of recursive dependency.
        conveyance_name: str = None,
        connect_output: bool = True,
    ):  # Returns an implementation of a Conveyance
        '''
        Connect this Building to another by creating a Conveyance between them. Throw exceptions if
        it cannot be done. Returns the conveyance created to connect the buildings, or None if the
        connection cannot be made.

            - target: A Building to connect this Building to
            - conveyance: A class representing the type of conveyance to build between the Buildings
            - connect_output: When True, connects an output on this building to an input on the
                target. When False, connects an input on this building to an output on the target.
        '''

        # Python's type hinting can't be self-referential, so we have to test a couple things here
        if not isinstance(target, Building):
            raise TypeError
        if not issubclass(conveyance, Conveyance):
            raise TypeError

        output = None
        input = None

        connector = conveyance()

        # If we're connecting the output of this building to the input of another...
        if connect_output:
            # ...find the first available, compatible output on this building...
            for o in self.outputs:
                if not o.target and o.conveyance_type == connector.conveyance_type:
                    output = o
                    break

            # ...then find the first available, compatible input on the target building.
            for i in target.inputs:
                if not i.source and i.conveyance_type == connector.conveyance_type:
                    input = i
                    break

            if not conveyance_name:
                conveyance_name = f'"{self.name}" to "{target.name}"'

        # If we're connecting the input of this building to the output of another...
        else:
            # ...find the first available, compatible output on the target building...
            for o in target.outputs:
                if not o.target and o.conveyance_type == connector.conveyance_type:
                    output = o
                    break

            # ...then find the first available, compatible input on this building.
            for i in self.inputs:
                if not i.source and i.conveyance_type == connector.conveyance_type:
                    input = i
                    break

            if not conveyance_name:
                conveyance_name = f'{target.name}_to_{self.name}'

        # We have to have a valid input and output to attach to this conveyance; fail otherwise
        if not input or not output:
            return False

        output.connect(connector.inputs[0])
        connector.outputs[0].connect(input)
        connector.name = conveyance_name
        return connector


class NonProcessingBuilding(Building):
    '''
    This is a Building - something that can be built in the world by a build gun - but which cannot
    process recipes. It has neither inputs nor outputs, and its processing functions are disabled.
    '''

    def __init__(self,
        building_type: BuildingType = BuildingType.OTHER,
        **kwargs
    ):
        super().__init__(
            building_type=building_type,
            recipe=None,
            overclockable=False,
            inputs=[],
            outputs=[],
            **kwargs
        )

    def can_process(self) -> bool:
        return False

    def process(self) -> bool:
        return False

    def connect(self):
        return None


class Conveyance(Building):
    '''
    A Conveyance is anything that can move Items from one Connection to another without changing
    the contents being conveyed. They are essentially Buildings with added constraints on the inputs
    and outputs, and on the maximum rate of transfer.

        - conveyance_type: The kind of conveyance, preventing us from attaching, say, a Conveyor
            Belt to a Pipeline.
        - rate: The maximum rate at which the Conveyance can move Items on it.
        - ingredients: The Items being conveyed.
    '''

    def __init__(self,
        conveyance_type: ConveyanceType = ConveyanceType.BELT,
        rate: float = 0,
        **kwargs
    ):
        super().__init__(
            building_type=BuildingType.CONVEYANCE,
            building_category=BuildingCategory.LOGISTICS,
            ingredients=list(),
            **kwargs
        )
        self.conveyance_type = conveyance_type
        self.rate = rate
        self.recipe = None

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        base = super().to_dict()
        base.update({
            'conveyance_type': self.conveyance_type.name,
            'rate': self.rate
        })
        return base

    def process(self) -> bool:
        '''
        Ensures the Recipe is set up correctly and that the outputs match the inputs.
        '''

        # If the conveyance's rate is lower than the combined ingredient rates, we have to slow it
        # all down proportionately.
        total_input = sum([ingredient.rate for ingredient in self.inputs[0].ingredients])
        recipe = ConveyanceRecipe(self.rate, self.ingredients)
        total_rate = sum([product.rate for product in recipe.produces])

        if total_input > total_rate:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                f'The conveyance receives {total_input} items/min, but can only carry {self.rate}.'
            ))
            ratio = total_rate / self.rate
            for ingredient in recipe.produces:
                ingredient.rate /= ratio
        self.recipe = recipe

        self.outputs[0].ingredients = self.recipe.produces
        return True


class Storage(Building):
    '''
    Any kind of building, such as Industrial Storage or a Fluid Buffer, which is essentially a
    Conveyance with added storage. Liquid storage is odd because it does not have inventory slots,
    but instead a volume of storage. Since the functionality is otherwise identical, fluids have a
    stack_size of 1 and buffers have a number of stacks equal to their volume.

    This class inherits from Building, not from Conveyance, because, unlike a Conveyance, the rate
    of output depends on the rate of whatever the output is connected to.

        - stacks: Number of inventory slots in the storage unit
    '''

    def __init__(self,
        stacks: int,
        ingredients: list[Ingredient] = None,
        **kwargs
    ):
        super().__init__(
            building_type=BuildingType.STORAGE,
            building_category=BuildingCategory.ORGANIZATION,
            **kwargs
        )
        self.rate = None
        self.stacks = stacks
        self.ingredients = ingredients

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of this object
        '''

        base = super().to_dict()
        base.update({
            'stacks': self.stacks
        })
        return base

    def process(self):
        '''
        Processing a Storage means passing along whatever ingredients are coming in at whatever rate
        the output can handle. In an actual game, what goes out is whatever is stacked inside. We're
        not tracking the contents of the Storage, and this software doesn't track factories over
        time, so we don't do that. We just pass the rates along, which is okay for simulation and
        problem detection.
        '''

        # We can have multiple outputs, which can have different rates
        for output in self.outputs:
            if output.target and output.target.attached_to:
                ingredients = self.ingredients
                for ingredient in ingredients:
                    ingredient.rate = min(ingredient.rate, output.target.attached_to.rate)
                output.ingredients = ingredients
