import json
import pdb

from threading import Thread
from typing import Callable
from satisfactor_py.base import (
    Base,
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

class Factory(Base):
    '''
    A Factory is a collection of interconnected Components.

        - components: A list of Components in the factory.
    '''

    def __init__(self,
        components: list[Component] = list(),
        **kwargs
    ):
        super().__init__(**kwargs)
        self._components = components

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'components': [component.to_dict() for component in self.components]
        })
        return base

    # By making this a read-only property, we can use Python's type hinting in the `add` function to
    # ensure we're only allowing Component types into the factory.
    @property
    def components(self):
        return self._components

    @property
    def resource_nodes(self) -> list[Component]:
        '''
        Quick access to all ResourceNodes in the factory.
        '''

        return [component for component in self._components
                if isinstance(component, ResourceNode)]

    def add(self,
        components: list[Component]
    ):
        for component in components:
            component.factory = self
        self._components.extend(components)

    def get_buildings_by_type(self,
        building_type: BuildingType
    ) -> list[Building]:
        '''
        Returns a list of all Buildings in the factory of a particular type.
        '''

        return [component for component in self._components
                if isinstance(component, Building)
                and component.building_type == building_type]

    def get_component_by_id(self,
        id: str
    ) -> Component:
        '''
        Returns a specific single Component, given its unique ID.
        '''

        for component in self._components:
            if component.id == id:
                return component
        return None

    def get_components_by_name(self,
        name: str,
        fuzzy: bool = False
    ) -> list[Component]:
        '''
        Returns a list of Components which match the name.

            - name: The text to search for
            - fuzzy: When True, returns names which are partial but not necessarily exact matches.
        '''

        components = list()
        for component in self._components:
            if fuzzy:
                if name in component.name:
                    components.append(component)
            else:
                if component.name == name:
                    components.append(component)
        return components

    def get_components_by_tag(self,
        key: str,
        value: str | None = None,
        fuzzy: bool = True
    ) -> list[Component]:
        '''
        Returns a list of Components with tags matching the specified inputs. If `value` is None, we
        match any component containing the tag matching the `key`.
        '''

        matches = list()

        for component in self.components:
            for tagKey, tagValue in component.tags.items():
                if key == tagKey:
                    if value is None:
                        matches.append(component)
                    else:
                        if fuzzy:
                            if value in tagValue:
                                matches.append(component)
                        else:
                            if value == tagValue:
                                matches.append(component)

        return matches


    def traverse_all(self,
        func: Callable
    ):
        '''
        Initiates factory traversal beginning at its ResourceNodes, running the `func` function on
        each Component and Connection in the flow.

            - func: A function to run on each Component and Connection in the flow
        '''

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

            - cursor: The Component to start traversing the factory from
            - func: A function to run on each Component and Connection in the flow
        '''

        # Run the function where the cursor is
        func(cursor)

        # Advance the cursor
        # import pdb; pdb.set_trace()
        if isinstance(cursor, Input):
            self.traverse(cursor.attached_to, func)
        elif isinstance(cursor, Output):
            if cursor.target:
                self.traverse(cursor.target, func)
        elif isinstance(cursor, ResourceNode):
            self.traverse(cursor.outputs[0], func)
        elif isinstance(cursor, Building):
            # If the cursor is on a building, the next step depends on how many outputs there are
            # If the building has no outputs (Awesome Sink), we can traverse no farther.
            if len(cursor.outputs) < 1:
                return
            # If there is only one output, traverse along it
            elif len(cursor.outputs) == 1 and cursor.recipe:
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

    def debug(self):
        '''
        Steps through each component, breaking with a debugger
        '''

        self.traverse_all(debug_component)

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

    component.process()

def debug_component(component):
    '''
    Break with a debugger prompt before and after processing each component
    '''

    # Threading makes this ugly. Print some output every time so the user understands what they're
    # looking at.
    print(f'\n[DEBUG] ----- Inspecting component BEFORE simulation "{component.name or component.id}" ({type(component).__name__})')
    x = component
    pdb.set_trace()
    component.process()
    print(f'\n[DEBUG] ----- Inspecting component AFTER simulation "{component.name or component.id}" ({type(component).__name__})')
    pdb.set_trace()

