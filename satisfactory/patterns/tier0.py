import satisfactory.base as base
import satisfactory.buildings as buildings
import satisfactory.conveyances as conveyances
import satisfactory.factories as factories
import satisfactory.items as items
import satisfactory.recipes as recipes
import satisfactory.storages as storages


class IronSmelterFactory(factories.Factory):
    """Returns a factory that draws Iron Ore from a ResourceNode of the given purity and connects it to a single
    smelter.
    """

    def __init__(self, purity: base.Purity = base.Purity.NORMAL):
        super().__init__(name='Tier 0 Iron Smelter Factory')
        self.tier = 0
        self.availability = 5

        self.ironSource = base.ResourceNode(
            name=f'{purity.name.title()} Iron Source', purity=purity, item=items.IronOre
        )
        self.ironMiner = buildings.MinerMk1(name='Iron Miner Mk. 1', recipe=recipes.IronOreMk1)
        self.ironSource.outputs[0].connect(connection=self.ironMiner.inputs[0])
        self.ironSmelter = buildings.Smelter(name='Iron Smelter', recipe=recipes.IronIngot)
        self.convOreToSmelter = self.ironMiner.connect(target=self.ironSmelter, conveyance=conveyances.ConveyorBeltMk1)

        self.add(components=[self.ironSource, self.ironMiner, self.convOreToSmelter, self.ironSmelter])


class IronPlateFactory(factories.Factory):
    def __init__(self, purity: base.Purity = base.Purity.NORMAL):
        """Returns a factory that builds Iron Plates at Tier 0."""

        super().__init__(name='Tier 0 Iron Plate Factory')
        self.tier = 0
        self.availability = 5

        self.smelter_factory = IronSmelterFactory(purity=purity)
        (ironSource, ironMiner, convOreToSmelter, ironSmelter) = self.smelter_factory.components

        self.plateConstructor = buildings.Constructor(name='Iron Plate Constructor', recipe=recipes.IronPlate)
        self.convIngotsToConstructor = ironSmelter.connect(
            target=self.plateConstructor, conveyance=conveyances.ConveyorBeltMk1
        )
        self.add(
            components=[
                self.smelter_factory.components,
                [
                    self.convIngotsToConstructor,
                    self.plateConstructor,
                ],
            ]
        )


class IronRodFactory(factories.Factory):
    def __init__(self, purity: base.Purity = base.Purity.NORMAL):
        """Returns a factory that builds Iron Rods at Tier 0."""

        super().__init__(name='Tier 0 Iron Rod Factory')
        self.tier = 0
        self.availability = 5

        self.smelter_factory = IronSmelterFactory(purity=purity)
        (ironSource, ironMiner, convOreToSmelter, ironSmelter) = self.smelter_factory.components

        self.rodConstructor = buildings.Constructor(name='Iron Rod Constructor', recipe=recipes.IronRod)
        self.convIngotsToConstructor = ironSmelter.connect(
            target=self.rodConstructor, conveyance=conveyances.ConveyorBeltMk1
        )
        self.add(
            components=[
                self.smelter_factory.components,
                [
                    self.convIngotsToConstructor,
                    self.rodConstructor,
                ],
            ]
        )


class StorageFactory(factories.Factory):
    def __init__(self, source: base.Building):
        """Returns a factory that routes items from the provided building into a storage container."""

        super().__init__(name='Tier 0 Iron Rod Factory')
        self.tier = 0
        self.availability = 5

        self.storage = storages.StorageContainer()
        self.convToStorage = source.connect(target=self.storage, conveyance=conveyances.ConveyorBeltMk1)

        self.add(components=[self.convToStorage, self.storage])
