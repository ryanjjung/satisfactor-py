'''
Contains all data required to track in-game items affecting production.
'''


import math
import random

from enum import Enum
from inspect import isfunction

WIKI_URL_BASE = 'https://satisfactory.fandom.com/wiki'


# Helper functions go here

def generate_id():
    '''
    Generates a random ID
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
    conveyance. For example, you may transport items with an Explorer, Tractor, Truck, or Factory
    Cart. These affect the rate of transfer, but all four of these are GROUND type conveyances.
    '''

    BELT          = 1
    DRONE         = 2
    GROUND        = 3
    PIPE          = 4
    POWER_LINE    = 5
    RESOURCE_NODE = 6


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
    Base object from which to build all other objects
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
        provided "strip" list. The `wiki_path` values are represented as full URLs.
        '''

        d = { key: value \
            for key, value in self.__dict__.items() \
            if not isfunction(value) }

        d['wiki_path'] = f'{WIKI_URL_BASE}{self.wiki_path}'

        for key in strip:
            if key in d:
                del(d[key])
        return d

        for key in d:
            if hasattr(d[key], 'to_dict'):
                d[key] = d[key].to_dict()

    def __repr__(self):
        return f'<{type(self).__name__} {self.id} ({self.name})>'


class Component(Base):
    '''
    Anything that can be built as part of a Factory is a Component
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Item(Base):
    '''
    An Item is something which can be held in an inventory slot or used in a Recipe or factory
    component. An item with None for a stack_size cannot be held in inventory. An item with None
    for a sink_value cannot be consumed by the Awesome Sink.
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
    This is a measure of an item, used to define Recipes. The `amount` is used when calculating
    single recipe builds. The `rate` is used when building factories.
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
    When items are combined to produce a different set of items, you have a recipe for producing
    those items. This class sets up a common interface for recipes.
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
    A special Recipe where the inputs and outputs are always identical.
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
    A Connection represents a linkage between two connectable points. It is essentially a constraint
    to ensure that we don't allow connections between incompatible parts and a way of determining
    rate changes through a factory.
    '''

    def __init__(self,
        attached_to: Base = None,
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


class Building(Component):
    '''
    A Building is anything which can be built or installed in the world which processes a Recipe of
    some kind. A Smelter is a Building, as are a Constructor, an Assembler, a Manufacturer, etc.
    Each one has a certain number of input and output connections which can be bound to the
    consumer/producer flows of a factory.
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
        Sets the ingredients of every output based on the settings for this Building.
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
        self.set_ingredients(ingredients)
    
    def set_ingredients(self,
        ingredients: list[Ingredient]
    ):
        self.recipe = ConveyanceRecipe(ingredients)
    
    def process(self):
        '''
        Ensures the recipe is set up correctly and that the outputs match the inputs.
        '''

        ingredients = list()
        for input in self.inputs:
            ingredients.extend(input.ingredients)
        self.set_ingredients(ingredients)
        return True


class Storage(Conveyance):
    '''
    Any kind of building which has storage capacity and some amount of inputs.
    '''

    def __init__(self,
        stacks: int,
        **kwargs
    ):
        super().__init__(
            **kwargs
        )
        self.stacks = stacks
