from satisfactor_py.base import (
    Availability,
    BuildingType,
    Ingredient,
    Recipe
)
from satisfactor_py.items import (
    Alien_Protein as iAlien_Protein,
    Biomass as iBiomass,
    BiomassBurner as iBiomassBurner,
    Cable as iCable,
    Color_Cartridge as iColorCartridge,
    Concrete as iConcrete,
    Constructor as iConstructor,
    ConveyorBeltMk1 as iConveyorBeltMk1,
    ConveyorPole as iConveyorPole,
    CopperIngot as iCopperIngot,
    CopperOre as iCopperOre,
    CraftBench as iCraftBench,
    DoubleWallOutletMk1 as iDoubleWallOutletMk1,
    EquipmentWorkshop as iEquipmentWorkshop,
    Hatcher_Remains as iHatcher_Remains,
    Hog_Remains as iHog_Remains,
    IronIngot as iIronIngot,
    IronOre as iIronOre,
    IronPlate as iIronPlate,
    IronRod as iIronRod,
    Leaves as iLeaves,
    Limestone as iLimestone,
    MinerMk1 as iMinerMk1,
    Mycelia as iMycelia,
    PortableMiner as iPortableMiner,
    PowerLine as iPowerLine,
    PowerPoleMk1 as iPowerPoleMk1,
    ReinforcedIronPlate as iReinforcedIronPlate,
    Screw as iScrew,
    Smelter as iSmelter,
    SpaceElevator as iSpaceElevator,
    Spitter_Remains as iSpitter_Remains,
    Stinger_Remains as iStinger_Remains,
    StorageContainer as iStorageContainer,
    Wire as iWire,
    WallOutletMk1 as iWallOutletMk1,
    Wood as iWood,
)


# Recipes built from natural items

Hatcher_Protein = Recipe(
    name='Hatcher Protein',
    wiki_path='/Alien_Protein',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iHatcher_Remains, 1, 1)],
    produces=[Ingredient(iAlien_Protein, 1, 1)]
)

Spitter_Protein = Recipe(
    name='Spitter Protein',
    wiki_path='/Alien_Protein',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iSpitter_Remains, 1, 1)],
    produces=[Ingredient(iAlien_Protein, 1, 1)]
)

Stinger_Protein = Recipe(
    name='Stinger Protein',
    wiki_path='/Alien_Protein',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iStinger_Remains, 1, 1)],
    produces=[Ingredient(iAlien_Protein, 1, 1)]
)

Hog_Protein = Recipe(
    name='Hog Protein',
    wiki_path='/Alien_Protein',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iHog_Remains, 1, 1)],
    produces=[Ingredient(iAlien_Protein, 1, 1)]
)

Biomass_Leaves = Recipe(
    name='Biomass (Leaves)',
    availability=Availability(0, 6),
    wiki_path='/Biomass',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iLeaves, 10, 120)],
    produces=[Ingredient(iBiomass, 5, 60)]
)

Biomass_Wood = Recipe(
    name='Biomass (Wood)',
    availability=Availability(0, 6),
    wiki_path='/Biomass',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iWood, 4, 60)],
    produces=[Ingredient(iBiomass, 20, 300)]
)

Biomass_Mycelia = Recipe(
    name='Biomass (Mycelia)',
    wiki_path='/Biomass',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iMycelia, 10, 150)],
    produces=[Ingredient(iBiomass, 10, 150)]
)

Biomass_Alien_Protein = Recipe(
    name='Biomass (Alien Protein)',
    wiki_path='/Biomass',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iAlien_Protein, 1, 15)],
    produces=[Ingredient(iBiomass, 100, 1500)]
)


# Miner recipes

CopperOreMk1 = Recipe(
    name='Copper Ore',
    availability=Availability(0, 2),
    wiki_path='/Copper_Ore',
    building_type=BuildingType.MINER,
    consumes=None,
    produces=[Ingredient(iCopperOre, None, 60)]
)

IronOreMk1 = Recipe(
    name='Iron Ore',
    wiki_path='/Iron_Ore',
    building_type=BuildingType.MINER,
    consumes=None,
    produces=[Ingredient(iIronOre, None, 60)]
)

Limestone = Recipe(
    name='Limestone',
    availability=Availability(0, 3),
    wiki_path='/Limestone',
    building_type=BuildingType.MINER,
    consumes=None,
    produces=[Ingredient(iLimestone, None, 60)]
)


# Smelter recipes

CopperIngot = Recipe(
    name='Copper Ingot',
    wiki_path='/Copper_Ingot',
    building_type=BuildingType.SMELTER,
    consumes=[Ingredient(iCopperOre, 1, 30)],
    produces=[Ingredient(iCopperIngot, 1, 30)]
)

IronIngot = Recipe(
    name='Iron Ingot',
    wiki_path='/Iron_Ingot',
    building_type=BuildingType.SMELTER,
    consumes=[Ingredient(iIronOre, 1, 30)],
    produces=[Ingredient(iIronIngot, 1, 30)]
)


# Constructor recipes

Cable = Recipe(
    name='Cable',
    availability=Availability(0, 2),
    wiki_path='/Cable',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iWire, 2, 60)],
    produces=[Ingredient(iCable, 1, 30)]
)

Concrete = Recipe(
    name='Concrete',
    availability=Availability(0, 3),
    wiki_path='/Concrete',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iLimestone, 3, 45)],
    produces=[Ingredient(iConcrete, 1, 15)]
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

Screw = Recipe(
    name='Screw',
    availability=Availability(0, 3),
    wiki_path='/Screw',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iIronRod, 1, 10)],
    produces=[Ingredient(iScrew, 4, 40)]
)

Wire = Recipe(
    name='Wire',
    availability=Availability(0, 2),
    wiki_path='/Wire',
    building_type=BuildingType.CONSTRUCTOR,
    consumes=[Ingredient(iCopperIngot, 1, 15)],
    produces=[Ingredient(iWire, 2, 30)]
)


# Assembler recipes

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

# Build gun recipes

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

ConveyorPole = Recipe(
    name='Conveyor Pole',
    availability=Availability(0, 4),
    wiki_path='/Conveyor_Poles#Simple',
    building_type=BuildingType.BUILD_GUN,
    consumes=[
        Ingredient(iIronPlate, 1, None),
        Ingredient(iIronRod, 1, None),
        Ingredient(iConcrete, 1, None)],
    produces=[Ingredient(iConveyorPole, 1, None)]
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


# Workshop recipes

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
