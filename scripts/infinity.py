#!/bin/env python3

import json
from satisfactor_py.base import (
    ConveyanceType,
    InfiniteSupplyNode
)
from satisfactor_py.buildings import (
    Assembler
)
from satisfactor_py.conveyances import (
    ConveyorBeltMk2
)
from satisfactor_py.items import (
    IronPlate as iIronPlate,
    ReinforcedIronPlate as iReinforcedIronPlate,
    Screw as iScrew
)
from satisfactor_py.factories import Factory
from satisfactor_py.recipes import (
    ReinforcedIronPlate as rReinforcedIronPlate
)
from satisfactor_py.storages import (
    StorageContainer
)


factory = Factory(
    name='Infinite Reinforced Iron Plates',
    tier=1,
    upgrade=2
)
infiniteIronPlates = InfiniteSupplyNode(iIronPlate, -1, ConveyanceType.BELT)
infiniteScrews = InfiniteSupplyNode(iScrew, -1, ConveyanceType.BELT)
assRIP = Assembler(
    name='Reinforced Iron Plate Assembler',
    recipe=rReinforcedIronPlate
)

convPlates = ConveyorBeltMk2()
convScrews = ConveyorBeltMk2()
infiniteIronPlates.outputs[0].connect(convPlates.inputs[0])
infiniteScrews.outputs[0].connect(convScrews.inputs[0])
convPlates.connect(assRIP, ConveyorBeltMk2)
convScrews.connect(assRIP, ConveyorBeltMk2)

storRIP = StorageContainer(name='Reinforced Iron Plate Storage')
assRIP.connect(storRIP, ConveyorBeltMk2)

factory.add([
    infiniteIronPlates,
    infiniteScrews,
    assRIP,
    storRIP
])

factory.save('/home/ryan/tmp/infinity.sat')

factory.simulate()
print(json.dumps(factory.get_errors_as_dict(), indent=2))
print(json.dumps([ing.to_dict() for ing in storRIP.ingredients], indent=2))
