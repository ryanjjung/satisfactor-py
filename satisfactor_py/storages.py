from satisfactor_py.base import (
    Availability,
    BuildingType,
    ConveyanceType,
    Dimension,
    Input,
    Output,
    Storage
)


ALL = None

def get_all():
    '''
    Returns a list of all Storages defined in this module; caches the results for quick access.
    '''

    global ALL
    if ALL is None:
        import inspect
        import sys
        ALL = [ mbr[1] for mbr in inspect.getmembers(sys.modules[__name__], inspect.isclass)
            if issubclass(mbr[1], Storage) and mbr[1] is not Storage ]
    return ALL



class FluidBuffer(Storage):
    '''
    Storage for liquids with a single input and output and a 400m³ capacity.
    '''

    def __init__(self,
        name: str = 'Fluid Buffer',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(3, 1),
            wiki_path='/Fluid_Buffer#Normal-0',
            image_path='/5/53/Fluid_Buffer.png',
            stacks=400,
            dimensions=Dimension(
                width=6,
                length=6,
                height=8
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


class StorageContainer(Storage):
    '''
    A Storage Container with a single input and output and 24 inventory slots.
    '''

    def __init__(self,
        name: str = 'Storage Container',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(0, 5),
            wiki_path='/Storage_Container#Normal-0',
            image_path='/2/20/Storage_Container.png',
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
