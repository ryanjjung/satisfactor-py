# Satisfactor-Py

A Python utility for planning factories in the video game [Satisfactory](https://www.satisfactorygame.com/). Much information here is taken from the [Satisfactory Wiki](https://satisfactory.wiki.gg/wiki/Satisfactory_Wiki).


## Setup

The `satisfactor_py` library has no dependencies.

`satisfactor_ui` requires GTK 4.0. Install it and the Python bindings for GObject. On Fedora, you run:

```
dnf install gtk4 python3-gobject
```

## Run Something

Right now, this is mostly CLI-driven and written up in Python code. A GTK-based user interface is in development.

A good place to start is the [screw factory test script](./scripts/screw_factory.py):

```
PYTHONPATH=. ./scripts/screw_factory.py
```


## How To

This library is intended to be used in a similar fashion to the way you play the game itself. You construct buildings, fit them with recipes, and connect them with conveyances. You add these components to a `Factory` object. When you are ready to see if your factory has any problems or inefficiencies, you run that factory's `simulate` function. Any such errors will get attached to the components they apply to, and you can collect and review those afterward.

The `satisfactor_py` module has a number of organizational submodules which contain the various factory components' code representations. The `scripts` directory here contains a number of test scripts that you can review and tinker with.


### Submodules

Here's a listing of each submodule and a summary of what you can find in each.


#### base

Contains the underlying data structures that provide common features to all the higher-order components. This includes the common metadata associated with each component (`base.Base`), the `Enum` objects defining various discrete options such as resource node `Purity` levels and `BuildingType`s, and what `ComponentError`s look like, among other things.

Generally, you do not directly use the contents of the `base` module. It does not make much sense to create a generic `Building`. Instead, you probably want to create a more specific type of building, such as a `Smelter` or a `Constructor`, which you get elsewhere. Peruse the code for full details, but here are a few things of note:


##### base.Base

Every single factory component you build with this library is based on this class, and therefore has a handful of common traits:

- `id`: A randomly generated UUID which uniquely identifies an object
- `name` An arbitrary string used for human readability/reference
- `availability`: An instance of `base.Availability`. A marker of what unlocks the object in the game. This can be at a particular tier and upgrade level, or be unlocked through the MAM or AWESOME Store.
- `wiki_path`: What page of the fan wiki contains information on this object.
- `tags`: An arbitrary dictionary of key/value pairs, used for higher order factory functions.

You can set these values on any object you wish.


##### base.Component

A `Component` is anything that can be constructed as part of a factory, including all buildings (including all conveyor belts), and even the lower-order inputs and outputs that connect them all. Common to all components are the following properties:

- `constructed`: A boolean marker indicating whether the component has been built in a user's game world yet.
- `traversed`: A boolean marker indicating whether the component has been traversed by this library's simulation function. This is useful for determining if you have built something but not connected it, or if there is an upstream factory problem preventing traversal of the component.
- `errors`: A list of `ComponentError`s describing some problem detected with the component.


##### base.Item

An `Item` is almost any resource which can be referred to in the game. This includes anything which you can hold in your inventory, but also buildings and such that can't be held or conveyed. This is because of how recipes work. They at least need to define some item that is produced, so even buildings like Constructors and Conveyor Splitters are "Items" to some extent.

Items have these properties:

- `conveyance_type`: What kind of conveyance this can be moved across. You can't move liquids on a conveyor belt, for example, nor ingots through a pipeline.
- `stack_size`: How many fit in a stack in your inventory. If this is `None` then you can't hold it in your inventory.
- `sink_value`: How many points you get for putting this item into an AWESOME Sink. If this is `None` then you can't sink the item.

They have these functions:

- `stacks(count)`: Returns the number of inventory stacks it would take to hold this many of this item.


##### base.Ingredient

An `Ingredient` is any `Item` in some volume, to be used as input or output of a recipe. If it has an `amount`, that refers to the number of this item used in a single production of a recipe, such as when you craft an item at a craft bench or workshop. If it has a `rate`, that refers to a number of this item consumed or produced per minute, such as when you attach a recipe to a building.


##### base.Recipe

A `Recipe` is two lists of `Ingredient`s defining what items are consumed to produce some output. For example, a smelter may consume iron ore at a rate of 30/m and produce iron ingots at a rate of 30/m. `consumes` and `produces` are the names of these lists of `Ingredients`.

A `Recipe` also has a `base.BuildingType` constraining which buildings can produce a particular recipe. It's worth noting that there's a `BUILD_GUN` building type for recipes that produce buildings.


##### base.Connection, base.Input, base.Output

A `Connection` is any port of transfer between two `Component`s. These are things you don't ordinarily worry about when playing the game because they're built into the buildings. We care about them here for logical reasons.

A `Connection` doesn't have any usefulness without specifying it as an `Input` or an `Output` because flow direction always matters in Satisfactory. As such, navigating the flow of a factory follows this kind of pattern:

- A `Component` has some number of `Output`s.
- Each of those `Output`s has a `target`, which is an `Input` on the next `Component`.
- An `Input` has a `source` `Component` from which it recieves `Ingredient`s.
- All `Connections` regardless of type are `attached_to` a `Component` of some sort.

Thus, you can navigate forward through the buildings of a factory by manipulating this code pattern:

```
component.outputs[0].target.attached_to
```

This starts at one component and traverses its zeroth output to whatever input it's pointed at (its `target`), and then to the building that input is attached to. You can do this in reverse as well:

```
component.inputs[0].source.attached_to
```

`Connection`s also have a list of `ingredients` on them describing what items are passing through them.


##### base.ResourceNode

A `ResourceNode` is a special `Component` with no inputs and one output. It's special because unlike other factory components, it doesn't process a recipe and can only be attached to a miner. This makes for slightly different logic than other components, so it gets its own base class.


##### base.Building

`Building`s are the base class for most constructions in Satisfactory. A `Building` is any component which occupies physical space in the world and which processes a recipe of some kind. Even conveyor belts function as "buildings" in this context.

A `Building` has the following properties:

- `building_type`: The other half of the constraints imposed upon recipes regarding where they can be produced.
- `recipe`: The `Recipe` being processed.
- `overclockable`: Whether or not the building can have its production overclocked.
- `clock_rate`: A modifier adjusting the recipe's consumption and production rates, expressed as a factor (2.5 to represent 250%) of production.
- `standby`: A boolean value representing if the building has been disabled.
- `dimensions`: Physical dimensions (`length`, `width`, and `height`) of the building in meters.
- `inputs`/`outputs`: Lists of the inputs and outputs of the building. Some have more than one.
- `power_connections`: A list of power lines connected to the building.
- `base_power_usage`: When normally clocked (1.0/100%), how much power is consumed to produce the recipe.

A `Building` has the following methods:

- `can_process()`: Checks the building to see if the basic requirements to operate the building are present. Returns `True` if the building should be able to process its recipe. If this returns `False`, factory traversal will not continue beyond this `Building`.
- `process()`: Processes the recipe in the building, passing the recipe's `produces` content on to the outputs.

It also has a `connect` function. This is a convenience function allowing you to connect this building directly to another one. Without this, you must connect buildings at the `Connection` level. Consider:

```
# Build a miner and a smelter and a conveyor belt to connect them
miner = MinerMk1(recipe=IronOreMk1)
conveyor = ConveyorBeltMk1()
smelter = Smelter(recipe=IronIngot)

miner.outputs[0].connect(conveyor.inputs[0])
conveyor.outputs[0].connect(smelter.inputs[0])
```

While not entirely obtuse, it is more detail than I tend to have in mind when working in the game. With `Building.connect` you can specify another building and the type of conveyance that should be built between them. It will automatically build the conveyance and find a suitable connection on the other component to attach to. The above code can be replaced with this segment:

```
miner = MinerMk1(recipe=IronOreMk1)
smelter = Smelter(recipe=IronIngot)
conveyor = miner.connect(smelter, ConveyorBeltMk1)
```

You can also connect in reverse, from an input to an upstream output, with an extra option:

```
conveyor = smelter.connect(miner, ConveyorBeltMk1, connect_output=True)
```


##### base.Conveyance

A `Conveyance` is anything you can build which transports `Item`s from one `Connection` to another without changing the contents being conveyed. When these components' `process` function is run, a special kind of recipe called a `base.ConveyanceRecipe` is created so that it `produces` whatever `Ingredient`s are on the conveyance, limited by the conveyance's rate of transfer. This can be a pipeline or conveyor belt, or represent vehicular transportation.


##### base.Storage

A `Storage` is anything that acts like a conveyance but has additional inventory slots. These don't function much differently from other conveyances, but they do have a `stacks` member showing how many inventory slots are there. This can be useful for answering questions like, "How long do I run my factory to fill up this storage container?"


#### buildings

This submodule contains specific `Building` implementations. Generally, these classes are named after the game objects they represent converted to title case. A few examples:

- `BiomassBurner`
- `Constructor`
- `MAM`
- `SpaceElevator`


#### conveyances

This submodule contains specific `Conveyance` implementations. Generally, these classes are named after the game objects they represent converted to title case. A few examples:

- `ConveyorBeltMk1`
- `ConveyorLiftMk1`


#### items

This submodule contains specific `Item` implementations. Generally, these classes are named after the game objects they represent converted to title case. A few examples:

- `Leaves`
- `AlienProtein`
- `CopperIngot`
- `Screw`


#### recipes

This submodule contains specific `Recipe` implementations. Generally, these classes are named after the recipes they represent in the game converted to title case. A few examples:

- `LimestoneMk1`
- `Cable`
- `Screw`
- `PersonalStorageBox`

`Recipe`s, `Item`s, and `Building`s often have the same name. When importing these, you may find they conflict with each other. Try using prefixed import names to work around this:

```
from satisfactor_py.buildings import Constructor as bConstructor
from satisfactor_py.items import Constructor as iConstructor
from satisfactor_py.recipes import Constructor as rConstructor

rConstructor  # The recipe which produces a constructor
iConstructor  # The item the recipe produces
bConstructor  # The constructor building as it appears in a factory
```


#### storages

This submodule contains specific `Storage` implementations. Generally, these classes are named after the recipes they represent in the game converted to title case. For example:

- `StorageContainer`
- `IndustrialStorageContainer`


### factories

A `factory.Factory` is a collection of `Component`s which ideally work efficiently. This is the higher-level class from which you can act on your components in an organized fashion.

Primarily, a `Factory` has a list of `components`. In the game world, we think of these as having a flow to them. Typically, a factory begins at a `ResourceNode` and flows through a series of `Buildings` which convert the resource into other `Item`s (although you are certainly not limited to this model). Here, though, all components exist as a flat list, whether they're connected to each other or not. Using a `Factory` you can access its components through simple Python list comprehensions.

For example, this returns a list of components which are `Building`s in standby mode:

```
[ component for component in factory.components
    if issubclass(component, Building) and component.standby ]
```


#### Adding components

Call `factory.add(components)` where `components` is either a list of `Component`s or a list of lists of `Component`s. Both forms are supported for convenience. For example, if you want to combine two different factories into one, you might try:

```
big_factory = Factory(name='The Big Factory')
big_factory.add([
    factory1.components,
    factory2.components
])
```

Alternatively, this accomplishes the same thing:

```
big_factory.add(factory1.components)
big_factory.add(factory2.components)
```


#### Accessing components

As shown above, `factory.components` is a list and so you can run Python list comprehensions against it to "query" it, so to speak. Some common queries are exposed as convenience functions or properties:

- `resource_nodes`: A property returning a list of all `ResourceNode` components in the factory.
- `get_buildings_by_type(building_type)`: Given a `base.BuildingType`, returns a list of all buildings of that type in this factory.
- `get_component_by_id(uuid)`: Returns the single factory component identified by the UUID.
- `get_components_by_name(name, fuzzy)`: Returns a list of components in the factory whose name match the provied text. This defaults to an exact string match. Set `fuzzy=True` to enable substring matching.
- `get_components_by_tag(key, value, fuzzy)`: Returns a list of components with tags where the value of the provided key matches the provided value. If no `value` is provided, this looks for components with the matching key set to anything at all. If a `value` is provided, this looks for an exact key/value match. If `fuzzy=True`, enables substring matching on the value only; the key name must still match completely. This enables you to arbitrarily tag components and then retrieve them by those tags later.


#### Traversing factories

The logic for factory traversal involves finding a starting point and iteratively determining the next component to move to. Cases where factories have divergent paths (such as when they have multiple resource nodes, or when a conveyor splitter is used) are handled with threading, allowing the logic to traverse these divergent paths simultaneously.

At the core of this is a factory's `traverse` function. It takes two arguments:

- `cursor`: The `Component` from which you want to start traversing. This can be any component at all.
- `func`: An arbitrary function. At each traversal step, this function will be called, and the `Component` currently being iterated will be passed in like so: `func(cursor)`. This allows you to write arbitrary code to act on your entire factory.

A few common traversal needs can be solved through a few other functions found here:

- `traverse_all(func)`: Traverse the factory beginning at its resource nodes, running the arbitrary `func` against each `Component`.
- `simulate()`: Traverse the factory beginning at its resource nodes. Run each component's `process` function, causing front-to-back simulation of the entire factory as it is designed. If any `ComponentError`s occur, they can be collected after the fact with comprehensions:

```
factory.simulate()
errors = {
    component.name: [error.to_dict() for error in component.errors]
    for component in factory.components
    if len(component.errors) > 0
}
```

- `drain()`: Traverse the factory beginning at its resource nodes, clearing out all of the working variables used for simulation, such as ingredients going through the connections.
- `purge()`: This function doesn't actually traverse the factory. It acts on all components, even if they're not connected or otherwise traversible in the factory, and clears out all of the simulation variables. When resetting a factory, this is the preferred method of doing it, as it is a much more direct and complete clearing out of the memory state.
- `debug()`: This function traverses the factory. At each component, it outputs some identifying information about the component and what stage of processing it's at (before or after processing it), then stops at a Python debugger prompt. From here, you can use [`pdb`](https://docs.python.org/3/library/pdb.html) as usual to debug the state of each component.


#### Reviewing errors

After simulating a factory, you can coalesce its errors easily through two convenience functions:

`Factory.get_errors()` produces a dict where they keys are UUIDs mapping to the `id` of a component in the factory. The values are lists of all `base.ComponentError`s associated with that component.

If you need a version of this which is better suited for textual output, use `Factory.get_errors_as_dict()` instead. Instead of the error objects themselves, it gives dicts containing the name of component, the type of building, and dictionary representations of the errors.


### patterns

This submodule contains functions which produce factories following certain established patterns. Right now this is mostly used for testing things, but could be used in the future for stamping out efficient factories from templates.

For instance, if you run this...

```
from satisfactor_py.base import Purity
from satisfactor_py.patterns import tier_0_screw_factory

factory = tier_0_screw_factory(Purity.NORMAL)
```

...the `factory` object will be a series of these interconnected components:

- A normal-purity iron ore resource node contributing to...
- A Miner Mk.1 outputting iron ore into...
- A Smelter turning that into iron ingots and sending it to...
- A Constructor turning ingots into iron rods and passing those on to...
- Another Constructor turning rods into screws, then finally sending those into...
- A storage container.

You can check that this works:

```
factory.simulate()
storage = factory.components[-1]
for ing in storage.ingredients:
    print(json.dumps(ing.to_dict(), indent=2))
```

This ultimately produces output like this, showing that the storage container at the end of the factory is recieving screws at a rate of 40 per minute:

```
{
  "item": {
    "id": "a661175a-49aa-418b-9cf6-4beb8f531341",
    "name": "Screw",
    "availability": {
      "tier": 0,
      "upgrade": 3
    },
    "wiki_path": "/Screw",
    "wiki_url": "https://satisfactory.wiki.gg/wiki/Screw",
    "tags": {},
    "conveyance_type": "BELT",
    "stack_size": 500,
    "sink_value": 2
  },
  "amount": null,
  "rate": 40.0
}
```

If you print out the result of `factory.get_errors_as_dict()`, you can even see some warnings:

```
Errors: {
  "59c7ec9a-1a08-4c2e-a888-de1caa1fbba1": {
    "component": "Storage Merger #1",
    "building_type": "Conveyance",
    "errors": [
      {
        "level": "DEBUG",
        "message": "The merger's combined input rate is greater than its output"
      }
    ]
  },
  "8433771a-a467-4d48-88e0-f19306040ba6": {
    "component": "Storage Merger #2",
    "building_type": "Conveyance",
    "errors": [
      {
        "level": "DEBUG",
        "message": "The merger's combined input rate is greater than its output"
      }
    ]
  },
  "d03fc620-95ff-465b-ac1d-500216d0e313": {
    "component": "Storage Merger #3",
    "building_type": "Conveyance",
    "errors": [
      {
        "level": "DEBUG",
        "message": "The merger's combined input rate is greater than its output"
      }
    ]
  }
}
```

Because this is a factory that you can build at Tier 0, these inefficiencies are to be expected.
