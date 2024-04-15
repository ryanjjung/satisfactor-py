from satisfactor_py.base import (
    Availability,
    BuildingType,
    Ingredient,
    Recipe
)
from satisfactor_py.items import (
    AlienProtein as iAlienProtein,
    Assembler as iAssembler,
    AwesomeShop as iAwesomeShop,
    AwesomeSink as iAwesomeSink,
    BasicWall1mFicsit as iBasicWall1mFicsit,
    BasicWall4mFicsit as iBasicWall4mFicsit,
    Beacon as iBeacon,
    Biomass as iBiomass,
    BiomassBurner as iBiomassBurner,
    Cable as iCable,
    Chainsaw as iChainsaw,
    Coal as iCoal,
    CoalGenerator as iCoalGenerator,
    ColorCartridge as iColorCartridge,
    CompactedCoal as iCompactedCoal,
    Concrete as iConcrete,
    Constructor as iConstructor,
    ConveyorLiftMk1 as iConveyorLiftMk1,
    ConveyorMerger as iConveyorMerger,
    ConveyorSplitter as iConveyorSplitter,
    ConveyorBeltMk1 as iConveyorBeltMk1,
    ConveyorBeltMk2 as iConveyorBeltMk2,
    ConveyorLiftMk2 as iConveyorLiftMk2,
    ConveyorPole as iConveyorPole,
    CopperIngot as iCopperIngot,
    CopperOre as iCopperOre,
    CopperSheet as iCopperSheet,
    CraftBench as iCraftBench,
    DoubleWallOutletMk1 as iDoubleWallOutletMk1,
    EquipmentWorkshop as iEquipmentWorkshop,
    FluidBuffer as iFluidBuffer,
    Foundation1mFicsit as iFoundation1mFicsit,
    Foundation2mFicsit as iFoundation2mFicsit,
    Foundation4mFicsit as iFoundation4mFicsit,
    Foundry as iFoundry,
    HatcherRemains as iHatcherRemains,
    HeavyOilResidue as iHeavyOilResidue,
    HogRemains as iHogRemains,
    IronIngot as iIronIngot,
    IronOre as iIronOre,
    IronPlate as iIronPlate,
    IronRod as iIronRod,
    JumpPad as iJumpPad,
    Leaves as iLeaves,
    Limestone as iLimestone,
    LookoutTower as iLookoutTower,
    MinerMk1 as iMinerMk1,
    ModularFrame as iModularFrame,
    Mycelia as iMycelia,
    ObjectScanner as iObjectScanner,
    PersonalStorageBox as iPersonalStorageBox,
    PetroleumCoke as iPetroleumCoke,
    PipelineMk1 as iPipelineMk1,
    PipelinePump as iPipelinePump,
    PipelineSupport as iPipelineSupport,
    PipelineJunctionCross as iPipelineJunctionCross,
    PortableMiner as iPortableMiner,
    Power as iPower,
    PowerLine as iPowerLine,
    PowerPoleMk1 as iPowerPoleMk1,
    Ramp1mFicsit as iRamp1mFicsit,
    Ramp2mFicsit as iRamp2mFicsit,
    Ramp4mFicsit as iRamp4mFicsit,
    ReinforcedIronPlate as iReinforcedIronPlate,
    Rotor as iRotor,
    Screw as iScrew,
    SmartPlating as iSmartPlating,
    Smelter as iSmelter,
    SolidBiofuel as iSolidBiofuel,
    StackableConveyorPole as iStackableConveyorPole,
    SpaceElevator as iSpaceElevator,
    SpitterRemains as iSpitterRemains,
    SteelBeam as iSteelBeam,
    SteelIngot as iSteelIngot,
    SteelPipe as iSteelPipe,
    StingerRemains as iStingerRemains,
    StorageContainer as iStorageContainer,
    Sulfur as iSulfur,
    Tractor as iTractor,
    TruckStation as iTruckStation,
    UJellyLandingPad as iUJellyLandingPad,
    VersatileFramework as iVersatileFramework,
    WallOutletMk1 as iWallOutletMk1,
    Water as iWater,
    WaterExtractor as iWaterExtractor,
    Wire as iWire,
    Wood as iWood,
    XenoBasher as iXenoBasher,
    XenoZapper as iXenoZapper,
)

'''
Here are defined every recipe we care about
'''

ALL = None

def get_all():
    '''
    Returns a list of all recipes
    '''

    global ALL
    if ALL is None:
        import inspect, sys
        ALL = [ mbr for mbr in inspect.getmembers(sys.modules[__name__])
            if isinstance(mbr[1], Recipe) ]
    return ALL

def get_all_unlockable():
    '''
    Returns a list of all recipes unlockable through the MAM
    '''

    return [ recipe for recipe in get_all() if recipe.availability.mam ]

Assembler = Recipe(
    name='Assembler',
    availability=Availability(2, 1),
    wiki_path='/Assembler',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iReinforcedIronPlate, 8, None),
        Ingredient(iRotor, 4, None),
        Ingredient(iCable, 10, None)
    ],
    produces=[Ingredient(iAssembler, 1, None)]
)

AwesomeShop = Recipe(
    name='AWESOME Shop',
    availability=Availability(2, 4),
    wiki_path='/AWESOME_Shop',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iScrew, 200, None),
        Ingredient(iIronPlate, 10, None),
        Ingredient(iCable, 10, None)
    ],
    produces=[Ingredient(iAwesomeShop, 1, None)]
)

AwesomeSink = Recipe(
    name='AWESOME Sink',
    availability=Availability(2, 4),
    wiki_path='/AWESOME_Sink',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iReinforcedIronPlate, 15, None),
        Ingredient(iCable, 30, None),
        Ingredient(iConcrete, 45, None)
    ],
    produces=[Ingredient(iAwesomeSink, 1, None)]
)

BasicWall1mFicsit = Recipe(
    name='Basic Wall 1m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Walls',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 2, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iBasicWall1mFicsit, 1, None)]
)

BasicWall4mFicsit = Recipe(
    name='Basic Wall 4m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Walls',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 2, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iBasicWall4mFicsit, 1, None)]
)

Beacon = Recipe(
    name='Beacon',
    availability=Availability(1, 3),
    wiki_path='/Beacon',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iCable, 15, None),
        Ingredient(iIronPlate, 3, None),
        Ingredient(iIronRod, 1, None),
        Ingredient(iWire, 15, None)],
    produces=[Ingredient(iBeacon, 1, None)]
)

BiomassAlienProtein = Recipe(
    name='Biomass (Alien Protein)',
    wiki_path='/Biomass',
    availability=Availability(None, None, True),
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iAlienProtein, 1, 15)],
    produces=[Ingredient(iBiomass, 100, 1500)]
)

BiomassBurner = Recipe(
    name='Biomass Burner',
    availability=Availability(0, 6),
    wiki_path='/Biomass_Burner',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 15, None),
        Ingredient(iIronRod, 15, None),
        Ingredient(iWire, 25, None)],
    produces=[Ingredient(iBiomassBurner, 1, None)]
)

BiomassLeaves = Recipe(
    name='Biomass (Leaves)',
    availability=Availability(0, 6),
    wiki_path='/Biomass',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iLeaves, 10, 120)],
    produces=[Ingredient(iBiomass, 5, 60)]
)

BiomassMycelia = Recipe(
    name='Biomass (Mycelia)',
    wiki_path='/Biomass',
    availability=Availability(None, None, True),
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iMycelia, 10, 150)],
    produces=[Ingredient(iBiomass, 10, 150)]
)

BiomassWood = Recipe(
    name='Biomass (Wood)',
    availability=Availability(0, 6),
    wiki_path='/Biomass',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iWood, 4, 60)],
    produces=[Ingredient(iBiomass, 20, 300)]
)

Cable = Recipe(
    name='Cable',
    availability=Availability(0, 2),
    wiki_path='/Cable',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iWire, 2, 60)],
    produces=[Ingredient(iCable, 1, 30)]
)

Chainsaw = Recipe(
    name='Chainsaw',
    availability=Availability(2, 2),
    wiki_path='/Chainsaw',
    building_type=BuildingType.WORKSHOP,
    consumes=[Ingredient(iReinforcedIronPlate, 1, None)],
    produces=[Ingredient(iConveyorBeltMk2, 1, None)]
)

CoalMk1 = Recipe(
    name='Coal',
    availability=Availability(3, 1),
    wiki_path='/Coal',
    building_type=BuildingType.MINER,
    produces=[Ingredient(iCoal, None, 60)]
)

CoalGenerator = Recipe(
    name='Coal Generator',
    availability=Availability(3, 1),
    wiki_path='/Coal_Generator',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iReinforcedIronPlate, 20, None),
        Ingredient(iRotor, 10, None),
        Ingredient(iCable, 30, None)
    ],
    produces=[Ingredient(iCoalGenerator, 1, None)]
)

CoalPower = Recipe(
    name='Coal Power',
    availability=Availability(3, 1),
    wiki_path='/Coal_Generator',
    building_type=BuildingType.COAL_GENERATOR,
    consumes=[
        Ingredient(iCoal, None, 15),
        Ingredient(iWater, None, 45),
    ],
    produces=[Ingredient(iPower, None, 75)]
)

CompactedCoal = Recipe(
    name='Compacted Coal',
    availability=Availability(None, None, mam=True),
    wiki_path='/Compacted_Coal',
    building_type=BuildingType.ASSEMBLER,
    consumes=[
        Ingredient(iCoal, 5, 25),
        Ingredient(iSulfur, 5, 25)
    ],
    produces=[Ingredient(iCompactedCoal, 25, None)]
)

CompactedCoalPower = Recipe(
    name='Compacted Coal Power',
    availability=Availability(3, 1),
    wiki_path='/Coal_Generator',
    building_type=BuildingType.COAL_GENERATOR,
    consumes=[
        Ingredient(iCompactedCoal, None, 7.142857),
        Ingredient(iWater, None, 45),
    ],
    produces=[Ingredient(iPower, None, 75)]
)

Concrete = Recipe(
    name='Concrete',
    availability=Availability(0, 3),
    wiki_path='/Concrete',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iLimestone, 3, 45)],
    produces=[Ingredient(iConcrete, 1, 15)]
)

CopperIngot = Recipe(
    name='Copper Ingot',
    wiki_path='/Copper_Ingot',
    building_type=BuildingType.SMELTER,
    consumes=[Ingredient(iCopperOre, 1, 30)],
    produces=[Ingredient(iCopperIngot, 1, 30)]
)

CopperOreMk1 = Recipe(
    name='Copper Ore',
    availability=Availability(0, 2),
    wiki_path='/Copper_Ore',
    building_type=BuildingType.MINER,
    consumes=None,
    produces=[Ingredient(iCopperOre, None, 60)]
)

Constructor = Recipe(
    name='Constructor',
    availability=Availability(0, 3),
    wiki_path='/Constructor',
    building_type=BuildingType.BUILD_GUN,
    base_power_usage=4,
    consumes=[
        Ingredient(iReinforcedIronPlate, 2, None),
        Ingredient(iCable, 8, None)],
    produces=[Ingredient(iConstructor, 1, None)]
)

ConveyorBeltMk1 = Recipe(
    name='Conveyor Belt Mk. 1',
    availability=Availability(0, 4),
    wiki_path='/Conveyor_Belt#Mk.1',
    building_type=BuildingType.BUILD_GUN,
    consumes=[Ingredient(iIronPlate, 1, None)],
    produces=[Ingredient(iConveyorBeltMk1, 1, None)]
)

ConveyorBeltMk2 = Recipe(
    name='Conveyor Belt Mk.2',
    availability=Availability(2, 5),
    wiki_path='/Conveyor_Belt#Mk.2',
    building_type=BuildingType.BUILD_GUN,
    consumes=[Ingredient(iReinforcedIronPlate, 1, None)],
    produces=[Ingredient(iConveyorBeltMk2, 1, None)]
)

ConveyorLiftMk1 = Recipe(
    name='Conveyor Lift Mk.1',
    availability=Availability(1, 2),
    wiki_path='/Conveyor_Lift',
    building_type=BuildingType.BUILD_GUN,
    consumes=[Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iConveyorLiftMk1, 1, None)]
)

ConveyorLiftMk2 = Recipe(
    name='Conveyor Lift Mk.2',
    availability=Availability(2, 5),
    wiki_path='/Conveyor_Lift#Mk.2',
    building_type=BuildingType.BUILD_GUN,
    consumes=[Ingredient(iReinforcedIronPlate, 2, None)],
    produces=[Ingredient(iConveyorLiftMk2, 1, None)]
)

ConveyorMerger = Recipe(
    name='Conveyor Merger',
    availability=Availability(1, 2),
    wiki_path='/Conveyor_Merger',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 2, None),
        Ingredient(iIronRod, 2, None)],
    produces=[Ingredient(iConveyorMerger, 1, None)]
)

ConveyorPole = Recipe(
    name='Conveyor Pole',
    availability=Availability(0, 4),
    wiki_path='/Conveyor_Poles#Simple-0',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 1, None),
        Ingredient(iIronRod, 1, None),
        Ingredient(iConcrete, 1, None)],
    produces=[Ingredient(iConveyorPole, 1, None)]
)

ConveyorSplitter = Recipe(
    name='Conveyor Splitter',
    availability=Availability(1, 2),
    wiki_path='/Conveyor_Splitter',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 2, None),
        Ingredient(iCable, 2, None)],
    produces=[Ingredient(iConveyorSplitter, 1, None)]
)

CopperSheet = Recipe(
    name='Copper Sheet',
    availability=Availability(2, 1),
    wiki_path='/Copper_Sheet',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iCopperIngot, 2, 20)],
    produces=[Ingredient(iCopperSheet, 1, 10)]
)

CraftBench = Recipe(
    name='Craft Bench',
    wiki_path='/Craft_Bench',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 3, None),
        Ingredient(iIronRod, 3, None)],
    produces=[Ingredient(iCraftBench, 1, None)]
)

DoubleWallOutletMk1 = Recipe(
    name='Double Wall Outlet Mk.1',
    availability=Availability(0, 3),
    wiki_path='/Power_Pole#Double_Wall_Outlets',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iWire, 8, None),
        Ingredient(iIronRod, 2, None)],
    produces=[Ingredient(iDoubleWallOutletMk1, 1, None)]
)

EquipmentWorkshop = Recipe(
    name='Equipment Workshop',
    availability=Availability(0, 1),
    wiki_path='/Equipment_Workshop',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iWire, 8, None),
        Ingredient(iIronRod, 2, None)],
    produces=[Ingredient(iDoubleWallOutletMk1, 1, None)]
)

FluidBuffer = Recipe(
    name='Fluid Buffer',
    availability=Availability(3, 1),
    wiki_path='/Fluid_Buffer#Normal-0',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iCopperSheet, 10, None),
        Ingredient(iModularFrame, 5, None)],
    produces=[Ingredient(iFluidBuffer, 1, None)]
)

Foundation1mFicsit = Recipe(
    name='Foundation 1m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Foundations',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 5, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iFoundation1mFicsit, 1, None)]
)

Foundation2mFicsit = Recipe(
    name='Foundation 2m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Foundations',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 5, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iFoundation2mFicsit, 1, None)]
)

Foundation4mFicsit = Recipe(
    name='Foundation 4m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Foundations',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 5, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iFoundation4mFicsit, 1, None)]
)

Foundry = Recipe(
    name='Foundry',
    availability=Availability(3, 3),
    wiki_path='/Foundry',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iModularFrame, 10, None),
        Ingredient(iRotor, 10, None),
        Ingredient(iConcrete, 20, None),
    ],
    produces=[Ingredient(iFoundry, 1, None)]
)

HatcherProtein = Recipe(
    name='Hatcher Protein',
    wiki_path='/Alien_Protein',
    availability=Availability(None, None, True),
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iHatcherRemains, 1, 1)],
    produces=[Ingredient(iAlienProtein, 1, 1)]
)

HogProtein = Recipe(
    name='Hog Protein',
    wiki_path='/Alien_Protein',
    availability=Availability(None, None, True),
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iHogRemains, 1, 1)],
    produces=[Ingredient(iAlienProtein, 1, 1)]
)

IronIngot = Recipe(
    name='Iron Ingot',
    wiki_path='/Iron_Ingot',
    building_type=BuildingType.SMELTER,
    consumes=[Ingredient(iIronOre, 1, 30)],
    produces=[Ingredient(iIronIngot, 1, 30)]
)

IronOreMk1 = Recipe(
    name='Iron Ore',
    wiki_path='/Iron_Ore',
    building_type=BuildingType.MINER,
    consumes=None,
    produces=[Ingredient(iIronOre, None, 60)]
)

IronPlate = Recipe(
    name='Iron Plate',
    wiki_path='/Iron_Plate',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iIronIngot, 3, 30)],
    produces=[Ingredient(iIronPlate, 2, 20)]
)

IronRod = Recipe(
    name='Iron Rod',
    wiki_path='/Iron_Rod',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iIronIngot, 1, 15)],
    produces=[Ingredient(iIronRod, 1, 15)]
)

JumpPad = Recipe(
    name='Jump Pad',
    availability=Availability(2, 3),
    wiki_path='/Jump_Pad',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iRotor, 2, None),
        Ingredient(iIronPlate, 15, None),
        Ingredient(iCable, 10, None)
    ],
    produces=[Ingredient(iJumpPad, 1, None)]
)

LimestoneMk1 = Recipe(
    name='Limestone',
    availability=Availability(0, 3),
    wiki_path='/Limestone',
    building_type=BuildingType.MINER,
    consumes=None,
    produces=[Ingredient(iLimestone, None, 60)]
)

LookoutTower = Recipe(
    name='Lookout Tower',
    availability=Availability(1, 1),
    wiki_path='/Lookout_Tower',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 5, None),
        Ingredient(iIronRod, 5, None)],
    produces=[Ingredient(iLookoutTower, 1, None)]
)

MAM = Recipe(
    name='MAM',
    availability=Availability(1, 3),
    wiki_path='/MAM',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iReinforcedIronPlate, 5, None),
        Ingredient(iCable, 15, None),
        Ingredient(iWire, 45, None)],
    produces=[Ingredient(iConveyorMerger, 1, None)]
)

MinerMk1 = Recipe(
    name='Miner Mk. 1',
    availability=Availability(0, 1),
    wiki_path='/Miner',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iPortableMiner, 1, None),
        Ingredient(iIronPlate, 10, None),
        Ingredient(iConcrete, 10, None)],
    produces=[Ingredient(iMinerMk1, 1, None)]
)

ModularFrame = Recipe(
    name='Modular Frame',
    availability=Availability(2, 1),
    wiki_path='/Modular_Frame',
    building_type=BuildingType.ASSEMBLER,
    consumes=[
        Ingredient(iIronRod, 12, 12),
        Ingredient(iReinforcedIronPlate, 3, 3)
    ],
    produces=[Ingredient(iModularFrame, 2, 2)]
)

ObjectScanner = Recipe(
    name='Object Scanner',
    availability=Availability(1, 3),
    wiki_path='/Object_Scanner',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iReinforcedIronPlate, 4, None),
        Ingredient(iScrew, 50, None),
        Ingredient(iWire, 20, None)],
    produces=[Ingredient(iObjectScanner, 1, None)]
)

PersonalStorageBox = Recipe(
    name='Personal Storage Box',
    availability=Availability(1, 3),
    wiki_path='/Personal_Storage_Box',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 6, None),
        Ingredient(iIronRod, 6, None)],
    produces=[Ingredient(iPersonalStorageBox, 1, None)]
)

PetroleumCoke = Recipe(
    name='Petroleum Coke',
    availability=Availability(5, 1),
    wiki_path='/Petroleum_Coke',
    building_type=BuildingType.REFINERY,
    consumes=[Ingredient(iHeavyOilResidue, None, 40)],
    produces=[Ingredient(iPetroleumCoke, 120, None)]
)

PetroleumCokePower = Recipe(
    name='Petroleum Coke Power',
    availability=Availability(3, 1),
    wiki_path='/Coal_Generator',
    building_type=BuildingType.COAL_GENERATOR,
    consumes=[
        Ingredient(iPetroleumCoke, None, 25),
        Ingredient(iWater, None, 45),
    ],
    produces=[Ingredient(iPower, None, 75)]
)

PipelineMk1 = Recipe(
    name='Pipeline Mk.1',
    availability=Availability(3, 1),
    wiki_path='/Pipelines#Mk.1-0',
    building_type=BuildingType.BUILD_GUN,
    consumes=[Ingredient(iCopperSheet, 1, None)],
    produces=[Ingredient(iPipelineMk1, 1, None)]
)

PipelineJunctionCross = Recipe(
    name='Pipeline Junction Cross',
    availability=Availability(3, 1),
    wiki_path='/Pipeline_Junction_Cross',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iCopperSheet, 5, None),
    ],
    produces=[Ingredient(iPipelineJunctionCross, 1, None)]
)

PipelinePump = Recipe(
    name='Pipeline Pump',
    availability=Availability(3, 1),
    wiki_path='/Pipeline_Pump',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iCopperSheet, 2, None),
        Ingredient(iRotor, 2, None)
    ],
    produces=[Ingredient(iPipelinePump, 1, None)]
)

PipelineSupport = Recipe(
    name='Pipeline Support',
    availability=Availability(3, 1),
    wiki_path='/Pipeline_Supports#Simple-0',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 2, None),
        Ingredient(iConcrete, 2, None),
    ],
    produces=[Ingredient(iPipelineSupport, 1, None)]
)

PortableMiner = Recipe(
    name='Portable Miner',
    availability=Availability(0, 1),
    wiki_path='/Miner#Portable_Miner',
    building_type=BuildingType.WORKSHOP,
    consumes=[
        Ingredient(iIronPlate, 2, None),
        Ingredient(iIronRod, 4, None)],
    produces=[Ingredient(iPortableMiner, 1, None)]
)

PowerLine = Recipe(
    name='Power Line',
    availability=Availability(0, 2),
    wiki_path='Power_Line',
    building_type=BuildingType.BUILD_GUN,
    consumes=[Ingredient(iCable, 1, None)],
    produces=[Ingredient(iPowerLine, 1, None)]
)

PowerPoleMk1 = Recipe(
    name='Power Pole Mk.1',
    availability=Availability(0, 3),
    wiki_path='Power_Pole#Ground_Poles',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iWire, 3, None),
        Ingredient(iIronRod, 1, None),
        Ingredient(iConcrete, 1, None)],
    produces=[Ingredient(iPowerPoleMk1, 1, None)]
)

Ramp1mFicsit = Recipe(
    name='Ramp 1m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Foundations#Ramps',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 5, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iRamp1mFicsit, 1, None)]
)

Ramp2mFicsit = Recipe(
    name='Ramp 2m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Foundations#Ramps',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 5, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iRamp2mFicsit, 1, None)]
)

Ramp4mFicsit = Recipe(
    name='Ramp 4m (FICSIT)',
    availability=Availability(1, 1),
    wiki_path='/Foundations#Ramps',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 5, None),
        Ingredient(iIronPlate, 2, None)],
    produces=[Ingredient(iRamp4mFicsit, 1, None)]
)

ReinforcedIronPlate = Recipe(
    name='Reinforced Iron Plate',
    availability=Availability(0, 3),
    wiki_path='/Reinforced_Iron_Plate',
    building_type=BuildingType.ASSEMBLER,
    consumes=[
        Ingredient(iIronPlate, 6, 30),
        Ingredient(iScrew, 12, 60)],
    produces=[Ingredient(iReinforcedIronPlate, 1, 5)]
)

Rotor = Recipe(
    name='Rotor',
    availability=Availability(2, 1),
    wiki_path='/Rotor',
    building_type=BuildingType.ASSEMBLER,
    consumes=[
        Ingredient(iIronRod, 5, 20),
        Ingredient(iScrew, 25, 100)
    ],
    produces=[Ingredient(iRotor, 1, 4)]
)

Screw = Recipe(
    name='Screw',
    availability=Availability(0, 3),
    wiki_path='/Screw',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iIronRod, 1, 10)],
    produces=[Ingredient(iScrew, 4, 40)]
)

SmartPlating = Recipe(
    name='Smart Plating',
    availability=Availability(2, 1),
    wiki_path='/Smart_Plating',
    building_type=BuildingType.ASSEMBLER,
    consumes=[
        Ingredient(iReinforcedIronPlate, 1, 2),
        Ingredient(iRotor, 1, 2)
    ],
    produces=[Ingredient(iSmartPlating, 1, 2)]
)

Smelter = Recipe(
    name='Smelter',
    availability=Availability(0, 2),
    wiki_path='/Smelter',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronRod, 5, None),
        Ingredient(iWire, 8, None)],
    produces=[Ingredient(iSmelter, 1, None)]
)

SolidBiofuel = Recipe(
    name='Solid Biofuel',
    availability=Availability(2, 2),
    wiki_path='/Solid_Biofuel',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iBiomass, 8, 120)],
    produces=[Ingredient(iSolidBiofuel, 4, 60)]
)

SpaceElevator = Recipe(
    name='Space Elevator',
    availability=Availability(0, 6),
    wiki_path='/Space_Elevator',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iConcrete, 500, None),
        Ingredient(iIronPlate, 250, None),
        Ingredient(iIronRod, 400, None),
        Ingredient(iWire, 1500, None)],
    produces=[Ingredient(iSpaceElevator, 1, None)]
)

SpitterProtein = Recipe(
    name='Spitter Protein',
    wiki_path='/Alien_Protein',
    availability=Availability(None, None, True),
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iSpitterRemains, 1, 1)],
    produces=[Ingredient(iAlienProtein, 1, 1)]
)

StackableConveyorPole = Recipe(
    name='StackableConveyor Pole',
    availability=Availability(2, 5),
    wiki_path='/Conveyor_Poles#Stackable',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronRod, 2, None),
        Ingredient(iIronPlate, 2, None),
        Ingredient(iConcrete, 2, None),
    ],
    produces=[Ingredient(iStackableConveyorPole, 1, None)]
)

SteelBeam = Recipe(
    name='Steel Beam',
    wiki_path='/Steel_Beam',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[
        Ingredient(iSteelIngot, 4, 60),
    ],
    produces=[Ingredient(iSteelBeam, 1, 15)]
)

SteelIngot = Recipe(
    name='Steel Ingot',
    wiki_path='/Steel_Ingot',
    building_type=BuildingType.FOUNDRY,
    consumes=[
        Ingredient(iIronOre, 3, 45),
        Ingredient(iCoal, 3, 45),
    ],
    produces=[Ingredient(iSteelIngot, 3, 45)]
)

SteelPipe = Recipe(
    name='Steel Pipe',
    wiki_path='/Steel_Pipe',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[
        Ingredient(iSteelIngot, 3, 30),
    ],
    produces=[Ingredient(iSteelPipe, 2, 20)]
)

StingerProtein = Recipe(
    name='Stinger Protein',
    wiki_path='/Alien_Protein',
    availability=Availability(None, None, True),
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iStingerRemains, 1, 1)],
    produces=[Ingredient(iAlienProtein, 1, 1)]
)

StorageContainer = Recipe(
    name='Storage Container',
    availability=Availability(0, 5),
    wiki_path='/Storage_Container',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 10, None),
        Ingredient(iIronRod, 10, None)
    ],
    produces=Ingredient(iStorageContainer, 1, None)
)

Tractor = Recipe(
    name='Tractor',
    availability=Availability(3, 2),
    wiki_path='/Tractor',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iModularFrame, 5, None),
        Ingredient(iRotor, 5, None),
        Ingredient(iReinforcedIronPlate, 10, None),
    ],
    produces=Ingredient(iTractor, 1, None)
)

TruckStation = Recipe(
    name='Truck Station',
    availability=Availability(3, 2),
    wiki_path='/Truck_Station',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iModularFrame, 15, None),
        Ingredient(iRotor, 20, None),
        Ingredient(iCable, 50, None),
    ],
    produces=Ingredient(iTruckStation, 1, None)
)

UJellyLandingPad = Recipe(
    name='U-Jelly Landing Pad',
    availability=Availability(2, 3),
    wiki_path='/U-Jelly_Landing_Pad',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iRotor, 2, None),
        Ingredient(iCable, 20, None),
        Ingredient(iBiomass, 200, None),
    ],
    produces=[Ingredient(iUJellyLandingPad, 1, None)]
)

VersatileFramework = Recipe(
    name='Versatile Framework',
    availability=Availability(3, 3),
    wiki_path='/Versatile_Framework',
    building_type=BuildingType.ASSEMBLER,
    consumes=[
        Ingredient(iModularFrame, 1, 2.5),
        Ingredient(iSteelBeam, 12, 30)
    ],
    produces=[Ingredient(iVersatileFramework, 2, 5)]
)

WallOutletMk1 = Recipe(
    name='Wall Outlet Mk.1',
    availability=Availability(0, 3),
    wiki_path='/Power_Pole#Wall_Outlets',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iWire, 4, None),
        Ingredient(iIronRod, 1, None)],
    produces=[Ingredient(iWallOutletMk1, 1, None)]
)

Water = Recipe(
    name='Water',
    availability=Availability(3, 1),
    wiki_path='/Water',
    building_type=BuildingType.WATER_EXTRACTOR,
    consumes=[],
    produces=[Ingredient(iWater, None, 120)]
)

WaterExtractor = Recipe(
    name='Water Extractor',
    availability=Availability(3, 1),
    wiki_path='/Water_Extractor',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iCopperSheet, 20, None),
        Ingredient(iReinforcedIronPlate, 10, None),
        Ingredient(iRotor, 10, None)
    ],
    produces=[Ingredient(iWaterExtractor, 1, None)]
)

Wire = Recipe(
    name='Wire',
    availability=Availability(0, 2),
    wiki_path='/Wire',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iCopperIngot, 1, 15)],
    produces=[Ingredient(iWire, 2, 30)]
)

XenoBasher = Recipe(
    name='Xeno-Basher',
    availability=Availability(3, 4),
    wiki_path='/Xeno-Basher',
    building_type=BuildingType.WORKSHOP,
    consumes=[
        Ingredient(iModularFrame, 5, 3.75),
        Ingredient(iXenoZapper, 2, 1.5),
        Ingredient(iCable, 25, 18.75),
        Ingredient(iWire, 500, 375),
    ],
    produces=[Ingredient(iXenoBasher, 1, 0.75)]
)

XenoZapper = Recipe(
    name='Xeno-Zapper',
    wiki_path='/Xeno-Zapper',
    building_type=BuildingType.WORKSHOP,
    consumes=[
        Ingredient(iIronRod, 10, 15),
        Ingredient(iReinforcedIronPlate, 2, 3),
        Ingredient(iCable, 15, 22.5),
        Ingredient(iWire, 50, 75),
    ],
    produces=[Ingredient(iXenoZapper, 1, 1.5)]
)
