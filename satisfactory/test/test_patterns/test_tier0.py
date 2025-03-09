import satisfactory.base as base
import satisfactory.items as items
import satisfactory.patterns.tier0 as tier0

def test_iron_smelter_factories():
    for purity in base.Purity.__members__.values():
        factory = tier0.IronSmelterFactory(purity=purity)
        __test_iron_smelter_factory(factory=factory)

def test_iron_plate_factories():
    for purity in base.Purity.__members__.values():
        factory = tier0.IronPlateFactory(purity=purity)
        __test_iron_plate_factory(factory=factory)

def test_iron_rod_factories():
    for purity in base.Purity.__members__.values():
        factory = tier0.IronRodFactory(purity=purity)
        __test_iron_rod_factory(factory=factory)

def __test_iron_smelter_factory(factory: tier0.IronSmelterFactory):
    factory.simulate()
    (
        ironSource,
        ironMiner,
        convOreToSmelter,
        ironSmelter,
    ) = factory.components

    # Iron Resource Node
    assert type(ironSource.item) is type(items.IronOre)
    # assert ironSource.item == items.IronOre
    assert ironSource.traversed is True

    # Pure resource nodes create some efficiency problems at Tier 0
    if ironSource.purity == base.Purity.PURE:
        # Iron Miner
        # import pdb; pdb.set_trace()
        assert len(ironMiner.errors) == 1
        o = ironMiner.outputs[0]
        assert len(o.ingredients) == 1
        i = o.ingredients[0]
        ironRate = i.rate
        assert type(i.item) is type(items.IronOre)
        assert ironRate == 60.0 * ironSource.purity.value

        # Conveyance from the miner to the smelter
        assert len(convOreToSmelter.errors) == 1
        assert len(convOreToSmelter.ingredients) == 1
        i = convOreToSmelter.ingredients[0]
        assert i.rate == ironRate
        assert type(i.item) is type(items.IronOre)

        # Iron Smelter
        assert len(ironSmelter.errors) == 1
        assert len(ironSmelter.ingredients) == 1
        o = ironSmelter.outputs[0]
        assert len(o.ingredients) == 1
        i = o.ingredients[0]
        assert i.rate == 30.0
        assert type(i.item) is type(items.IronIngot)

    else:
        # Iron Miner
        assert len(ironMiner.errors) == 0
        o = ironMiner.outputs[0]
        assert len(o.ingredients) == 1
        i = o.ingredients[0]
        ironRate = i.rate
        assert type(i.item) is type(items.IronOre)
        assert ironRate == 60.0 * ironSource.purity.value * ironMiner.clock_rate

        # Conveyance from the miner to the smelter
        assert len(convOreToSmelter.errors) == 0
        assert len(convOreToSmelter.ingredients) == 1
        o = convOreToSmelter.outputs[0]
        assert len(o.ingredients) == 1
        i = o.ingredients[0]
        assert i.rate == ironRate
        assert type(i.item) is type(items.IronOre)

        # Iron Smelter
        if ironSource.purity == base.Purity.NORMAL:
            assert len(ironSmelter.errors) == 1
        else:
            assert len(ironSmelter.errors) == 0
        assert len(ironSmelter.ingredients) == 1
        o = ironSmelter.outputs[0]
        assert len(o.ingredients) == 1
        i = o.ingredients[0]
        assert i.rate == 30.0
        assert type(i.item) is type(items.IronIngot)

def __test_iron_plate_factory(factory: tier0.IronPlateFactory):
    factory.simulate()
    (
        ironSource,
        ironMiner,
        convOreToSmelter,
        ironSmelter,
        convIngotsToConstructor,
        plateConstructor,
    ) = factory.components

    # Conveyance from the smelter to the constructor
    assert len(convIngotsToConstructor.errors) == 0
    assert len(convIngotsToConstructor.ingredients) == 1
    o = convIngotsToConstructor.outputs[0]
    assert len(o.ingredients) == 1
    i = o.ingredients[0]
    assert i.rate == 30.0
    assert type(i.item) is type(items.IronIngot)

    # Iron Plate Constructor
    assert len(plateConstructor.errors) == 0
    assert len(plateConstructor.ingredients) == 1
    o = plateConstructor.outputs[0]
    assert len(o.ingredients) == 1
    i = o.ingredients[0]
    assert i.rate == 20.0
    assert type(i.item) is type(items.IronPlate)

def __test_iron_rod_factory(factory: tier0.IronRodFactory):
    factory.simulate()
    (
        ironSource,
        ironMiner,
        convOreToSmelter,
        ironSmelter,
        convIngotsToConstructor,
        rodConstructor,
    ) = factory.components

    # Conveyance from the smelter to the constructor
    assert len(convIngotsToConstructor.errors) == 0
    assert len(convIngotsToConstructor.ingredients) == 1
    o = convIngotsToConstructor.outputs[0]
    assert len(o.ingredients) == 1
    i = o.ingredients[0]
    assert i.rate == 30.0
    assert type(i.item) is type(items.IronIngot)

    # Iron Rod Constructor
    assert len(rodConstructor.errors) == 1
    assert len(rodConstructor.ingredients) == 1
    o = rodConstructor.outputs[0]
    assert len(o.ingredients) == 1
    i = o.ingredients[0]
    assert i.rate == 15.0
    assert type(i.item) is type(items.IronRod)

def test_storage_factory():
    factory = tier0.IronRodFactory()
    rodConstructor = factory.components[-1]
    storage = tier0.StorageFactory(source=rodConstructor)
    (
        convRodsToStorage,
        rodStorage
    ) = storage.components
    factory.add(storage.components)
    factory.simulate()

    # Conveyance from the constructor to storage
    assert len(convRodsToStorage.errors) == 0
    assert len(convRodsToStorage.ingredients) == 1
    o = convRodsToStorage.outputs[0]
    assert len(o.ingredients) == 1
    i = o.ingredients[0]
    assert i.rate == 15.0
    assert type(i.item) is type(items.IronRod)

    # Iron Rod Storage
    assert len(rodStorage.errors) == 0
    assert len(rodStorage.ingredients) == 1
    o = rodConstructor.outputs[0]
    assert len(o.ingredients) == 1
    i = o.ingredients[0]
    assert i.rate == 15.0
    assert type(i.item) is type(items.IronRod)
