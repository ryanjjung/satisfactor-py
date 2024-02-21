#!/bin/env python3

import json

from satisfactor_py.base import BuildingType
from satisfactor_py.patterns import tier_2_biofuel_factory


def main():
    factory, starters = tier_2_biofuel_factory()
    factory.simulate_multi(starters)
    errors = {
        component.name: [error.to_dict() for error in component.errors]
        for component in factory.components
        if len(component.errors) > 0
    }
    print(f'Errors: {json.dumps(errors, indent=2)}')

    sink = factory.get_buildings_by_type(BuildingType.AWESOME_SINK)[0]
    print(f'Sink generating {sink.outputs[0].ingredients[0].rate} points per minue.')

if __name__ == '__main__':
    main()
