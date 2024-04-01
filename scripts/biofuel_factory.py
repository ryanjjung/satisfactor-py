#!/bin/env python3

import json

from satisfactor_py.base import BuildingType
from satisfactor_py.patterns import tier_2_biofuel_factory


def main():
    factory, starters = tier_2_biofuel_factory()
    factory.save('/home/ryan/tmp/biofuel.sat')
    factory.simulate_multi(starters)
    errors = factory.get_errors_as_dict()
    print(f'Errors: {json.dumps(errors, indent=2)}')

    sink = factory.get_buildings_by_type(BuildingType.AWESOME_SINK)[0]
    print(f'Sink generating {sink.outputs[0].ingredients[0].rate} points per minute.')


if __name__ == '__main__':
    main()

