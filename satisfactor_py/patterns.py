from satisfactor_py.base import Purity, ResourceNode
from satisfactor_py.buildings import (
    Constructor,
    MinerMk1,
    Smelter,
)
from satisfactor_py.conveyances import ConveyorBeltMk1
from satisfactor_py.factories import Factory
from satisfactor_py.items import (
    CopperOre as iCopperOre,
    IronOre as iIronOre,
    Limestone as iLimestone
)
from satisfactor_py.recipes import (
    Cable as rCable,
    Concrete as rConcrete,
    CopperOreMk1 as rCopperOreMk1,
    CopperIngot as rCopperIngot,
    IronOreMk1 as rIronOreMk1,
    IronIngot as rIronIngot,
    IronRod as rIronRod,
    LimestoneMk1 as rLimestoneMk1,
    Screw as rScrew,
    Wire as rWire,
)
from satisfactor_py.storages import StorageContainer


def tier_0_screw_factory(
    purity: Purity = Purity.NORMAL
):
    '''
    Returns a simple factory containing a series of Tier 0 components that produces screws and
    stores them as follows:
        - Iron resource node (iron ore)
        - Smelter (iron ingots)
        - Constructor (iron rods)
        - Constructor (screws)
        - Storage container
    '''

    factory = Factory(name='Tier 0 Screw Factory')

    # Start by adding an iron resource node to the factory
    ironSource = ResourceNode(
        name=f'{purity.name.title()} Iron Source',
        purity=purity,
        item=iIronOre
    )

    # Connect it to a miner
    ironMiner = MinerMk1(
        name='Iron Miner',
        recipe=rIronOreMk1
    )

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

def tier_0_cable_factory(
    purity: Purity = Purity.NORMAL
):
    '''
    Returns a simple factory containing a series of Tier 0 components that produces cable and stores
    them as follows:
        - Normal copper resource node (copper ore)
        - Smelter (copper ingots)
        - Constructor (Wire)
        - Constructor (Cable)
        - Storage container
    '''

    factory = Factory(name='Tier 0 Cable Factory')

    # Start by adding a copper resource node to the factory
    copperSource = ResourceNode(
        name=f'{purity.name.title()} Copper Source',
        purity=purity,
        item=iCopperOre
    )

    # Connect it to a miner
    copperMiner = MinerMk1(
        name='Copper Miner',
        recipe=rCopperOreMk1
    )

    copperSource.outputs[0].connect(copperMiner.inputs[0])

    # Connect the miner to a smelter
    copperSmelter = Smelter(
        name='Copper Smelter',
        recipe=rCopperIngot
    )
    convOreToSmelter = copperMiner.connect(copperSmelter, ConveyorBeltMk1)

    # Connect the smelter to a constructor making wire
    wireConstructor = Constructor(
        name='Wire Constructor',
        recipe=rWire
    )
    convIngotsToConstructor = copperSmelter.connect(wireConstructor, ConveyorBeltMk1)

    # Connect the wire constructor to a cable constructor
    cableConstructor = Constructor(
        name='Cable Constructor',
        recipe=rCable
    )
    convWireToConstructor = wireConstructor.connect(cableConstructor, ConveyorBeltMk1)

    # Connect the cable constructor to a storage container
    cableStorage = StorageContainer(name='Cable Storage')
    convCableToStorage = cableConstructor.connect(cableStorage, ConveyorBeltMk1)

    # Add everything to the factory
    factory.add([
        copperSource,
        copperMiner,
        convOreToSmelter,
        copperSmelter,
        convIngotsToConstructor,
        wireConstructor,
        convWireToConstructor,
        cableConstructor,
        convCableToStorage,
        cableStorage
    ])
    return factory

def tier_0_concrete_factory(
    purity: Purity = Purity.NORMAL
):
    '''
    Returns a simple factory producing concrete using only Tier 0 items as follows:

        - Limestone resource node
        - Miner
        - Concrete constructor
        - Storage container
    '''

    factory = Factory(name='Tier 0 Concrete Factory')

    # Start with a limestone resource node
    limestoneSource = ResourceNode(
        name=f'{purity.name.title()} Limestone Source',
        purity=purity,
        item=iLimestone
    )

    # Connect a miner to it
    limestoneMiner = MinerMk1(
        name='Limestone Miner',
        recipe=rLimestoneMk1
    )
    limestoneSource.outputs[0].connect(limestoneMiner.inputs[0])

    # Connect it to a constructor producing limestone
    concreteConstructor = Constructor(
        name='Concrete Constructor',
        recipe=rConcrete
    )
    convLimestoneToConstructor = limestoneMiner.connect(concreteConstructor, ConveyorBeltMk1)

    concreteStorage = StorageContainer(name='Concrete Storage')
    convConcreteToStorage = concreteConstructor.connect(concreteStorage, ConveyorBeltMk1)

    factory.add([
        limestoneSource,
        limestoneMiner,
        convLimestoneToConstructor,
        concreteConstructor,
        convConcreteToStorage,
        concreteStorage
    ])
    return factory
