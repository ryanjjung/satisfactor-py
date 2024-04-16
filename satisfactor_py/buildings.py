from satisfactor_py.base import (
    Availability,
    Building,
    BuildingCategory,
    BuildingType,
    ComponentError,
    ComponentErrorLevel,
    ConveyanceType,
    Dimension,
    Ingredient,
    Input,
    Item,
    NonProcessingBuilding,
    Output,
    Recipe,
    ResourceNode
)
from satisfactor_py.items import (
    AwesomeSinkPoint,
    Water
)


ALL = None

def get_all() -> list[Building]:
    '''
    Returns a list of all Buildings defined in this module; caches the results for quick access.
    '''

    global ALL
    unbuildable = [Miner, NonProcessingBuilding]
    if ALL is None:
        import inspect
        import sys
        ALL = [ mbr[1] for mbr in inspect.getmembers(sys.modules[__name__], inspect.isclass)
            if issubclass(mbr[1], Building)
            and mbr[1] is not Building
            and mbr[1] not in unbuildable ]
    return ALL


class Assembler(Building):
    '''
    A type of Building which combines two items into a single other item. Has two inputs and one
    output.
    '''

    def __init__(self,
        name: str = 'Assembler',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.PRODUCTION,
            building_type=BuildingType.ASSEMBLER,
            wiki_path='/Assembler',
            image_path='/a/ae/Assembler.png',
            availability=Availability(2, 1),
            base_power_usage=15,
            dimensions=Dimension(
                width=10,
                length=15,
                height=11
            ),
            inputs=[Input(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self
            ) for i in range(2)],
            outputs=[Output(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self
            )],
            **kwargs
        )


class AwesomeShop(NonProcessingBuilding):
    '''
    That AWESOME Shop for spending your tickets
    '''

    def __init__(self,
        name: str = 'AWESOME Shop',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.SPECIAL,
            availability=Availability(2, 4),
            wiki_path='/AWESOME_Shop',
            image_path='/b/b1/AWESOME_Shop.png',
            dimensions=Dimension(
                width=4,
                length=6,
                height=5
            )
        )


class AwesomeSink(Building):
    '''
    An AWESOME Sink
    '''

    def __init__(self,
        name: str = 'AWESOME Sink',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.SPECIAL,
            availability=Availability(2, 4),
            building_type=BuildingType.AWESOME_SINK,
            wiki_path='/AWESOME_Sink',
            image_path='/8/85/AWESOME_Sink.png',
            recipe=None,
            overclockable=False,
            dimensions=Dimension(
                width=16,
                length=13,
                height=24
            ),
            inputs=[Input(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self
            )],
            outputs=[Output(
                conveyance_type=ConveyanceType.AWESOME_SINK,
                attached_to=self
            )]
        )

    def can_process(self) -> bool:
        '''
        Determine if this Sink can process
        '''

        nondisposables = [ingredient for ingredient in self.ingredients if ingredient.item.sink_value == None]
        if len(nondisposables) > 0:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                message=f'Non-disposable items ({nondisposables}) are being sent to an AWESOME Sink.'
            ))
            return False

        return True

    def process(self) -> bool:
        '''
        Convert items into points
        '''

        if not self.can_process():
            return False

        self.outputs[0].ingredients = [
            Ingredient(
                item=AwesomeSinkPoint,
                amount=None,
                rate=sum([ingredient.item.sink_value * ingredient.rate
                    for ingredient in self.ingredients])
            )
        ]
        return True


class BiomassBurner(NonProcessingBuilding):
    '''
    A type of Building where biomass can be burned into power
    '''

    def __init__(self,
        name: str = 'Biomass Burner',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.POWER,
            building_type=BuildingType.BIOMASS_GENERATOR,
            wiki_path='/Biomass_Burner',
            image_path='/2/20/Biomass_Burner.png',
            availability=Availability(0, 6),
            dimensions=Dimension(
                width=8,
                length=8,
                height=7
            ),
            **kwargs
        )


class CoalGenerator(Building):
    '''
    A Building where various coal products can be converted to power
    '''

    def __init__(self,
        name: str = 'Coal Generator',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.POWER,
            building_type=BuildingType.COAL_GENERATOR,
            wiki_path='/Coal_Generator',
            image_path='/b/ba/Coal_Generator.png',
            availability=Availability(3, 1),
            dimensions=Dimension(
                width=10,
                length=26,
                height=36
            ),
            inputs=[
                Input(
                    conveyance_type=ConveyanceType.BELT,
                    attached_to=self
                ),
                Input(
                    conveyance_type=ConveyanceType.PIPE,
                    attached_to=self
                )
            ],
            outputs=[
                Output(
                    conveyance_type=ConveyanceType.POWER_LINE,
                    attached_to=self
                )
            ],
            **kwargs
        )


class Constructor(Building):
    '''
    A type of Building which converts an item of one type into an item of another. Has one input and
    one output.
    '''

    def __init__(self,
        name: str = 'Constructor',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.PRODUCTION,
            building_type=BuildingType.CONSTRUCTOR,
            wiki_path='Constructor',
            image_path='/6/61/Constructor.png',
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


class ConveyorMerger(Building):
    '''
    A building which merges the contents of up to three inputs into a single output.
    '''

    def __init__(self,
        name: str = 'Conveyor Merger',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.LOGISTICS,
            building_type=BuildingType.CONVEYANCE,
            wiki_path='/Conveyor_Merger',
            image_path='/a/aa/Conveyor_Merger.png',
            availability=Availability(1, 2),
            dimensions=Dimension(
                width=4,
                length=4,
                height=3
            ),
            inputs=[Input(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self
            ) for i in range(3)],
            outputs=[Output(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self
            )],
            **kwargs
        )

    def can_process(self, connected_inputs) -> bool:
        success = True
        if len(connected_inputs) == 0:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                'Conveyor merge has no connected inputs'
            ))
            success = False

        if len(connected_inputs) > 3:
            self.add_error(ComponentError(
                ComponentErrorLevel.IMPOSSIBLE,
                'Conveyor merger has more than three connected inputs'
            ))
            success = False

        return success

    def process(self) -> bool:
        '''
        Merges the contents of the inputs onto the output proportionately.
        '''

        connected_inputs = [input for input in self.inputs if input.source]
        if not self.can_process(connected_inputs):
            return False

        self._errors = []

        # Determine the ideal recipe by combining all inputs into one, combining like ingredients
        working_recipe = Recipe(
            building_type=BuildingType.CONVEYANCE,
            produces=self.ingredients
        )

        # Determine if the output can handle the combined rate of input
        total_ingredient_rate = sum([ingredient.rate for ingredient in working_recipe.produces])
        output_rate = self.outputs[0].target.attached_to.rate
        if output_rate < total_ingredient_rate:
            self.add_error(ComponentError(
                ComponentErrorLevel.DEBUG,
                "The merger's combined input rate is greater than its output"
            ))

            # Determine the slowdown ratio and apply it to each ingredient
            slowdown_ratio = output_rate / total_ingredient_rate
            for ingredient in working_recipe.produces:
                ingredient.rate *= slowdown_ratio

        self.outputs[0].ingredients = working_recipe.produces

        return True


class ConveyorSplitter(Building):
    '''
    A building which splits the contents of its single input evenly across up to three outputs.
    '''

    def __init__(self,
        name: str = 'Conveyor Splitter',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.LOGISTICS,
            building_type=BuildingType.CONVEYANCE,
            availability=Availability(1, 2),
            wiki_path='/Conveyor_Splitter',
            image_path='/4/41/Conveyor_Splitter.png',
            dimensions=Dimension(
                width=4,
                length=4,
                height=3  # Should be 2n + 1, but who's counting?
            ),
            inputs=[Input(
                conveyance_type=ConveyanceType.BELT,
                attached_to=self)],
            outputs=[Output(
                    conveyance_type=ConveyanceType.BELT,
                    attached_to=self
                ) for i in range(3)],
            **kwargs
        )

    def can_process(self, connected_outputs: list[Output]) -> bool:
        '''
        Determines if the conditions required for processing are present.
        '''

        success = True
        if len(connected_outputs) == 0:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                'Conveyor splitter has no connected outputs.'
            ))
            success = False

        if len(connected_outputs) > 3:
            self.add_error(ComponentError(
                ComponentErrorLevel.IMPOSSIBLE,
                'Conveyor splitter has more than three connected outputs.'
            ))
            success = False

        return success

    def process(self) -> bool:
        '''
        Splits the contents of a single input across all outputs proportionately.
        '''

        connected_outputs = [output for output in self.outputs if output.target]
        if not self.can_process(connected_outputs):
            return False

        self._errors = []

        # Determine the ideal recipe, if we were to divide the incoming ingredients up across all
        # connected outputs.
        total_ingredient_rate = sum([ingredient.rate for ingredient in self.ingredients])
        output_ratio = 1 / len(connected_outputs)
        ingredient_pct = total_ingredient_rate * output_ratio
        working_recipe = Recipe(
            building_type=BuildingType.CONVEYANCE,
            produces=[Ingredient(
                item=ingredient.item,
                rate=ingredient.rate * output_ratio,
                amount=None
            ) for ingredient in self.ingredients]
        )

        # Determine if any of those connected outputs are too slow to take its portion of items
        slow_outputs = [output for output in connected_outputs
            if output.target.attached_to.rate < ingredient_pct]
        if len(slow_outputs) > 0:
            # Count through all connected outputs
            outputs_remaining = len(connected_outputs)
            for output in connected_outputs:
                outputs_remaining -= 1
                # Determine the total rate of all ingredients in the proportionate recipe
                total_working_recipe_rate = sum(
                    [ingredient.rate for ingredient in working_recipe.produces])

                # For any outputs that are too slow, determine how much of the recipe cannot be
                # passed on to that output.
                if output.target.attached_to.rate < ingredient_pct:
                    slowdown_ratio = output.target.attached_to.rate / total_working_recipe_rate
                    slowed_ingredients = list()
                    for ingredient in working_recipe.produces:
                        slowed_rate = ingredient.rate * slowdown_ratio
                        remainder = ingredient.rate - new_rate
                        slowed_ingredients.append(Ingredient(
                            item=ingredient.item,
                            rate=slowed_rate,
                            amount=None
                        ))
                        if remainder:
                            # If there are leftover items but no leftover outputs, that's an issue
                            if outputs_remaining == 0:
                                self.add_error(ComponentError(
                                    ComponentErrorLevel.WARNING,
                                    "The splitter's incoming rate is more than its total outgoing rate."
                                ))
                                ingredient.rate = remainder
                            # If there are leftover items and still some outputs, update the working
                            # recipe to include a proportion of the leftovers
                            else:
                                ingredient.rate = ingredient.rate + (remainder / outputs_remaining)
                    # Emit a slowed down version of the ingredients to the slow outputs
                    output.ingredients = slowed_ingredients
                else:
                    # Emit the full working production to outputs that are fast enough
                    output.ingredients = working_recipe.produces

        # If all connected outputs can handle the proportionate rate, just pass the ingredients on
        else:
            for output in connected_outputs:
                output.ingredients = working_recipe.produces

        return True


class ConveyorPole(NonProcessingBuilding):
    '''
    A building which supports a conveyor belt
    '''

    def __init__(self,
        name: str = 'Conveyor Pole',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.LOGISTICS,
            building_type=BuildingType.OTHER,
            availability=Availability(0, 4),
            wiki_path='/Conveyor_Pole',
            image_path='/7/73/Conveyor_Pole.png',
            dimensions=Dimension(
                width=2,
                length=1,
                height=1
            ),
            **kwargs
        )


class Foundry(Building):
    '''
    A Foundry Building
    '''

    def __init__(self,
        name: str = 'Foundry',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.PRODUCTION,
            availability=Availability(3, 3),
            wiki_path='/Foundry',
            image_path='/1/19/Foundry.png',
            base_power_usage=16,
            building_type=BuildingType.FOUNDRY,
            dimensions=Dimension(
                width=10,
                length=9,
                height=9
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT
            ) for i in range(2)],
            outputs=[Output(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT
            )],
            **kwargs
        )


class JumpPad(NonProcessingBuilding):
    '''
    A Jump Pad for launching the pilgrim
    '''

    def __init__(self,
        name: str = 'Jump Pad',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.TRANSPORT,
            availability=Availability(2, 3),
            wiki_path='/Jump_Pad',
            image_path='/4/4c/Jump_Pad.png',
            dimensions=Dimension(
                width=6,
                length=6,
                height=6
            ),
            power_connections=1,
            base_power_usage=5
        )


class MAM(NonProcessingBuilding):
    '''
    MAM building for performing field research
    '''

    def __init__(self,
        name: str = 'MAM',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.SPECIAL,
            availability=Availability(1, 3),
            wiki_path='/MAM',
            image_path='/b/b4/MAM.png',
            building_type=BuildingType.WORKSHOP,
            dimensions=Dimension(
                width=5,
                length=9,
                height=6
            ),
            power_connections=0,
            **kwargs
        )


class PersonalStorageBox(NonProcessingBuilding):
    '''
    Personal Storage Box for holding up to 25 items. This is not an automatable building, and has
    neither inputs nor outputs nor power connections.
    '''

    def __init__(self,
        name: str = 'Personal Storage Box',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.ORGANIZATION,
            availability=Availability(1, 3),
            wiki_path='/Personal_Storage_Box',
            image_path='/4/4d/Personal_Storage_Box.png',
            building_type=BuildingType.WORKSHOP,
            dimensions=Dimension(
                width=2,
                length=1,
                height=1
            ),
            power_connections=0,
            **kwargs
        )


class Miner(Building):
    '''
    A type of Building that takes input from a ResourceNode and outputs Items on a Conveyor Belt.
    Typically, you would rather build an implementation of this class instead, like a MinerMk1.
    '''

    def __init__(self,
        image_path: str = '/c/cf/Miner_Mk.1.png',
        wiki_path: str = '/Miner',
        name: str = 'Miner',
        building_category: BuildingCategory = BuildingCategory.PRODUCTION,
        **kwargs
    ):
        super().__init__(
            building_category=building_category,
            building_type=BuildingType.MINER,
            image_path=image_path,
            wiki_path=wiki_path,
            name=name,
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

    def can_process(self) -> bool:
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
        self.outputs[0].ingredients = [self.recipe.produces[0]]

        # Apply resource node purity and clock rate
        self.outputs[0].ingredients[0].rate = \
            self.outputs[0].ingredients[0].rate * self.inputs[0].source.attached_to.purity.value \
                * self.clock_rate


class MinerMk1(Miner):
    '''
    A first-tier Miner
    '''

    def __init__(self,
        name: str = 'Miner Mk.1',
        **kwargs
    ):
        super().__init__(
            name=name,
            availability=Availability(0, 5),
            wiki_path='/Miner#Mk.1-0',
            image_path='/c/cf/Miner_Mk.1.png',
            base_power_usage=5,
            **kwargs
        )


class PipelineJunctionCross(Building):
    '''
    A combination splitter/merger for pipe networks. Has a configurable number of inputs and
    outputs, but the total must be no more than four.
    '''

    def __init__(self,
        inputs: int = 1,
        outputs: int = 1,
        name: str = 'Pipeline Junction Cross',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.LOGISTICS,
            building_type=BuildingType.OTHER,
            wiki_path='/Pipeline_Junction_Cross',
            image_path='/8/8c/Pipeline_Junction_Cross.png',
            availability=Availability(3, 1),
            dimensions=Dimension(
                width=2,
                length=1,
                height=1
            ),
            inputs=[],
            outputs=[],
            **kwargs
        )

        self.set_connections(inputs, outputs)

    def set_connections(self,
        inputs: int = 1,
        outputs: int = 1
    ):
        '''
        Sets this junction's input and output counts. This breaks any connections that may have
        been placed before.
        '''

        if inputs + outputs > 4:
            raise ValueError('Total number of connections exceeds 4')

        if inputs < 1:
            raise ValueError('Cannot have fewer than 1 input')

        if outputs < 0:
            raise ValueError('Cannot have negative number of connections')

        for i in self.inputs:
            if i.source:
                i.source.target = None
            del(i)

        for o in self.outputs:
            if o.target:
                o.target.source = None
            del(o)

        self.inputs = [Input(
            attached_to=self,
            conveyance_type=ConveyanceType.PIPE
        ) for i in range(inputs)]

        self.outputs = [Output(
            attached_to=self,
            conveyance_type=ConveyanceType.PIPE
        ) for o in range(outputs)]

    def can_process(self) -> bool:
        '''
        Determines if the junction can process normally.
        '''

        all_ingredients = []
        for i in self.inputs:
            for ingredient in i.ingredients:
                if ingredient.item not in all_ingredients:
                    all_ingredients.append(ingredient.item)

        ct = len(all_ingredients)
        if ct > 1:
            self.add_error(ComponentError(
                level=ComponentErrorLevel.WARNING,
                message=f'There are {ct} ingredients in this pipeline, but there can be no more '
                    'than 1.'
            ))
            return False

        return True

    def process(self):
        '''
        Splits the incoming fluid proportionately among the outputs.
        '''

        self.clear_errors()
        if not self.can_process():
            return False

        input_item = self.inputs[0].ingredients[0].item
        total_input_rate = 0
        for i in self.inputs:
            total_input_rate += sum([ingredient.rate for ingredient in i.ingredients])
        remaining_rate = total_input_rate

        connected_outputs = [output for output in self.outputs if output.target]
        unfilled_outputs = connected_outputs.copy()
        num_unfilled = len(unfilled_outputs)

        # Set the ingredient for each connected output, but give it no rate
        for output in connected_outputs:
            output.ingredients = [Ingredient(input_item, None, 0)]

        # Repeatedly iterate over outputs that have not reached capacity, evenly distributing the
        # ingredient rate until either there is nothing left to distribute or all connected outputs
        # are full.
        while num_unfilled > 0 and remaining_rate > 0:
            num_unprocessed = num_unfilled
            for output in unfilled_outputs:
                ideal_output_rate = remaining_rate / num_unprocessed
                remaining_capacity = output.target.attached_to.rate - output.ingredients[0].rate
                if remaining_capacity >= ideal_output_rate:
                    output.ingredients[0].rate += ideal_output_rate
                    remaining_rate -= ideal_output_rate
                    num_unprocessed -= 1
                else:
                    output.ingredients[0].rate = output.target.attached_to.rate
                    remaining_rate -= remaining_capacity
                    num_unfilled -= 1
                    num_unprocessed -= 1

            # Reset the counters for the next pass
            unfilled_outputs = [output for output in connected_outputs \
                if output.ingredients[0].rate < output.target.attached_to.rate]
            num_unfilled = len(unfilled_outputs)

        if remaining_rate > 0:
            self.add_error(ComponentError(
                level=ComponentErrorLevel.WARNING,
                message=f'Input rate exceeds output rate by {remaining_rate} per minute'
            ))


class PipelineSupport(NonProcessingBuilding):
    '''
    A building which supports a pipeline
    '''

    def __init__(self,
        name: str = 'Pipeline Support',
        **kwargs
    ):
        super().__init__(
            building_category=BuildingCategory.LOGISTICS,
            building_type=BuildingType.OTHER,
            wiki_path='/Pipeline_Support',
            image_path='/c/c5/Pipeline_Support.png',
            name=name,
            availability=Availability(3, 1),
            dimensions=Dimension(
                width=2,
                length=1,
                height=1
            ),
            **kwargs
        )


class Smelter(Building):
    '''
    A Smelter Building
    '''

    def __init__(self,
        name: str = 'Smelter',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.PRODUCTION,
            building_type=BuildingType.SMELTER,
            availability=Availability(0, 2),
            wiki_path='/Smelter',
            image_path='/4/45/Smelter.png',
            base_power_usage=4,
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

    def __init__(self,
        name: str = 'Space Elevator',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.SPECIAL,
            building_type=BuildingType.SPACE_ELEVATOR,
            availability=Availability(0, 6),
            wiki_path='/Space_Elevator',
            image_path='/a/a4/Space_Elevator.png',
            dimensions=Dimension(
                width=54,
                length=54,
                height=118
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT) for i in range(6)],
            power_connections=0,
            **kwargs
        )


class StackableConveyorPole(NonProcessingBuilding):
    '''
    A stackable conveyor pole for organizing conveyor belts
    '''

    def __init__(self,
        name: str = 'Stackable Conveyor Pole',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.LOGISTICS,
            availability=Availability(2, 5),
            wiki_path='Conveyor_Poles#Stackable-0',
            image_path='/4/49/Stackable_Conveyor_Pole.png',
            dimensions=Dimension(
                width=2,
                length=1,
                height=3
            ),
            power_connections=0,
            **kwargs
        )


class TruckStation(Building):
    '''
    A Truck Station Building
    '''

    def __init__(self,
        name: str = 'Truck Station',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.TRANSPORT,
            building_type=BuildingType.OTHER,
            availability=Availability(3, 2),
            wiki_path='/Truck_Station',
            image_path='/a/a6/Truck_Station.png',
            dimensions=Dimension(
                width=16,
                length=22,
                height=12
            ),
            inputs=[Input(
                attached_to=self,
                conveyance_type=ConveyanceType.BELT) for i in range(3)],
            power_connections=1,
            **kwargs
        )


class UJellyLandingPad(NonProcessingBuilding):
    '''
    A landing pad building
    '''

    def __init__(self,
        name: str = 'U-Jelly Landing Pad',
        **kwargs
    ):
        super().__init__(
            name=name,
            building_category=BuildingCategory.TRANSPORT,
            building_type=BuildingType.OTHER,
            availability=Availability(2, 3),
            wiki_path='/U-Jelly_Landing_Pad',
            image_path='/d/de/U-Jelly_Landing_Pad.png',
            dimensions=Dimension(
                width=10,
                length=11,
                height=5
            ),
            power_connections=1,
            base_power_usage=5,
            **kwargs
        )


class WaterExtractor(Miner):
    '''
    A kind of Miner that produces Water
    '''

    def __init__(self,
        name: str = 'Water Extractor',
        **kwargs
    ):
        '''
        This should be, at a base level, a Miner, but we have to override some special things
        '''
        super().__init__(
            name=name,
            building_category=BuildingCategory.PRODUCTION,
            availability=Availability(3, 1),
            wiki_path='/Water_Extractor',
            image_path='/6/6b/Water_Extractor.png',
            base_power_usage=20,
            **kwargs
        )
        self.building_type = BuildingType.WATER_EXTRACTOR
        self.dimensions = Dimension(
            width=20,
            length=19.5,
            height=26
        )
        self.inputs=[Input(
            conveyance_type=ConveyanceType.RESOURCE_NODE,
            attached_to=self
        )]
        self.outputs=[Output(
            conveyance_type=ConveyanceType.PIPE,
            attached_to=self
        )]
