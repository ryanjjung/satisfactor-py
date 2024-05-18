#!/bin/env python3

'''
This script iterates over every component defined
'''

import inspect
import requests
import satisfactory.base
import satisfactory.buildings
import satisfactory.conveyances
import satisfactory.items
import satisfactory.storages


BASE_IMAGE_PATH = './static/images/components/'

def get_all_classes():
    # Base
    base = [
        satisfactory.base.ResourceNode,
        satisfactory.base.InfiniteSupplyNode
    ]

    # Buildings
    buildings = satisfactory.buildings.get_all()

    # Conveyances
    conveyances = satisfactory.conveyances.get_all()

    # Storages
    storages = satisfactory.storages.get_all()

    all_classes = []
    all_classes.extend(base)
    all_classes.extend(buildings)
    all_classes.extend(conveyances)
    all_classes.extend(storages)

    return all_classes

def get_all_instances():
    # Items
    items = satisfactory.items.get_all()

    all_instances = []
    all_instances.extend(items)

    return all_instances

def save_image(obj, filename):
    if hasattr(obj, 'image_path') and obj.image_path is not None:
        url = f'{satisfactory.base.IMAGE_URL_BASE}{obj.image_path}'
        filename = f'{BASE_IMAGE_PATH}{filename}.png'
        print(f'Downloading {url} to {filename}')
        response = requests.get(url).content
        with open(filename, 'wb') as fh:
            fh.write(response)
    else:
        print(f'Objects of type {obj.__class__.__name__} have no image_path set.')
        print(f'    See the wiki article: {satisfactory.base.WIKI_URL_BASE}{obj.wiki_path}')


def main():
    for cls in get_all_classes():
        print()
        print(f'Inspecting class {cls.__name__}')
        obj = cls()
        save_image(obj, obj.__class__.__name__)

    for inst in get_all_instances():
        print()
        print(f'Inspecting instance {inst[0]}')
        save_image(inst[1], inst[0])

if __name__ == '__main__':
    main()
