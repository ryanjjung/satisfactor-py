from satisfactor_py.base import Purity, ResourceNode
from satisfactor_py.buildings import (
    Constructor,
    ConveyorMerger,
    ConveyorSplitter,
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

def tier_1_screw_factory():
    '''
    Builds a Tier 1 screw factory from a normal resource node, splitting various outputs to maximize
    efficiency.

        - Iron resource node (Normal)
        - Miner Mk.1
        - Smelter x2
        - Constructor (Iron Rod) x4
        - Constructor (Screw) x6
        - Storage Container
    '''

    factory = Factory(name='Tier 1 Screw Factory')

    # Start with a normal iron source, attach it to a miner
    ironSource = ResourceNode(
        name='Normal Iron Source',
        purity=Purity.NORMAL,
        item=iIronOre
    )
    ironMiner = MinerMk1(
        name='Iron Miner',
        recipe=rIronOreMk1
    )
    ironSource.outputs[0].connect(ironMiner.inputs[0])

    # Build two smelters and split the ore from the miner to go to each of them
    oreSplitter = ConveyorSplitter(name='Iron Ore Splitter')
    ironMiner.connect(oreSplitter, ConveyorBeltMk1)

    ironSmelters = [Smelter(
        name=f'Iron Smelter #{i + 1}',
        recipe=rIronIngot) for i in range(2)]
    oreSplitter.connect(ironSmelters[0], ConveyorBeltMk1)
    oreSplitter.connect(ironSmelters[1], ConveyorBeltMk1)

    # Split the output of each smelter to supply two rod constructors per smelter
    ingotSplitters = [ConveyorSplitter(name=f'Iron Ingot Splitter #{i + 1}')
        for i in range(2)]
    ironSmelters[0].connect(ingotSplitters[0], ConveyorBeltMk1)
    ironSmelters[1].connect(ingotSplitters[1], ConveyorBeltMk1)

    ironRodConstructors = [Constructor(
        name=f'Iron Rod Constructor #{i + 1}',
        recipe=rIronRod
    ) for i in range(4)]
    ingotSplitters[0].connect(ironRodConstructors[0], ConveyorBeltMk1)
    ingotSplitters[0].connect(ironRodConstructors[1], ConveyorBeltMk1)
    ingotSplitters[1].connect(ironRodConstructors[2], ConveyorBeltMk1)
    ingotSplitters[1].connect(ironRodConstructors[3], ConveyorBeltMk1)

    # Merge output of each pair of rod constructors (15/m * 2 = 30/m) so we can split it up evenly
    # into (30/m ÷ 3 = 10/m) feeders for three screw constructors. With two of this pattern, we get
    # six constructors getting exactly the supply they need.
    rodMergers = [ConveyorMerger(name=f'Iron Rod Merger #{i + 1}')
        for i in range(2)]
    ironRodConstructors[0].connect(rodMergers[0], ConveyorBeltMk1)
    ironRodConstructors[1].connect(rodMergers[0], ConveyorBeltMk1)
    ironRodConstructors[2].connect(rodMergers[1], ConveyorBeltMk1)
    ironRodConstructors[3].connect(rodMergers[1], ConveyorBeltMk1)

    rodSplitters = [ConveyorSplitter(name=f'Iron Rod Splitter #{i + 1}')
        for i in range(2)]
    rodMergers[0].connect(rodSplitters[0], ConveyorBeltMk1)
    rodMergers[1].connect(rodSplitters[1], ConveyorBeltMk1)

    screwConstructors = [Constructor(
        name=f'Screw Constructor #{i + 1}',
        recipe=rScrew
    ) for i in range(6)]
    rodSplitters[0].connect(screwConstructors[0], ConveyorBeltMk1)
    rodSplitters[0].connect(screwConstructors[1], ConveyorBeltMk1)
    rodSplitters[0].connect(screwConstructors[2], ConveyorBeltMk1)
    rodSplitters[1].connect(screwConstructors[3], ConveyorBeltMk1)
    rodSplitters[1].connect(screwConstructors[4], ConveyorBeltMk1)
    rodSplitters[1].connect(screwConstructors[5], ConveyorBeltMk1)

    # The screw constructors emit 40 screws/m. Merging even two of these will outpace the output of
    # the merger by 20/m, so to keep efficiency up, we have to pipeline each constructor into its
    # own storage container.
    screwStorages = [StorageContainer(name=f'Screw Storage #{i + 1}')
        for i in range(6)]
    for i in range(6):
        screwConstructors[i].connect(screwStorages[i], ConveyorBeltMk1)

    # If we then merge the storages down into a single storage, we should see some errors pop up.abs
    storageMergers = [ConveyorMerger(name=f'Storage Merger #{i + 1}')
        for i in range(3)]
    for i in range(3):
        screwStorages[i].connect(storageMergers[0], ConveyorBeltMk1)
    for i in range(3, 6):
        screwStorages[i].connect(storageMergers[1], ConveyorBeltMk1)
    storageMergers[0].connect(storageMergers[2], ConveyorBeltMk1)
    storageMergers[1].connect(storageMergers[2], ConveyorBeltMk1)

    finalStorage = StorageContainer(name='Final Screw Storage')
    storageMergers[2].connect(finalStorage, ConveyorBeltMk1)

    factory.add([
        ironSource,
        ironMiner,
        oreSplitter,
        ironSmelters,
        ingotSplitters,
        ironRodConstructors,
        rodMergers,
        rodSplitters,
        screwConstructors,
        screwStorages,
        storageMergers,
        finalStorage
    ])
    return factory
