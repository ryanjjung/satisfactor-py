#!/bin/env python3

import json
import sys

from satisfactor_py.patterns import tier_0_cable_factory


def main():
    factory = tier_0_cable_factory()
    factory.simulate()
    errors = {
        component.name: [error.to_dict() for error in component.errors]
        for component in factory.components
        if len(component.errors) > 0
    }
    print(json.dumps(errors, indent=2))
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    main()
