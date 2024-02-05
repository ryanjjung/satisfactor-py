from satisfactor_py.base import Purity, ResourceNode
from satisfactor_py.buildings import (
    Constructor,
    MinerMk1,
    Smelter
)
from satisfactor_py.conveyances import ConveyorBeltMk1
from satisfactor_py.factories import Factory
from satisfactor_py.items import (
    IronOre as iIronOre
)
from satisfactor_py.recipes import (
    CopperOreMk1 as rCopperOreMk1,
    IronOreMk1 as rIronOreMk1,
    IronIngot as rIronIngot,
    IronRod as rIronRod,
    Screw as rScrew
)
from satisfactor_py.storages import StorageContainer


def tier_0_screw_factory():
    '''
    Returns a simple factory containing a series of Tier 0 components that produces screws and
    stores them as follows:
        - Impure iron resource node (iron ore)
        - Smelter (iron ingots)
        - Constructor (iron rods)
        - Constructor (screws)
        - Storage container
    '''

    factory = Factory(name='Tier 0 Screw Factory')

    # Start by adding an impure iron resource node to the factory
    ironSource = ResourceNode(
        name='Impure Iron Source',
        purity=Purity.IMPURE,
        item=iIronOre
    )

    # Connect it to a miner
    ironMiner = MinerMk1(recipe=rIronOreMk1)

    # Uncomment the next line to produce an error
    #ironMiner = MinerMk1(recipe=rCopperOreMk1)
    ironSource.outputs[0].connect(ironMiner.inputs[0])

    # Connect the miner to a smelter
    ironSmelter = Smelter(
        name='Iron Smelter',
        recipe=rIronIngot
    )
    convOreToSmelter = ironMiner.connect(ironSmelter, ConveyorBeltMk1)

    # Connect the smelter to a constructor making rods
    rodConstructor = Constructor(
        name='Rod Constructor',
        recipe=rIronRod
    )
    convIngotsToConstructor = ironSmelter.connect(rodConstructor, ConveyorBeltMk1)

    # Connect the rod constructor to a constructor making screws
    screwConstructor = Constructor(
        name='Screw Constructor',
        recipe=rScrew
    )
    convRodsToConstructor = rodConstructor.connect(screwConstructor, ConveyorBeltMk1)

    # Connect the screw constructor to a storage container
    screwStorage = StorageContainer(name='Screw Storage')
    convScrewsToStorage = screwConstructor.connect(screwStorage, ConveyorBeltMk1)

    # Add everything to the factory
    factory.add([
        ironSource,
        ironMiner,
        convOreToSmelter,
        ironSmelter,
        convIngotsToConstructor,
        rodConstructor,
        convRodsToConstructor,
        screwConstructor,
        convScrewsToStorage,
        screwStorage
    ])
    return factory
