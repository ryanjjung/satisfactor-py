#!/bin/env python3

import json
import sys

from satisfactory.patterns import tier_3_steel_beam_factory


def main():
    factory = tier_3_steel_beam_factory()
    factory.simulate()
    errors = factory.get_errors_as_dict()
    print(json.dumps(errors, indent=2))

if __name__ == '__main__':
    main()
