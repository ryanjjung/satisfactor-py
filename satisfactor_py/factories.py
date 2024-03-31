import json
import pdb

from threading import Thread
from typing import Callable
from satisfactor_py.base import (
    Base,
    Building,
    BuildingType,
    Component,
    ComponentError,
    ComponentErrorLevel,
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
        tier: int = 0,
        upgrade: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._components = components
        self._errors = list()
        self.tier = tier
        self.upgrade = upgrade

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
        components: list[Component] | list[list[Component]]
    ):
        for component in components:
            if issubclass(type(component), Component):
                component.factory = self
                self._components.append(component)
            if type(component) == list:
                for comp in component:
                    comp.factory = self
                    self._components.append(comp)

    def add_error(self,
        error: ComponentError
    ):
        '''
        Simple helper to ensure that errors are of the right type
        '''

        self._errors.append(error)

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

    def get_errors(self) -> dict[str, list[ComponentError]]:
        '''
        Returns a dictionary where the keys are UUIDs which correspond to components in this factory
        and the values are lists of `base.ComponentError`s occuring on those components. Use this
        when programmatically reviewing errors in the factory.
        '''

        return {
            component.id: component.errors
            for component in self.components
            if len(component.errors) > 0
        }

    def get_errors_as_dict(self) -> dict[str, dict]:
        '''
        Returns a dictionary where the keys are UUIDs which correspond to components in this factory
        and where the values are dictionary representations of `base.ComponentError` objects. Use
        this when preparing textual output about errors in the factory.
        '''

        return {
            component.id: {
                'component': component.name,
                'building_type': component.building_type.name.title(),
                'errors': [ error.to_dict() for error in component.errors ]
            } for component in self.components if len(component.errors) > 0
        }


    def traverse_all(self,
        func: Callable
    ):
        '''
        Initiates factory traversal beginning at its ResourceNodes, running the `func` function on
        each Component and Connection in the flow.

            - func: A function to run on each Component and Connection in the flow
        '''

        self.traverse_multi(self.resource_nodes, func)

    def traverse_multi(self,
        components: list[Component],
        func: Callable
    ):
        '''
        Initiates factory traversal beginning with a list of arbitrary components, running the
        `func` function on each Component and Connection in the flow.

            - components: A list of Components to begin traversal at
            - func: A function to run on each component
        '''

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

        cursor.traversed = True

        # Run the function where the cursor is
        func(cursor)

        # Advance the cursor
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
            elif len(cursor.outputs) == 1:
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
        self.errors = list()

    def purge(self):
        '''
        Clears ingredients out of all components in the factory, even if they're not traversible.
        '''

        for component in self.components:
            component.clear_errors()
            component.ingredients = list()
            if isinstance(component, Building):
                for input in component.inputs:
                    input.ingredients = list()
                for output in component.outputs:
                    output.ingredients = list()
            if isinstance(component, Conveyance):
                component.recipe = None

    def simulate(self):
        '''
        Steps through each connection in the factory, simulating each building.
        '''
        self.traverse_all(simulate_component)

        excluded = [component for component in self.components if not component.traversed]
        if len(excluded) > 0:
            self.add_error(ComponentError(
                ComponentErrorLevel.WARNING,
                f'Some components were not traversed: {excluded}'
            ))

    def simulate_multi(self,
        components: list[Component]
    ):
        '''
        Runs factory simulation beginning at the specified list of components.
        '''
        self.traverse_multi(components, simulate_component)

def drain_component(component):
    '''
    Clear all ingredients in a component, and clear its errors
    '''

    component.clear_errors()
    component.traversed = False
    if hasattr(component, 'ingredients'):
        component.ingredients.clear()
    return

def simulate_component(component):
    '''
    Simulate the component, determining if it can process, and what the contents of its outputs are
    '''

    print(f'Simulating component {component}')
    component.process()

def debug_component(component):
    '''
    Break with a debugger prompt before and after processing each component
    '''

    # Threading makes this ugly. Print some output every time so the user understands what they're
    # looking at.
    this = component
    print(f'\n[DEBUG] ----- Inspecting component BEFORE simulation "{this.name or this.id}" ({type(this).__name__})')
    pdb.set_trace()
    this.process()
    print(f'\n[DEBUG] ----- Inspecting component AFTER simulation "{this.name or this.id}" ({type(this).__name__})')
    pdb.set_trace()

