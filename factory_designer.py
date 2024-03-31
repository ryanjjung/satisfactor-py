#!/bin/env python3

import sys
from argparse import ArgumentParser
from satisfactor_ui.app import FactoryDesigner

APP_ID='com.github.ryanjjung.satisfactory.FactoryDesigner'


def main():
    app = FactoryDesigner(application_id=APP_ID)
    app.run(sys.argv)

if __name__ == '__main__':
    main()