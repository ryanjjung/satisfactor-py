#!/bin/env python3

import sys
from argparse import ArgumentParser
from factory_designer_gtk.app import FactoryDesigner


def main():
    app = FactoryDesigner()
    app.run(sys.argv)

if __name__ == '__main__':
    main()