#!/bin/env python3

import sys
from argparse import ArgumentParser
from satisfactor_ui.app import FactoryDesigner


def main():
    app = FactoryDesigner()
    app.run(sys.argv)

if __name__ == '__main__':
    main()