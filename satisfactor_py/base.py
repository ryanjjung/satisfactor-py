'''
Contains all data required to track in-game items affecting production.
'''


import math
import random

from enum import Enum
from inspect import isclass, isfunction


WIKI_URL_BASE = 'https://satisfactory.fandom.com/wiki'


# Helper functions go here

def generate_id():
    '''
    Generates a random ID for the purpose of unique reference
    '''

    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    length = random.randint(12, 40)
    return ''.join([random.choice(alphabet) for i in range(0, length)])


# Enums and helper classes go here

class BuildingType(Enum):
    '''
    A constraint for Recipes, which can only be built by certain types of Buildings.
    '''

    ASSEMBLER                 = 1
    BLENDER                   = 2
    CONSTRUCTOR               = 3
    CONVEYANCE                = 4
    FOUNDRY                   = 5
    MANUFACTURER              = 6
    MINER                     = 7
    OIL_EXTRACTOR             = 8
    PACKAGER                  = 9
    PARTICLE_ACCELERATOR      = 10
    REFINERY                  = 11
    RESOURCE_WELL_PRESSURIZER = 12
    SMELTER                   = 13
    STORAGE                   = 14
    WATER_EXTRACTOR           = 15


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


class Dimension(object):
    '''
    Represents the dimensions of a rectangular prism such as that which encompasses a building.
    '''

    def __init__(self,
        width: int,
        length: int,
        height: int
    ):
        self.width = width
        self.length = length
        self.height = height

    def area(self) -> int:
        return self.width * self.length

    def volume(self) -> int:
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
        - wiki_path: The URL path where the entry for this object can be found in the online wiki
        - tags: A dictionary of arbitrary key:value pairs used as additional descriptors
    '''

    def __init__(self,
        id: str = None,
        name: str = '',
        wiki_path: str ='/',
        tags: dict[str, str] = dict(),
        **kwargs
    ):
        if not id:
            self.id = generate_id()
        else:
            self.id = id
        self.name = name
        self.wiki_path = wiki_path
        self.tags = tags

    def to_dict(self, strip: list[str] = list()):
        '''
        Return the item as a dict, stripping out all functions in the process so that the data can
        be represented as YAML. Additionally strip out any top-level keys matching those in the
        provided "strip" list. The `wiki_url` value is added as a full wiki URL.
        '''

        # Start with all attributes of this class which are not functions
        d = { key: value \
            for key, value in self.__dict__.items() \
            if not isfunction(value) }

        # Add an assembled and working URL to the object's wiki page
        d['wiki_url'] = f'{WIKI_URL_BASE}{self.wiki_path}'

        # Remove any keys matching the "strip" list (inheriting classes can "opt out" of fields
        # rather than re-implement this function)
        for key in strip:
            if key in d:
                del(d[key])

        # We refer to a lot of derived classes which may also have to_dict functions. Here we call
        # those to expand as much of these into text as possible.
        for key in d:
            if hasattr(d[key], 'to_dict'):
                d[key] = d[key].to_dict()

        # Remove any remaining unexpanded classes
        d = { key: value \
            for key, value in d.items() \
            if not isclass(value)}

        return d

    def __repr__(self):
        return f'<{type(self).__name__} {self.id} ({self.name})>'


class ComponentErrorLevel(Enum):
    '''
    Different levels of problems that can arise when testing factories.

        - DEBUG: Used only for emitting debugging information
        - WARNING: Indicates a scenario that is possible to achieve in the game but which should be
            considered misconfigured for the purposes of running a factory, such as a Building with
            no assigned recipe.
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
        message: str,
        **kwargs
    ):
        super().__init__(message, **kwargs)


class Component(Base):
    '''
    Anything that can be built as part of a Factory is a Component.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._errors = list()

    def test(self):
        '''
        In this base class, running `test` just ensures that the list of errors is cleared. Call
        this function before running downstream test functions to prevent duplicate errors.
        '''

        self.errors = list()

    def add_error(self,
        error: ComponentError
    ):
        '''
        Simple helper to ensure that errors are of the right type
        '''

        self._errors.append(error)

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self,
        value: list[ComponentError]
    ):
        self._errors = value


class Item(Base):
    '''
    An Item is something which can be held in an inventory slot, used in a Recipe, or used to build
    a factory component. An item with `None` for a `stack_size` cannot be held in inventory. An item
    with `None` for a `sink_value` cannot be consumed by the Awesome Sink.

        - conveyance_type: The mechanism by which the item can be transported automatically. Used to
            prevent, for example, a liquid material being transported on a conveyor belt.
        - stack_size: The number of this item which can be held in one inventory slot. `None` means
            it cannot be held in inventory (such as Power or Water).
        - sink_value: The number of points this item generates when destroyed in the Awesome Sink.
            `None` means it cannot be destroyed in the Awesome Sink.
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

    def to_dict(self):
        return {
            'item': self.item.to_dict(),
            'amount': self.amount,
            'rate': self.rate
        }


class Recipe(Base):
    '''
    When Items are combined to produce a different set of Items, you have a Recipe for producing
    those Items. This class sets up a common interface for Recipes.

        - building_type: The type of building that this Recipe can be built in (such as Iron Ingots
            only being craftable in Smelters).
        - consumes: A list of Ingredients that go into the Recipe
        - produces: A list of Ingredients that come out of the Recipe
    '''

    def __init__(self,
        building_type: BuildingType,
        consumes: list[Ingredient] = list(),
        produces: list[Ingredient] = list(),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.building_type = building_type
        self.consumes = consumes
        self.produces = produces


class ConveyanceRecipe(Recipe):
    '''
    A special Recipe where the inputs and outputs are always identical. This is used for Conveyances
    like conveyor belts and pipelines which cannot transform their contents and are only used to
    transport Items from one Building to another.

        - ingredients: A list of Ingredients that must be consumed and produced at identical rates.
    '''

    def __init__(self,
        ingredients: list[Ingredient] = list()
    ):
        super().__init__(building_type=BuildingType.CONVEYANCE)
        self.set_ingredients(ingredients)

    def set_ingredients(self,
        ingredients: list[Ingredient]
    ):
        self._ingredients = ingredients
        self.consumes = self._ingredients
        self.produces = self._ingredients


class Connection(Base):
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
        source=None,
        target=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.attached_to = attached_to
        self.conveyance_type = conveyance_type
        self.ingredients = ingredients
        self.source = source
        self.target = target

    def is_input(self):
        raise NotImplementedError

    def is_output(self):
        '''
        Downstream classes must implement `is_input`. This is a convenience function that simply
        negates whatever that is so downstream classes don't also have to reimplement this.
        '''

        return not self.is_input()

    def connect(self) -> bool:
        raise NotImplementedError


class Input(Connection):
    '''
    Connections must have direction, and this derived class indicates an incoming connection.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_input(self):
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


class Output(Connection):
    '''
    Connections must have direction, and this derived class indicates an outgoing connection.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_input(self):
        return False

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
        purity: Purity,
        item: Item,
        **kwargs
    ):
        super().__init__(
            wiki_path='/Resource_node',
            **kwargs
        )
        self.purity = purity
        self.item = item
        self.inputs = list()
        self.outputs = [Output(
            conveyance_type=ConveyanceType.RESOURCE_NODE,
            attached_to=self
        )]

    def test(self):
        '''
        Detects errors with this ResourceNode
        '''

        super().test()
        self.test_inputs()
        self.test_outputs()

    def test_inputs(self):
        '''
        Resource nodes cannot have inputs
        '''

        input_ct = len(self.inputs)
        if input_ct > 0:
            self.add_error(ComponentError(
                f'ResourceNodes cannot have any inputs, but this has {input_ct}.'
            ))

    def test_outputs(self):
        '''
        ResourceNodes must be connected to Miners whose Recipes match the Item the ResourceNode
        emits. They can also not have multiple outputs.
        '''

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
                if target_bldg.building_type != BuildingType.MINER:
                    self.add_error(ComponentError(
                        ComponentErrorLevel.IMPOSSIBLE,
                        'ResourceNodes must be connected to miners, but this is connected to a '
                        f'{target.building_type.name}'
                    ))
                else:
                    if target_bldg.recipe is None:
                        self.add_error(ComponentError(
                            ComponentErrorLevel.WARNING,
                            'The connected Miner has no recipe'
                        ))
                    else:
                        if self.item not in target_bldg.recipe.produces:
                            self.add_error(ComponentError(
                                ComponentErrorLevel.IMPOSSIBLE,
                                f'The connected Miner must produce {self.item.name}, but it does not.'
                            ))


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
        building_type: BuildingType,
        recipe: Recipe = None,
        clock_rate: float = 1.0,
        standby: bool = False,
        dimensions: Dimension = Dimension(0, 0, 0),
        inputs: list[Input] = list(),
        outputs: list[Output] = list(),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.building_type = building_type
        self.recipe = recipe
        self.clock_rate = clock_rate
        self.standby = standby
        self.dimensions = dimensions
        self.inputs = inputs
        self.outputs = outputs

    @property
    def ingredients(self):
        '''
        A property representing the contents of the Building's Inputs.
        '''

        ingredients = list()
        for input in self.inputs:
            ingredients.extend(input.ingredients)
        return [ingredient.item for ingredient in ingredients]

    def can_process(self) -> bool:
        '''
        Determines if the conditions are met for the recipe to be processed.
        '''

        # Can't process if there's no recipe to process
        if self.recipe is None:
            return False

        # Can't process in standby mode
        if self.standby:
            return False

        # Can't process if there aren't enough inputs to supply the recipe's ingredients (but some
        # recipes don't consume anything).
        if self.recipe.consumes and len(self.inputs) < len(self.recipe.consumes):
            return False

        # Can't process if the contents of the building's inputs don't match the recipe's
        # ingredients.
        if self.recipe.consumes:
            requirements = [ingredient.item for ingredient in self.recipe.consumes]
            for ingredient in requirements:
                if ingredient not in self.ingredients:
                    return False

        return True

    def process(self) -> bool:
        '''
        Sets the ingredients of this Building's outputs based on its settings.
        '''

        if not self.can_process():
            return False

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
        return True


class Conveyance(Building):
    '''
    A Conveyance is anything that can move Items from one Connection to another without changing
    the contents being conveyed. They are essentially Buildings with added constraints on the inputs
    and outputs.

        - conveyance_type: The kind of conveyance, preventing us from attaching, say, a Conveyor
            Belt to a Pipeline.
        - rate: The maximum rate at which the Conveyance can move Items on it.
        - ingredients: The Items being conveyed.
    '''

    def __init__(self,
        conveyance_type: ConveyanceType = ConveyanceType.BELT,
        rate: int = 0,
        ingredients: list[Ingredient] = list(),
        **kwargs
    ):
        super().__init__(
            building_type=BuildingType.CONVEYANCE,
            **kwargs
        )
        self.conveyance_type = conveyance_type
        self.rate = rate
        self.recipe = None
        self.set_ingredients(ingredients)

    def set_ingredients(self,
        ingredients: list[Ingredient]
    ):
        '''
        Special function that ensures we always load a special ConveyanceRecipe into Conveyances.
        '''

        self.recipe = ConveyanceRecipe(ingredients)

    def process(self):
        '''
        Ensures the Recipe is set up correctly and that the outputs match the inputs.
        '''

        ingredients = list()
        for input in self.inputs:
            ingredients.extend(input.ingredients)
        self.set_ingredients(ingredients)
        return True


class Storage(Conveyance):
    '''
    Any kind of building, such as Industrial Storage or a Fluid Buffer, which is essentially a
    Conveyance with added storage. Liquid storage is odd because it does not have inventory slots,
    but instead a volume of storage. Since the functionality is otherwise identical, fluids have a
    stack_size of 1 and buffers have a number of stacks equal to their volume.

        - stacks: Number of inventory slots in the storage unit
    '''

    def __init__(self,
        stacks: int,
        **kwargs
    ):
        super().__init__(
            **kwargs
        )
        self.stacks = stacks
