#!/bin/env python3

import json
import pickle
import sys

from argparse import ArgumentParser

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


def create_tier_0_screw_factory():
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

def parse_args():
    parser = ArgumentParser(description='Test with Pickle files')
    parser.add_argument('-l', '--loadfile',
        help='Load a screw factory from a previously saved file')
    parser.add_argument('-s', '--savefile',
        help='Generate a new screw factory and save it')
    return parser.parse_args()

def main():
    args = parse_args()

    if args.loadfile:
        with open(args.loadfile, 'rb') as fh:
            factory = pickle.load(fh)
    elif args.savefile:
        factory = create_tier_0_screw_factory()
        with open(args.savefile, 'wb') as fh:
            pickle.dump(factory, fh, pickle.HIGHEST_PROTOCOL)
    else:
        print('[ERROR] You must provide either a loadfile or savefile option.')
        sys.exit(1)

    factory.test()
    factory.drain()
    factory.simulate()
    errors = {
        component.name: [error.to_dict() for error in component.errors]
        for component in factory.components
        if len(component.errors) > 0
    }
    print(json.dumps(errors, indent=2))

if __name__ == '__main__':
    main()
