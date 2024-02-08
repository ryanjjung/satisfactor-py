from satisfactor_py.base import (
    Availability,
    ConveyanceType,
    Item
)

'''
Here are defined all of the items we care about.
'''

# "Natural" items
# Things you find/discover in the world, which cannot be manufactured

Leaves = Item(
    name='Leaves',
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=3,
    wiki_path='Leaves'
)

Wood = Item(
    name='Wood',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=30,
    wiki_path='/Wood'
)

Biomass = Item(
    name='Biomass',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=12,
    wiki_path='/Biomass'
)

Mycelia = Item(
    name='Mycelia',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=10,
    wiki_path='/Mycelia'
)

Flower_Petals = Item(
    name='Flower Petals',
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=10,
    wiki_path='/Flower_Petals'
)

Hatcher_Remains = Item(
    name='Hatcher Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Hatcher'
)

Hog_Remains = Item(
    name='Hog Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Hog'
)

Spitter_Remains = Item(
    name='Spitter Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Spitter'
)

Stinger_Remains = Item(
    name='Stinger Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Stinger'
)


# Things made of Natural Items

Alien_Protein = Item(
    name='Alien Protein',
    availability=Availability(0, 0, True),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=None,
    wiki_path='/Alien_Protein'
)

Color_Cartridge = Item(
    name='Color Cartridge',
    availability=Availability(2, 0),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=10,
    wiki_path='/Color_Cartridge'
)


# "Core" items
# Things which are pulled up from the ground like ore, oil, and water
IronOre = Item(
    name='Iron Ore',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=1,
    wiki_path='/Iron_Ore')

CopperOre = Item(
    name='Copper Ore',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=3,
    wiki_path='/Copper_Ore')


# Smelted Items

CopperIngot = Item(
    name='Copper Ingot',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=6,
    wiki_path='/Copper_Ingot'
)

IronIngot = Item(
    name='Iron Ingot',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=2,
    wiki_path='/Iron_Ingot')


# Constructed Items

Cable = Item(
    name='Cable',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=24,
    wiki_path='/Cable'
)

Concrete = Item(
    name='Concrete',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=12,
    wiki_path='/Concrete'
)

IronPlate = Item(
    name='Iron Plate',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=6,
    wiki_path='Iron_Plate')

IronRod = Item(
    name='Iron Rod',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=4,
    wiki_path='/Iron_Rod'
)

Limestone = Item(
    name='Limestone',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=2,
    wiki_path='/Limestone'
)

Screw = Item(
    name='Screw',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=2,
    wiki_path='/Screw'
)

Wire = Item(
    name='Wire',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=6,
    wiki_path='/Wire'
)


# Assembled Items

PortableMiner = Item(
    name='Portable Miner',
    availability=Availability(0, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=1,
    sink_value=60,
    wiki_path='/Miner#Portable_Miner'
)

ReinforcedIronPlate = Item(
    name='Reinforced Iron Plate',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=120,
    wiki_path='/Reinforced_Iron_Plate'
)

# Built Items

BiomassBurner = Item(
    name='Biomass Burner',
    availability=Availability(0, 6),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Biomass_Burner'
)

Constructor = Item(
    name='Constructor',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Constructor'
)

ConveyorBeltMk1 = Item(
    name='Conveyor Belt Mk.1',
    availability=Availability(0, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Belt#Mk.1'
)

ConveyorPole = Item(
    name='Conveyor Pole',
    availability=Availability(0, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Poles#Simple'
)

CraftBench = Item(
    name='Craft Bench',
    conveyance_type=None,
    stack_size=0,
    sink_value=0,
    wiki_path='/Craft_Bench'
)

DoubleWallOutletMk1 = Item(
    name='Double Wall Outlet Mk.1',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Pole#Double_Wall_Outlets'
)

EquipmentWorkshop = Item(
    name='Equipment Workshop',
    availability=Availability(0, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Equipment_Workshop'
)

MinerMk1 = Item(
    name='Miner Mk. 1',
    availability=Availability(0, 1),
    conveyance_type=None,
    stack_size=0,
    sink_value=0,
    wiki_path='/Miner#Mk.1'
)

PowerLine = Item(
    name='Power Line',
    availability=Availability(0, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Line'
)

PowerPoleMk1 = Item(
    name='Power Pole Mk.1',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Pole#Ground_Poles'
)

Smelter = Item(
    name='Smelter',
    availability=Availability(0, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Smelter'
)

SpaceElevator = Item(
    name='Space Elevator',
    availability=Availability(0, 6),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Space_Elevator'
)

StorageContainer = Item(
    name='Storage Container',
    availability=Availability(0, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Storage_Container'
)

WallOutletMk1 = Item(
    name='Wall Outlet Mk.1',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Pole#Wall_Outlets'
)


# Power Items

Power = Item(
    name='Power',
    conveyance_type=ConveyanceType.POWER_LINE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power'
)
