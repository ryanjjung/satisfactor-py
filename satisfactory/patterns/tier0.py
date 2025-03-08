import satisfactory.base as base
import satisfactory.buildings as buildings
import satisfactory.conveyances as conveyances
import satisfactory.factories as factories
import satisfactory.items as items
import satisfactory.recipes as recipes


def screw_factory(purity: base.Purity = base.Purity.NORMAL) -> factories.Factory:
    """Returns a simple factory containing a series of Tier 0 components that produces screws and
    stores them as follows:
        - Iron resource node (iron ore)
        - Smelter (iron ingots)
        - Constructor (iron rods)
        - Constructor (screws)
        - Storage container
    """

    factory = factories.Factory(name='Tier 0 Screw Factory')
    factory.tier = 0
    factory.availability = 5

    # Start by adding an iron resource node to the factory
    ironSource = base.ResourceNode(name=f'{purity.name.title()} Iron Source', purity=purity, item=items.IronOre)

    # Connect it to a miner
    ironMiner = buildings.MinerMk1(name='Iron Miner', recipe=recipes.IronOreMk1)

    # Uncomment the next line to produce an error
    # ironMiner = MinerMk1(recipe=rCopperOreMk1)
    ironSource.outputs[0].connect(ironMiner.inputs[0])

    # Connect the miner to a smelter
    ironSmelter = buildings.Smelter(name='Iron Smelter', recipe=recipes.IronIngot)
    convOreToSmelter = ironMiner.connect(ironSmelter, conveyances.ConveyorBeltMk1)

    # Connect the smelter to a constructor making rods
    rodConstructor = buildings.Constructor(name='Rod Constructor', recipe=recipes.IronRod)
    convIngotsToConstructor = ironSmelter.connect(rodConstructor, buildings.ConveyorBeltMk1)

    # Connect the rod constructor to a constructor making screws
    screwConstructor = buildings.Constructor(name='Screw Constructor', recipe=recipes.Screw)
    convRodsToConstructor = rodConstructor.connect(screwConstructor, conveyances.ConveyorBeltMk1)

    # Connect the screw constructor to a storage container
    screwStorage = buildings.StorageContainer(name='Screw Storage')
    convScrewsToStorage = screwConstructor.connect(screwStorage, conveyances.ConveyorBeltMk1)

    # Add everything to the factory
    factory.add(
        [
            ironSource,
            ironMiner,
            convOreToSmelter,
            ironSmelter,
            convIngotsToConstructor,
            rodConstructor,
            convRodsToConstructor,
            screwConstructor,
            convScrewsToStorage,
            screwStorage,
        ]
    )
    return factory
