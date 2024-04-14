from satisfactor_py.base import (
    Availability,
    ConveyanceType,
    Item
)

'''
Here are defined all of the items we care about.
'''

ALL = None

def get_all():
    '''
    Returns a list of all Items defined in this module; caches the results for quick access.
    '''

    global ALL
    if ALL is None:
        import inspect
        import sys
        ALL = [ mbr for mbr in inspect.getmembers(sys.modules[__name__])
            if isinstance(mbr[1], Item) ]
    return ALL




AlienProtein = Item(
    name='Alien Protein',
    availability=Availability(0, 0, True),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=None,
    wiki_path='/Alien_Protein',
    image_path='/6/6f/Alien_Protein.png',
)

Assembler = Item(
    name='Assembler',
    availability=Availability(2, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Assembler',
    image_path='/a/ae/Assembler.png',
)

AwesomeShop = Item(
    name='AWESOME Shop',
    availability=Availability(2, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/AWESOME_Shop',
    image_path='/b/b1/AWESOME_Shop.png'
)

AwesomeSink = Item(
    name='AWESOME Sink',
    availability=Availability(2, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/AWESOME_Sink',
    image_path='/8/85/AWESOME_Sink.png',
)

AwesomeSinkPoint = Item(
    name='AWESOME Sink Point',
    availability=Availability(2, 4),
    conveyance_type=ConveyanceType.AWESOME_SINK,
    stack_size=None,
    sink_value=None,
    wiki_path='/AWESOME_Sink',
    image_path='/c/c3/Satisfactory_logo_full_color_square.png',
)

BasicWall1mFicsit = Item(
    name='Basic Wall 1m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Walls',
    image_path='/3/32/Basic_Wall_4m_(FICSIT).png', # Can't find image of 1m wall
)

BasicWall4mFicsit = Item(
    name='Basic Wall 4m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Walls',
    image_path='/3/32/Basic_Wall_4m_(FICSIT).png',
)

Beacon = Item(
    name='Beacon',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Beacon',
    image_path='/b/b3/Beacon.png',
)

Biomass = Item(
    name='Biomass',
    availability=Availability(0, 6),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=12,
    wiki_path='/Biomass',
    image_path='/f/f0/Biomass.png',
)

BiomassBurner = Item(
    name='Biomass Burner',
    availability=Availability(0, 6),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Biomass_Burner',
    image_path='/2/20/Biomass_Burner.png',
)

Cable = Item(
    name='Cable',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=24,
    wiki_path='/Cable',
    image_path='/4/49/Cable.png',
)

Chainsaw = Item(
    name='Chainsaw',
    availability=Availability(2, 2),
    conveyance_type=None,
    stack_size=1,
    sink_value=2760,
    wiki_path='/Chainsaw',
    image_path='/c/cc/Chainsaw.png',
)

Coal = Item(
    name='Coal',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=100,
    sink_value=3,
    wiki_path='/Coal',
    image_path='/a/a7/Coal.png',
)

CoalGenerator = Item(
    name='Coal Generator',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Coal_Generator',
    image_path='/b/ba/Coal_Generator.png',
)

CompactedCoal = Item(
    name='Compacted Coal',
    availability=Availability(3, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=28,
    wiki_path='/Compacted_Coal',
    image_path='/5/52/Compacted_Coal.png',
)

Concrete = Item(
    name='Concrete',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=12,
    wiki_path='/Concrete',
    image_path='/c/c3/Concrete.png',
)

ColorCartridge = Item(
    name='Color Cartridge',
    availability=Availability(2, 4),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=10,
    wiki_path='/Color_Cartridge',
    image_path='/3/38/Color_Cartridge.png',
)

Constructor = Item(
    name='Constructor',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Constructor',
    image_path='/6/61/Constructor.png',
)

ConveyorBeltMk1 = Item(
    name='Conveyor Belt Mk.1',
    availability=Availability(0, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Belt#Mk.1-0',
    image_path='/c/c9/Conveyor_Belt_Mk.1.png',
)

ConveyorBeltMk2 = Item(
    name='Conveyor Belt Mk.2',
    availability=Availability(2, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Belt#Mk.2-0',
    image_path='/e/e9/Conveyor_Belt_Mk.2.png',
)

ConveyorLiftMk1 = Item(
    name='Conveyor Lift Mk.1',
    availability=Availability(1, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Lift#Mk.1-0',
    image_path='/2/2d/Conveyor_Lift_Mk.1.png',
)

ConveyorLiftMk2 = Item(
    name='Conveyor Lift Mk.2',
    availability=Availability(2, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Lift#Mk.2-0',
    image_path='/8/8a/Conveyor_Lift_Mk.2.png',
)

ConveyorMerger = Item(
    name='Conveyor Merger',
    availability=Availability(1, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Merger',
    image_path='/a/aa/Conveyor_Merger.png',
)

ConveyorPole = Item(
    name='Conveyor Pole',
    availability=Availability(0, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Poles#Simple-0',
    image_path='/7/73/Conveyor_Pole.png',
)

ConveyorSplitter = Item(
    name='Conveyor Splitter',
    availability=Availability(1, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Splitter',
    image_path='/4/41/Conveyor_Splitter.png',
)

CopperIngot = Item(
    name='Copper Ingot',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=6,
    wiki_path='/Copper_Ingot',
    image_path='/0/00/Copper_Ingot.png',
)

CopperOre = Item(
    name='Copper Ore',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=3,
    wiki_path='/Copper_Ore',
    image_path='/7/78/Copper_Ore.png',
)

CopperSheet = Item(
    name='Copper Sheet',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=24,
    wiki_path='/Copper_Sheet',
    image_path='/e/e1/Copper_Sheet.png',
)

CraftBench = Item(
    name='Craft Bench',
    conveyance_type=None,
    stack_size=0,
    sink_value=0,
    wiki_path='/Craft_Bench',
    image_path='/7/75/Craft_Bench.png',
)

DoubleWallOutletMk1 = Item(
    name='Double Wall Outlet Mk.1',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Wall_Outlets#Double_Wall_Outlets-0',
    image_path='/2/21/Double_Wall_Outlet_Mk.1.png'
)

EquipmentWorkshop = Item(
    name='Equipment Workshop',
    availability=Availability(0, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Equipment_Workshop',
    image_path='/d/d9/Equipment_Workshop.png'
)

FlowerPetals = Item(
    name='Flower Petals',
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=10,
    wiki_path='/Flower_Petals',
    image_path='/8/83/Flower_Petals.png'
)

FluidBuffer = Item(
    name='Fluid Buffer',
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Fluid_Buffer#Normal-0',
    image_path='/5/53/Fluid_Buffer.png'
)

Foundation1mFicsit = Item(
    name='Foundation 1m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations',
    image_path='/0/00/Foundation_4m_(FICSIT).png'
)

Foundation2mFicsit = Item(
    name='Foundation 2m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations',
    image_path='/0/00/Foundation_4m_(FICSIT).png'
)

Foundation4mFicsit = Item(
    name='Foundation 4m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations',
    image_path='/0/00/Foundation_4m_(FICSIT).png'
)

Foundry = Item(
    name='Foundry',
    availability=Availability(3, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundry',
    image_path='/1/19/Foundry.png'
)

HatcherRemains = Item(
    name='Hatcher Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Hatcher-0',
    image_path='/4/4d/Hatcher_Remains.png'
)

HeavyOilResidue = Item(
    name='Heavy Oil Residue',
    availability=Availability(5, 1),
    conveyance_type=ConveyanceType.PIPE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Heavy_Oil_Residue',
    image_path='/b/bd/Heavy_Oil_Residue.png'
)

HogRemains = Item(
    name='Hog Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Hog-0',
    image_path='/e/e0/Hog_Remains.png'
)

IronIngot = Item(
    name='Iron Ingot',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=2,
    wiki_path='/Iron_Ingot',
    image_path='/0/0a/Iron_Ingot.png'
)

IronOre = Item(
    name='Iron Ore',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=1,
    wiki_path='/Iron_Ore',
    image_path='/8/87/Iron_Ore.png'
)

IronPlate = Item(
    name='Iron Plate',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=6,
    wiki_path='/Iron_Plate',
    image_path='/5/51/Iron_Plate.png'
)

IronRod = Item(
    name='Iron Rod',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=4,
    wiki_path='/Iron_Rod',
    image_path='/5/5f/Iron_Rod.png'
)

JumpPad = Item(
    name='Jump Pad',
    availability=Availability(2, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Jump_Pad',
    image_path='/4/4c/Jump_Pad.png',
)

Leaves = Item(
    name='Leaves',
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=3,
    wiki_path='/Leaves',
    image_path='/f/f1/Leaves.png',
)

Limestone = Item(
    name='Limestone',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=2,
    wiki_path='/Limestone',
    image_path='/4/4e/Limestone.png',
)

LookoutTower = Item(
    name='Lookout Tower',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Lookout_Tower',
    image_path='/c/cc/Lookout_Tower.png',
)

MAM = Item(
    name='MAM',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/MAM',
    image_path='/b/b4/MAM.png',
)

MinerMk1 = Item(
    name='Miner Mk. 1',
    availability=Availability(0, 1),
    conveyance_type=None,
    stack_size=0,
    sink_value=0,
    wiki_path='/Miner#Mk.1-0',
    image_path='/c/cf/Miner_Mk.1.png',
)

ModularFrame = Item(
    name='Modular Frame',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=408,
    wiki_path='/Modular_Frame',
    image_path='/8/81/Modular_Frame.png',
)

Mycelia = Item(
    name='Mycelia',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=10,
    wiki_path='/Mycelia',
    image_path='/e/e0/Mycelia.png',
)

ObjectScanner = Item(
    name='Object Scanner',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Object_Scanner',
    image_path='/2/2a/Object_Scanner.png',
)

PersonalStorageBox = Item(
    name='Personal Storage Box',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Personal_Storage_Box#Personal-0',
    image_path='/4/4d/Personal_Storage_Box.png',
)

PetroleumCoke = Item(
    name='Petroleum Coke',
    availability=Availability(5, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=20,
    wiki_path='/Petroleum_Coke',
    image_path='/5/5c/Petroleum_Coke.png',
)

PipelineJunctionCross = Item(
    name='Pipeline Junction Cross',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipeline_Junction_Cross',
    image_path='/8/8c/Pipeline_Junction_Cross.png',
)

PipelineMk1 = Item(
    name='Pipeline Mk.1',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipelines#Mk.1-0',
    image_path='/5/54/Pipeline_Mk.1.png',
)

PipelinePump = Item(
    name='Pipeline Pump',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipeline_Pump',
    image_path='/2/2d/Pipeline_Pump_Mk.1.png',
)

PipelineSupport = Item(
    name='Pipeline Support',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipeline_Supports#Simple-0',
    image_path='/c/c5/Pipeline_Support.png',
)

PortableMiner = Item(
    name='Portable Miner',
    availability=Availability(0, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=1,
    sink_value=60,
    wiki_path='/Miner#Portable_Miner',
    image_path='/b/b3/Portable_Miner.png',
)

Power = Item(
    name='Power',
    conveyance_type=ConveyanceType.POWER_LINE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power',
    image_path='/c/c3/Satisfactory_logo_full_color_square.png',
)

PowerLine = Item(
    name='Power Line',
    availability=Availability(0, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Line',
    image_path='/0/09/Power_Line.png',
)

PowerPoleMk1 = Item(
    name='Power Pole Mk.1',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Poles#Mk.1-0',
    image_path='/a/af/Power_Pole_Mk.1.png',
)

Ramp1mFicsit = Item(
    name='Ramp 1m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations',
    image_path='/3/33/Ramp_4m_(FICSIT).png',
)

Ramp2mFicsit = Item(
    name='Ramp 2m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations',
    image_path='/3/33/Ramp_4m_(FICSIT).png',
)

Ramp4mFicsit = Item(
    name='Ramp 4m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations',
    image_path='/3/33/Ramp_4m_(FICSIT).png',
)

ReinforcedIronPlate = Item(
    name='Reinforced Iron Plate',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=120,
    wiki_path='/Reinforced_Iron_Plate',
    image_path='/2/29/Reinforced_Iron_Plate.png',
)

Rotor = Item(
    name='Rotor',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=140,
    wiki_path='/Rotor',
    image_path='/3/3d/Rotor.png',
)

Screw = Item(
    name='Screw',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=2,
    wiki_path='/Screw',
    image_path='/5/59/Screw.png',
)

SmartPlating = Item(
    name='Smart Plating',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=520,
    wiki_path='/Smart_Plating',
    image_path='/d/d5/Smart_Plating.png',
)

Smelter = Item(
    name='Smelter',
    availability=Availability(0, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Smelter',
    image_path='/4/45/Smelter.png',
)

SolidBiofuel = Item(
    name='Solid Biofuel',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=48,
    wiki_path='/Solid_Biofuel',
    image_path='/b/bb/Solid_Biofuel.png',
)

SpaceElevator = Item(
    name='Space Elevator',
    availability=Availability(0, 6),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Space_Elevator',
    image_path='/a/a4/Space_Elevator.png',
)

SpitterRemains = Item(
    name='Spitter Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Spitter-0',
    image_path='/5/5a/Plasma_Spitter_Remains.png',
)

StackableConveyorPole = Item(
    name='StackableConveyor Pole',
    availability=Availability(2, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Poles#Stackable-0',
    image_path='/4/49/Stackable_Conveyor_Pole.png',
)

SteelBeam = Item(
    name='Steel Beam',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=64,
    wiki_path='/Steel_Beam',
    image_path='/6/6f/Steel_Beam.png',
)

SteelIngot = Item(
    name='Steel Ingot',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=8,
    wiki_path='/Steel_Ingot',
    image_path='/b/bd/Steel_Ingot.png',
)

SteelPipe = Item(
    name='Steel Pipe',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=24,
    wiki_path='/Steel_Pipe',
    image_path='/a/aa/Steel_Pipe.png',
)

StingerRemains = Item(
    name='Stinger Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Stinger-0',
    image_path='/f/fb/Stinger_Remains.png',
)

StorageContainer = Item(
    name='Storage Container',
    availability=Availability(0, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Storage_Container',
    image_path='/2/20/Storage_Container.png',
)

Sulfur = Item(
    name='Sulfur',
    availability=Availability(0, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=11,
    wiki_path='/Sulfur',
    image_path='/1/1d/Sulfur.png',
)

Tractor = Item(
    name='Tractor',
    availability=Availability(3, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Tractor',
    image_path='/7/7a/Tractor.png',
)

TruckStation = Item(
    name='Truck Station',
    availability=Availability(3, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Truck_Station',
    image_path='/a/a6/Truck_Station.png',
)

UJellyLandingPad = Item(
    name='U-Jelly Landing Pad',
    availability=Availability(2, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/U-Jelly_Landing_Pad',
    image_path='/d/de/U-Jelly_Landing_Pad.png',
)

VersatileFramework = Item(
    name='Versatile Framework',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=1176,
    wiki_path='/Versatile_Framework',
    image_path='/7/74/Versatile_Framework.png',
)

WallOutletMk1 = Item(
    name='Wall Outlet Mk.1',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Wall_Outlets',
    image_path='/8/82/Wall_Outlet_Mk.1.png',
)

Water = Item(
    name='Water',
    availability=Availability(3, 1),
    conveyance_type=ConveyanceType.PIPE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Water',
    image_path='/9/9d/Water.png',
)

WaterExtractor = Item(
    name='Water Extractor',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Water_Extractor',
    image_path='/6/6b/Water_Extractor.png',
)

Wire = Item(
    name='Wire',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=6,
    wiki_path='/Wire',
    image_path='/7/77/Wire.png',
)

Wood = Item(
    name='Wood',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=30,
    wiki_path='/Wood',
    image_path='/d/df/Wood.png',
)

XenoBasher = Item(
    name='Xeno-Basher',
    availability=Availability(3, 4),
    conveyance_type=None,
    stack_size=1,
    sink_value=18800,
    wiki_path='/Xeno-Basher',
    image_path='/8/83/Xeno-Basher.png',
)

XenoZapper = Item(
    name='Xeno-Zapper',
    conveyance_type=None,
    stack_size=1,
    sink_value=1880,
    wiki_path='/Xeno-Zapper',
    image_path='/5/5d/Xeno-Zapper.png',
)
