from threading import Thread
from typing import Callable
from satisfactor_py.base import (
    Building,
    BuildingType,
    Component,
    Connection,
    Conveyance,
    ConveyanceRecipe,
    Input,
    Output,
    ResourceNode
)

class Factory(Component):
    '''
    A Factory is a collection of interconnected Components. It is itself a Component, meaning that
    Factories can be nested.
    '''

    def __init__(self,
        components: list[Component] = list(),
        **kwargs
    ):
        super().__init__(**kwargs)
        self._components = components

    # By making this a read-only property, we can use Python's type hinting in the `add` function to
    # ensure we're only allowing Component types into the factory.
    @property
    def components(self):
        return self._components

    @property
    def resource_nodes(self):
        return [component for component in self._components
                if isinstance(component, ResourceNode)]

    def add(self,
        components: list[Component]
    ):
        self._components.extend(components)

    def get_buildings_by_type(self,
        building_type: BuildingType
    ) -> list[Building]:
        return [component for component in self._components
                if isinstance(component, Building)
                and component.building_type == building_type]

    def get_component_by_id(self,
        id: str
    ) -> Component:
        for component in self._components:
            if component.id == id:
                return component
        return None

    def get_components_by_name(self,
        name: str
    ) -> list[Component]:
        components = list()
        for component in self._components:
            if component.name == name:
                components.append(component)
        return components

    def drain(self):
        '''
        Steps through each connection in the factory, clearing all ingredients out of each one. This
        process begins with any resource nodes in the factory.
        '''
        self.traverse_all(drain_component)

    def simulate(self):
        '''
        Steps through each connection in the factory, simulating each building.
        '''
        self.traverse_all(simulate_component)

    def traverse_all(self,
        func: Callable
    ):
        components = self.resource_nodes

        # Start up traversal threads.
        threads = list()
        for component in components:
            threads.append(Thread(target=self.traverse, args=[component, func]))
        for thread in threads:
            thread.start()
            thread.join()

    def traverse(self,
        cursor: Component,
        func: Callable
    ):
        '''
        Traverses factory pathways beginning at the given Component, passing each Component into the
        given function.
        '''

        # Run the function where the cursor is
        func(cursor)

        # Advance the cursor
        if isinstance(cursor, Input):
            self.traverse(cursor.attached_to, func)
        elif isinstance(cursor, Output):
            if cursor.target:
                # Conveyances need to have their recipes set based on their inputs
                if isinstance(cursor.target.attached_to, Conveyance):
                    cursor.target.recipe = ConveyanceRecipe(cursor.ingredients)
                cursor.target.ingredients = cursor.ingredients
                self.traverse(cursor.target, func)
        elif isinstance(cursor, ResourceNode):
            self.traverse(cursor.outputs[0], func)
        elif isinstance(cursor, Building):
            # If the cursor is on a building, the next step depends on how many outputs there are
            # If the building has no outputs (Awesome Sink), we can traverse no farther.
            if len(cursor.outputs) < 1:
                return
            # If there is only one output, traverse along it
            elif len(cursor.outputs) == 1:
                cursor.outputs[0].ingredients = cursor.recipe.produces
                self.traverse(cursor.outputs[0], func)
            # If there are multiple outputs, we must split into threads to traverse them
            elif len(cursor.outputs) > 1:
                threads = list()
                for output in cursor.outputs:
                    threads.append(Thread(target=self.traverse, args=[output, func]))
                for thread in threads:
                    thread.start()
                    thread.join()


def drain_component(component):
    '''
    Clear all ingredients in a component
    '''

    if isinstance(component, Connection):
        component.ingredients = list()
    return

def simulate_component(component):
    '''
    Simulate the component, determining if it can process, and what the contents of its outputs are
    '''

    if isinstance(component, Building):
        component.process()
    return
