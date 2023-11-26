#!/bin/env python3

from satisfactor_py.base import Purity, ResourceNode
from satisfactor_py.buildings import MinerMk1, Smelter
from satisfactor_py.conveyances import ConveyorBeltMk1
from satisfactor_py.factories import Factory
from satisfactor_py.recipes import IronOreMk1, IronIngot
from satisfactor_py.storages import StorageContainer

def build_test_factory():
    factory = Factory(name='Ironworks')

    # Start with an iron resource node
    ironSource = ResourceNode(
        name='Normal Iron Source',
        purity=Purity.NORMAL
    )

    # Build a miner and hook it to the resource node
    ironMiner = MinerMk1(recipe=IronOreMk1)
    ironSource.outputs[0].connect(ironMiner.inputs[0])

    # Keep adding these things to the factory as we go
    factory.add([ironSource, ironMiner])

    # Add a smelter and hook it up to the miner with a conveyor belt
    ironSmelter1 = Smelter(
        name='Iron Smelter #1',
        recipe=IronIngot
    )
    ironOreToSmelter1 = ConveyorBeltMk1()
    ironOreToSmelter1.inputs[0].connect(ironMiner.outputs[0])
    ironOreToSmelter1.outputs[0].connect(ironSmelter1.inputs[0])
    factory.add([ironOreToSmelter1, ironSmelter1])

    # Move the ingots into storage
    ironIngotStorage = StorageContainer(id='storage')
    ironIngotToStorage = ConveyorBeltMk1()
    ironIngotToStorage.inputs[0].connect(ironSmelter1.outputs[0])
    ironIngotToStorage.outputs[0].connect(ironIngotStorage.inputs[0])
    factory.add([ironIngotToStorage, ironIngotStorage])

    return factory

factory = build_test_factory()
factory.simulate()
# factory.drain()
