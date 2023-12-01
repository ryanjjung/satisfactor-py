from satisfactor_py.base import (
    BuildingType,
    Ingredient,
    Recipe
)
from satisfactor_py.items import (
    CopperOre as iCopperOre,
    IronOre as iIronOre,
    IronIngot as iIronIngot,
)


CopperOreMk1 = Recipe(
    name='Copper Ore',
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

IronIngot = Recipe(
    name='Iron Ingot',
    wiki_path='/Iron_Ingot',
    building_type=BuildingType.SMELTER,
    consumes=[Ingredient(iIronOre, None, 30)],
    produces=[Ingredient(iIronIngot, None, 30)]
)
