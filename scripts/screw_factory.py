#!/bin/env python3

import json

from satisfactor_py.base import BuildingType, ResourceNode
from satisfactor_py.patterns import tier_1_screw_factory


def main():
    factory = tier_1_screw_factory()
    factory.simulate()
    errors = {
        component.name: [error.to_dict() for error in component.errors]
        for component in factory.components
        if len(component.errors) > 0
    }
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



    import pdb; pdb.set_trace()

if __name__ == '__main__':
    main()
