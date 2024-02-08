from satisfactor_py.base import (
    Availability,
    Building,
    BuildingType,
    ConveyanceType,
    Dimension,
    Input,
    Item,
    Output,
    Recipe,
    ResourceNode
)


class BiomassBurner(Building):
    '''
    A type of Building where biomass can be burned into power
    '''

    def __init__(self, **kwargs):
        super().__init__(
            building_type=BuildingType.GENERATOR,
            availability=Availability(0, 6),
            dimensions=Dimension(
                width=8,
                length=8,
                height=7
            ),
            **kwargs
        )


class Constructor(Building):
    '''
    A type of Building which converts an item of one type into an item of another. Has one input and
    one output.
    '''
    def __init__(self, **kwargs):
        super().__init__(
            building_type=BuildingType.CONSTRUCTOR,
            availability=Availability(0, 3),
            base_power_usage=4,
            dimensions=Dimension(
                width=8,
                length=10,
                height=8
            ),
            inputs=[Input(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self)],
            outputs=[Output(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self)],
            **kwargs
        )


class Miner(Building):
    '''
    A type of Building that takes input from a ResourceNode and outputs Items on a Conveyor Belt.
    '''

    def __init__(self, **kwargs):
        super().__init__(
            building_type=BuildingType.MINER,
            dimensions=Dimension(
                width=6,
                length=14,
                height=18
            ),
            inputs=[Input(
                conveyance_type=ConveyanceType.RESOURCE_NODE,
                attached_to=self
            )],
            outputs=[Output(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self
            )],
            **kwargs
        )

    def can_process(self):
        '''
        Returns True if the conditions are right for processing the Miner recipe.
        '''

        # All the basic building tests
        super().can_process()

        # If it's not connected, we can't process
        if not self.inputs[0].source:
            return False

        # It can only be attached to a resource node
        resource_node = self.inputs[0].source.attached_to
        if type(resource_node) is not ResourceNode:
            return False

        # The recipe must be of a special kind that consumes nothing and produces only one thing
        if self.recipe.consumes != None or len(self.recipe.produces) != 1:
            return False

        # The resource node must produce the right item
        if resource_node.item != self.recipe.produces[0].item:
            return False

        return True


    def process(self):
        '''
        Miners must additionally apply a purity factor to their outputs
        '''

        self.can_process()
        super().process()
        self.outputs[0].ingredients[0].rate = \
            self.outputs[0].ingredients[0].rate * self.inputs[0].source.attached_to.purity.value


class MinerMk1(Miner):
    '''
    A first-tier Miner
    '''

    def __init__(self, name='Miner Mk.1', **kwargs):
        super().__init__(
            name=name,
            availability=Availability(0, 1),
            wiki_path='/Miner#Mk.1',
            base_power_usage=5,
            **kwargs
        )


class Smelter(Building):
    '''
    A Smelter Building
    '''

    def __init__(self, name='Smelter', **kwargs):
        super().__init__(
            name=name,
            availability=Availability(0, 2),
            wiki_path='/Smelter',
            base_power_usage=4,
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


class SpaceElevator(Building):
    '''
    A Space Elevator Building
    '''

    def __init__(self, name='Space Elevator', **kwargs):
        super().__init__(
            name=name,
            availability=Availability(0, 6),
            wiki_path='/Space_Elevator',
            building_type=BuildingType.SPACE_ELEVATOR,
            dimensions=Dimension(
                width=54,
                length=54,
                height=118
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT) for i in range(0, 6)],
            power_connections=0,
            **kwargs
        )
