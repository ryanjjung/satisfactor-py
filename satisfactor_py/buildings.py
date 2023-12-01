from satisfactor_py.base import (
    Building,
    BuildingType,
    ConveyanceType,
    Dimension,
    Input,
    Item,
    Output,
    Recipe
)


class Miner(Building):
    '''
    A type of Building that takes input from a resource node and outputs items on a conveyor belt.
    '''

    def __init__(self, **kwargs):
        super().__init__(
            building_type=BuildingType.MINER,
            inputs=[Input(
                conveyance_type=ConveyanceType.RESOURCE_NODE,
                attached_to=self
            )],
            outputs=[Output(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self
            )],
            dimensions=Dimension(
                width=6,
                length=14,
                height=18
            ),
            **kwargs
        )


class MinerMk1(Miner):
    '''
    A first-tier Miner
    '''

    def __init__(self, **kwargs):
        super().__init__(
            name='Miner Mk. 1',
            **kwargs
        )


class Smelter(Building):
    '''
    A Smelter building
    '''

    def __init__(self, **kwargs):
        super().__init__(
            building_type=BuildingType.SMELTER,
            dimensions=Dimension(
                width=6,
                length=9,
                height=9
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT
            )],
            outputs=[Output(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT
            )],
            **kwargs
        )
