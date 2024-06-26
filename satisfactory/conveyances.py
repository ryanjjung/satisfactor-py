from satisfactory.base import (
    Availability,
    BuildingType,
    Conveyance,
    ConveyanceType,
    Dimension,
    Input,
    Output
)


ALL = None

def get_all() -> list[Conveyance]:
    '''
    Returns a list of all Conveyances defined in this module; caches the results for quick access.
    '''

    global ALL
    if ALL is None:
        import inspect
        import sys
        ALL = [ mbr[1] for mbr in inspect.getmembers(sys.modules[__name__], inspect.isclass)
            if issubclass(mbr[1], Conveyance) and mbr[1] is not Conveyance ]
    return ALL


class ConveyorBeltMk1(Conveyance):
    '''
    A first-tier conveyor belt carrying 60 Items per minute.
    '''

    def __init__(self,
        name: str='Conveyor Belt Mk.1',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(0, 4),
            wiki_path='/Conveyor_Belts#Mk.1-0',
            image_path='/c/c9/Conveyor_Belt_Mk.1.png',
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


class ConveyorBeltMk2(Conveyance):
    '''
    A second-tier conveyor belt carrying 120 Items per minute.
    '''

    def __init__(self,
        name='Conveyor Belt Mk.2',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(2, 5),
            wiki_path='/Conveyor_Belts#Mk.2-0',
            image_path='/e/e9/Conveyor_Belt_Mk.2.png',
            conveyance_type=ConveyanceType.BELT,
            rate=120,
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
    def __init__(self,
        name='Conveyor Lift Mk.1',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(1, 2),
            wiki_path='/Conveyor_Lifts#Mk.1-0',
            image_path='/2/2d/Conveyor_Lift_Mk.1.png',
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


class ConveyorLiftMk2(Conveyance):
    def __init__(self,
        name='Conveyor Lift Mk.2',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(2, 5),
            wiki_path='/Conveyor_Lifts#Mk.2-0',
            image_path='/8/8a/Conveyor_Lift_Mk.2.png',
            conveyance_type=ConveyanceType.BELT,
            rate=120,
            dimensions=Dimension(
                width=2,
                length=2,
                height=7
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


class PipelineMk1(Conveyance):
    '''
    A first-tier pipeline capable of moving up to 300m³ of fluid per minute.
    '''

    def __init__(self,
        name='Pipeline Mk. 1',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(0, 4),
            wiki_path='/Pipelines#Mk.1-0',
            image_path='/5/54/Pipeline_Mk.1.png',
            conveyance_type=ConveyanceType.PIPE,
            rate=300,
            dimensions=Dimension(
                width=2,
                length=1,
                height=2
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.PIPE
            )],
            outputs=[Output(
                attached_to=self,
                conveyance_type=ConveyanceType.PIPE
            )],
            **kwargs
        )


class PipelinePump(Conveyance):
    '''
    In the game, a Pipeline Pump provides additional headlift to pipelines. This tool doesn't care
    about headlift, so it acts here like any other pipeline conveyance.
    '''

    def __init__(self,
        name='Pipeline Pump Mk. 1',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(3, 1),
            wiki_path='/Pipeline_Pump',
            image_path='/2/2d/Pipeline_Pump_Mk.1.png',
            conveyance_type=ConveyanceType.PIPE,
            dimensions=Dimension(
                width=2,
                length=4,
                height=2
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.PIPE
            )],
            outputs=[Output(
                attached_to=self,
                conveyance_type=ConveyanceType.PIPE
            )],
            **kwargs
        )
