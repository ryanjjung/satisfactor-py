#!/bin/env python3

import json
import pickle
import sys

from argparse import ArgumentParser
from satisfactor_py.patterns import tier_0_screw_factory


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
        factory = tier_0_screw_factory()
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
