from satisfactor_py.base import (
    BuildingType,
    ConveyanceType,
    Dimension,
    Input,
    Output,
    Storage
)

class StorageContainer(Storage):
    '''
    A Storage Container with a single input and 24 inventory slots.
    '''

    def __init__(self, **kwargs):
        super().__init__(
            name='Storage Container',
            availability=Availability(0, 5),
            wiki_path='/Storage_Container',
            stacks=24,
            dimensions=Dimension(
                width=5,
                length=10,
                height=4
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
