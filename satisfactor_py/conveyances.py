from satisfactor_py.base import (
    Availability,
    BuildingType,
    Conveyance,
    ConveyanceType,
    Dimension,
    Input,
    Output
)

class ConveyorBeltMk1(Conveyance):
    '''
    A first-tier conveyor belt carrying 60 Items per minute.
    '''

    def __init__(self, **kwargs):
        super().__init__(
            name='Conveyor Belt Mk.1',
            availability=Availability(0, 4),
            wiki_path='/Conveyor_Belt#Mk.1',
            conveyance_type=ConveyanceType.BELT,
            rate=60,
            dimensions=Dimension(
                width=2,
                length=1,
                height=1
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT,
            )],
            outputs=[Output(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT
            )],
            **kwargs
        )


class ConveyorLiftMk1(Conveyance):
    def __init__(self, **kwargs):
        super().__init__(
            name='Conveyor Lift Mk.1',
            availability=Availability(1, 2),
            wiki_path='/Conveyor_Lift',
            conveyance_type=ConveyanceType.BELT,
            rate=60,
            dimensions=Dimension(
                width=2,
                length=2,
                height=7 # At a minimum, adjust after instantiation as needed
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
