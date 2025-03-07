import json

from satisfactory.items import Limestone
from satisfactory.patterns import tier_0_concrete_factory


def test_tier_0_concrete_factory():
    factory = tier_0_concrete_factory()

    # Unpack components for ease of access
    (
        limestoneSource,
        limestoneMiner,
        convLimestoneToConstructor,
        concreteConstructor,
        convConcreteToStorage,
        concreteStorage,
    ) = factory.components
    factory.simulate()
    errors = factory.get_errors_as_dict()

    # Basic factory data
    assert factory.name == 'Tier 0 Concrete Factory'
    assert factory.tier == 0
    assert factory.availability == 5

    # Test status of the limestone miner
    assert len(limestoneMiner.outputs) == 1
    output = limestoneMiner.outputs[0]
    assert output.ingredients[0].item == Limestone
    assert output.ingredients[0].rate == 60.0
    assert output.ingredients[0].amount == None

    # Test for errors
    assert len(errors) == 1
