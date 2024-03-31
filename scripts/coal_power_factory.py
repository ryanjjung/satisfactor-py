#!/bin/env python3

import json
import sys

from satisfactor_py.patterns import tier_3_coal_power_factory


def main():
    factory = tier_3_coal_power_factory()
    factory.simulate()
    errors = factory.get_errors_as_dict()
    print(json.dumps(errors, indent=2))

if __name__ == '__main__':
    main()
