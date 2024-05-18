#!/bin/env python3

import json
from satisfactory.base import (
    ConveyanceType,
    InfiniteSupplyNode
)
from satisfactory.buildings import (
    Assembler
)
from satisfactory.conveyances import (
    ConveyorBeltMk2
)
from satisfactory.items import (
    IronPlate as iIronPlate,
    ReinforcedIronPlate as iReinforcedIronPlate,
    Screw as iScrew
)
from satisfactory.factories import Factory
from satisfactory.recipes import (
    ReinforcedIronPlate as rReinforcedIronPlate
)
from satisfactory.storages import (
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
