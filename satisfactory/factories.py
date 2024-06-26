import json
import pdb
import pickle

from threading import Thread
from typing import Callable
from satisfactory.base import (
    Availability,
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
        - availability: A base.Availability describing the unlock level of the factory
    '''

    def __init__(self,
        components: list[Component] = list(),
        availability: Availability = Availability(0, 1),
        **kwargs
    ):
        super().__init__(**kwargs)
        self._components = components
        self._errors = list()
        self.availability = availability

    def to_dict(self) -> dict:
        '''
        Returns a dict representation of the object
        '''

        base = super().to_dict()
        base.update({
            'components': [component.to_dict() for component in self.components]
        })
        return base

    @property
    def components(self):
        '''
        This is a read-only property so we can use Python's type hinting in the `add` function to
        ensure we're only allowing Component types into the factory.
        '''

        return self._components

    @property
    def resource_nodes(self) -> list[ResourceNode]:
        '''
        Quick access to all ResourceNodes and InfiniteSupplyNodes in the factory.
        '''

        return [component for component in self._components
                if isinstance(component, ResourceNode)]

    def add(self,
        components: list[Component] | list[list[Component]]
    ):
        '''
        Add the provided components to the factory.

            - components: Either a list of Components or a list of lists of Components, allowing
                multiple factories to be merged conveniently.
        '''

        for component in components:
            if issubclass(type(component), Component):
                component.factory = self
                self._components.append(component)
            if type(component) == list:
                for comp in component:
                    comp.factory = self
                    self._components.append(comp)

    def remove(self,
        component_id: str
    ):
        '''
        Removes the component with the given unique ID from the factory.
        '''

        component = None
        for component in self.components:
            if component.id == component_id:
                self.components.remove(component)
                break

    def add_error(self,
        error: ComponentError
    ):
        '''
        Simple helper to ensure that errors are of the right type
        '''

        self._errors.append(error)

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

    def get_available_connections(self,
        compatible_with: Connection,
        ignore_conveyances: bool = True,
    ):
        '''
        Returns a dictionary containing information about connections which are candidates for
        connecting with the given connection. That is, they have the same conveyance type and are
        the opposite kind of Connection (Inputs are compatible with Outputs, for example, or vice
        versa). That dictionary structure looks like this:

            {
                "<component_id>": [{
                    'component': <Component>,
                    'connection': <Input|Output>,
                    'connection_index': <int>
                }]
            }

        The 'connection' is the Input or Output that is available. The 'connection_index' represents
        the index in the remote component's appropriate list of inputs or outputs where this
        connection can be found. The 'component' is the component the available connection is
        attached to.

        Arguments:

            - compatible_with: An Input or Output for which we are seeking a compatible connection.
            - ignore_conveyances: In the factory designer, we do not manipulate conveyances
                ourselves, so we are not usually interested in including them in this function call.
        '''

        source_component = compatible_with.attached_to
        target_type = Input if isinstance(compatible_with, Output) else Output

        available_connections = {}
        # Go through every component in the factory
        for component in self.components:

            # Ignore the component we've been asked to find compatible connections for
            if component == source_component:
                continue

            # Ignore conveyances if we've been asked to
            if issubclass(component.__class__, Conveyance):
                continue

            # Go through the right kind of connections
            connections = component.inputs if target_type is Input else component.outputs
            connection_objs = []
            for i in range(len(connections)):
                # Ignore connections with incompatible conveyance types
                if connections[i].conveyance_type != compatible_with.conveyance_type:
                    continue

                # Ignore connections that are already connected
                if connections[i].remote is not None:
                    continue

                # If it's passed through the filters, add it to the list
                connection_objs.append({
                    'component': component,
                    'connection': connections[i],
                    'connection_index': i,
                })

            # Update the main dict
            if len(connection_objs) > 0:
                available_connections[component.id] = connection_objs
        return available_connections

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

    @staticmethod
    def load(filename: str):
        '''
        Static method which loads a factory from a file previously saved by this library.

            - filename: The path to the factory file
        '''

        with open(filename, 'rb') as fh:
            factory = pickle.load(fh)

        return factory

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

    def save(self, filename: str):
        '''
        Serializes the factory using pickle and saves that content to the specified file
        '''

        with open(filename, 'wb') as fh:
            pickle.dump(self, fh, pickle.HIGHEST_PROTOCOL)

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


def drain_component(component):
    '''
    Clear all ingredients in a component, and clear its errors
    '''

    component.clear_errors()
    component.traversed = False
    if hasattr(component, 'ingredients'):
        component.ingredients.clear()

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

