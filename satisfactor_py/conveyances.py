from satisfactor_py.base import (
    BuildingType,
    Conveyance,
    ConveyanceType,
    Input,
    Output
)

class ConveyorBeltMk1(Conveyance):
    def __init__(self, **kwargs):
        super().__init__(
            conveyance_type=ConveyanceType.BELT,
            rate=60,
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