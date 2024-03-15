from satisfactor_py.base import (
    Availability,
    ConveyanceType,
    Item
)

'''
Here are defined all of the items we care about.
'''


AlienProtein = Item(
    name='Alien Protein',
    availability=Availability(0, 0, True),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=None,
    wiki_path='/Alien_Protein'
)

Assembler = Item(
    name='Assembler',
    availability=Availability(2, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Assembler'
)

AwesomeSink = Item(
    name='AWESOME Sink',
    availability=Availability(2, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/AWESOME_Sink'
)

AwesomeSinkPoint = Item(
    name='AWESOME Sink Point',
    availability=Availability(2, 4),
    conveyance_type=ConveyanceType.AWESOME_SINK,
    stack_size=None,
    sink_value=None,
    wiki_path='/AWESOME_Sink'
)

Biomass = Item(
    name='Biomass',
    availability=Availability(0, 6),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=12,
    wiki_path='/Biomass'
)

BiomassBurner = Item(
    name='Biomass Burner',
    availability=Availability(0, 6),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Biomass_Burner'
)

BasicWall1mFicsit = Item(
    name='Basic Wall 1m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Walls'
)

BasicWall4mFicsit = Item(
    name='Basic Wall 4m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Walls'
)

Beacon = Item(
    name='Beacon',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Beacon'
)

Cable = Item(
    name='Cable',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=24,
    wiki_path='/Cable'
)

Chainsaw = Item(
    name='Chainsaw',
    availability=Availability(2, 2),
    conveyance_type=None,
    stack_size=1,
    sink_value=2760,
    wiki_path='/Copper_Sheet'
)

Coal = Item(
    name='Coal',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=100,
    sink_value=3,
    wiki_path='/Coal'
)

CoalGenerator = Item(
    name='Coal Generator',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Coal_Generator'
)

CompactedCoal = Item(
    name='Compacted Coal',
    availability=Availability(3, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=28,
    wiki_path='/Compacted_Coal'
)

Concrete = Item(
    name='Concrete',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=12,
    wiki_path='/Concrete'
)

CopperOre = Item(
    name='Copper Ore',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=3,
    wiki_path='/Copper_Ore'
)

ColorCartridge = Item(
    name='Color Cartridge',
    availability=Availability(2, 4),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=10,
    wiki_path='/Color_Cartridge'
)

CopperIngot = Item(
    name='Copper Ingot',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=6,
    wiki_path='/Copper_Ingot'
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

ConveyorBeltMk2 = Item(
    name='Conveyor Belt Mk.2',
    availability=Availability(2, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Belt#Mk.2'
)

ConveyorLiftMk1 = Item(
    name='Conveyor Lift Mk.1',
    availability=Availability(1, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Lift'
)

ConveyorLiftMk2 = Item(
    name='Conveyor Lift Mk.2',
    availability=Availability(2, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Lift#Mk.2'
)

ConveyorMerger = Item(
    name='Conveyor Merger',
    availability=Availability(1, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Merger'
)

ConveyorPole = Item(
    name='Conveyor Pole',
    availability=Availability(0, 4),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Poles#Simple'
)

ConveyorSplitter = Item(
    name='Conveyor Splitter',
    availability=Availability(1, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Splitter'
)

CopperSheet = Item(
    name='Copper Sheet',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=24,
    wiki_path='/Copper_Sheet'
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

FlowerPetals = Item(
    name='Flower Petals',
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=10,
    wiki_path='/Flower_Petals'
)

FluidBuffer = Item(
    name='Fluid Buffer',
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Fluid_Buffer#Normal-0'
)

Foundation1mFicsit = Item(
    name='Foundation 1m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations'
)

Foundation2mFicsit = Item(
    name='Foundation 2m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations'
)

Foundation4mFicsit = Item(
    name='Foundation 4m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations'
)

Foundry = Item(
    name='Foundry',
    availability=Availability(3, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundry'
)

HatcherRemains = Item(
    name='Hatcher Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Hatcher'
)

HeavyOilResidue = Item(
    name='Heavy Oil Residue',
    availability=Availability(5, 1),
    conveyance_type=ConveyanceType.PIPE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Heavy_Oil_Residue'
)

HogRemains = Item(
    name='Hog Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Hog'
)

IronIngot = Item(
    name='Iron Ingot',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=2,
    wiki_path='/Iron_Ingot'
)

IronOre = Item(
    name='Iron Ore',
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=1,
    wiki_path='/Iron_Ore'
)

IronPlate = Item(
    name='Iron Plate',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=6,
    wiki_path='Iron_Plate'
)

IronRod = Item(
    name='Iron Rod',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=4,
    wiki_path='/Iron_Rod'
)

JumpPad = Item(
    name='Jump Pad',
    availability=Availability(2, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Jump_Pad'
)

Leaves = Item(
    name='Leaves',
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=3,
    wiki_path='Leaves'
)

Limestone = Item(
    name='Limestone',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=2,
    wiki_path='/Limestone'
)

LookoutTower = Item(
    name='Lookout Tower',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='Lookout_Tower'
)

MAM = Item(
    name='MAM',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/MAM'
)

MinerMk1 = Item(
    name='Miner Mk. 1',
    availability=Availability(0, 1),
    conveyance_type=None,
    stack_size=0,
    sink_value=0,
    wiki_path='/Miner#Mk.1'
)

ModularFrame = Item(
    name='Modular Frame',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=408,
    wiki_path='/Modular_Frame'
)

Mycelia = Item(
    name='Mycelia',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=10,
    wiki_path='/Mycelia'
)

ObjectScanner = Item(
    name='Object Scanner',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Object_Scanner'
)

PersonalStorageBox = Item(
    name='Personal Storage Box',
    availability=Availability(1, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Personal_Storage_Box'
)

PetroleumCoke = Item(
    name='Petroleum Coke',
    availability=Availability(5, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=20,
    wiki_path='/Petroleum_Coke'
)

PipelineMk1 = Item(
    name='Pipeline Mk.1',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipelines#Mk.1-0'
)

PipelineJunctionCross = Item(
    name='Pipeline Junction Cross',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipeline_Junction_Cross'
)

PipelinePump = Item(
    name='Pipeline Pump',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipeline_Pump'
)

PipelineSupport = Item(
    name='Pipeline Support',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Pipeline_Supports#Simple-0'
)

PortableMiner = Item(
    name='Portable Miner',
    availability=Availability(0, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=1,
    sink_value=60,
    wiki_path='/Miner#Portable_Miner'
)

Power = Item(
    name='Power',
    conveyance_type=ConveyanceType.POWER_LINE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power'
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

Ramp1mFicsit = Item(
    name='Ramp 1m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations#Ramps'
)

Ramp2mFicsit = Item(
    name='Ramp 2m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations#Ramps'
)

Ramp4mFicsit = Item(
    name='Ramp 4m (FICSIT)',
    availability=Availability(1, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Foundations#Ramps'
)

ReinforcedIronPlate = Item(
    name='Reinforced Iron Plate',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=120,
    wiki_path='/Reinforced_Iron_Plate'
)

Rotor = Item(
    name='Rotor',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=140,
    wiki_path='/Rotor'
)

Screw = Item(
    name='Screw',
    availability=Availability(0, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=2,
    wiki_path='/Screw'
)

SmartPlating = Item(
    name='Smart Plating',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=520,
    wiki_path='/Smart_Plating'
)

Smelter = Item(
    name='Smelter',
    availability=Availability(0, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Smelter'
)

SolidBiofuel = Item(
    name='Solid Biofuel',
    availability=Availability(2, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=48,
    wiki_path='/Solit_Biofuel'
)

SpaceElevator = Item(
    name='Space Elevator',
    availability=Availability(0, 6),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Space_Elevator'
)

SpitterRemains = Item(
    name='Spitter Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Spitter'
)

StackableConveyorPole = Item(
    name='StackableConveyor Pole',
    availability=Availability(2, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Conveyor_Poles#Stackable'
)

SteelBeam = Item(
    name='Steel Beam',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=64,
    wiki_path='/Steel_Beam'
)

SteelIngot = Item(
    name='Steel Ingot',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=8,
    wiki_path='/Steel_Ingot'
)

SteelPipe = Item(
    name='Steel Pipe',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=24,
    wiki_path='/Steel_Pipe'
)

StingerRemains = Item(
    name='Stinger Remains',
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=None,
    wiki_path='/Alien_Remains#Stinger'
)

StorageContainer = Item(
    name='Storage Container',
    availability=Availability(0, 5),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Storage_Container'
)

Sulfur = Item(
    name='Sulfur',
    availability=Availability(0, 1),
    conveyance_type=ConveyanceType.BELT,
    stack_size=100,
    sink_value=11,
    wiki_path='/Sulfur'
)

Tractor = Item(
    name='Tractor',
    availability=Availability(3, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Tractor'
)

TruckStation = Item(
    name='Truck Station',
    availability=Availability(3, 2),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Truck_Station'
)

UJellyLandingPad = Item(
    name='U-Jelly Landing Pad',
    availability=Availability(2, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/U-Jelly_Landing_Pad'
)

VersatileFramework = Item(
    name='Versatile Framework',
    availability=Availability(3, 3),
    conveyance_type=ConveyanceType.BELT,
    stack_size=50,
    sink_value=1176,
    wiki_path='/Versatile_Framework'
)

WallOutletMk1 = Item(
    name='Wall Outlet Mk.1',
    availability=Availability(0, 3),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Pole#Wall_Outlets'
)

Water = Item(
    name='Water',
    availability=Availability(3, 1),
    conveyance_type=ConveyanceType.PIPE,
    stack_size=None,
    sink_value=None,
    wiki_path='/Power_Pole#Wall_Outlets'
)

WaterExtractor = Item(
    name='Water Extractor',
    availability=Availability(3, 1),
    conveyance_type=None,
    stack_size=None,
    sink_value=None,
    wiki_path='/Water_Extractor'
)

Wire = Item(
    name='Wire',
    availability=Availability(0, 2),
    conveyance_type=ConveyanceType.BELT,
    stack_size=500,
    sink_value=6,
    wiki_path='/Wire'
)

Wood = Item(
    name='Wood',
    conveyance_type=ConveyanceType.BELT,
    stack_size=200,
    sink_value=30,
    wiki_path='/Wood'
)

XenoBasher = Item(
    name='Xeno-Basher',
    availability=Availability(3, 4),
    conveyance_type=None,
    stack_size=1,
    sink_value=18800,
    wiki_path='/Xeno-Basher'
)

XenoZapper = Item(
    name='Xeno-Zapper',
    conveyance_type=None,
    stack_size=1,
    sink_value=1880,
    wiki_path='/Xeno-Zapper'
)
