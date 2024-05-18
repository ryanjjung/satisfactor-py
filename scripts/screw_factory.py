#!/bin/env python3

import json

from satisfactory.base import BuildingType, ResourceNode
from satisfactory.patterns import tier_1_screw_factory


def main():
    factory = tier_1_screw_factory()
    factory.simulate()
    errors = factory.get_errors_as_dict()
    print(f'Errors: {json.dumps(errors, indent=2)}')

    print('Components without ingredients:')
    for component in factory.components:
        if type(component) != ResourceNode:
            if len(component.ingredients) == 0:
                print(component)

    print('\nContents of storage:')
    storages = factory.get_buildings_by_type(BuildingType.STORAGE)
    for storage in storages:
        for ingredient in storage.ingredients:
            print(f'{storage} - {ingredient.item}@{ingredient.rate}')


if __name__ == '__main__':
    main()
