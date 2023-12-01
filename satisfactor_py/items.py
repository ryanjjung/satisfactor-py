from satisfactor_py.base import (
    ConveyanceType,
    Item
)

'''
Here are defined all of the items we care about.
'''


Power = Item(
    name='Power',
    conveyance_type=ConveyanceType.POWER_LINE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power'
)

IronOre = Item(
    name='Iron Ore',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=1,
    wiki_path='/Iron_Ore')

IronIngot = Item(
    name='Iron Ingot',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=2,
    wiki_path='/Iron_Ingot')

CopperOre = Item(
    name='Copper Ore',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=1,
    wiki_path='/Copper_Ore')
