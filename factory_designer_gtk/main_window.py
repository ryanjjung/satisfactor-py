import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject
from gi.repository.GdkPixbuf import Pixbuf
from pathlib import Path
from satisfactory.base import (
    Availability,
    Building,
    BuildingCategory,
    BuildingType,
    Conveyance,
    InfiniteSupplyNode,
    Purity,
    ResourceNode,
    Storage,
)
from satisfactory.buildings import (
    get_all as get_all_buildings,
    ConveyorMerger,
    ConveyorSplitter,
    Miner,
)
from satisfactory.conveyances import get_all as get_all_conveyances
from satisfactory.factories import Factory
from satisfactory.items import (
    get_all as get_all_items,
    IronOre,
)
from satisfactory.recipes import get_all as get_all_recipes
from satisfactory.storages import get_all as get_all_storages
from factory_designer_gtk.dialogs import (
    ConfirmOrCancelWindow,
    ConnectionManagementWindow,
    ConnectionManagementWindowResponse,
)
from factory_designer_gtk.drawing import Blueprint
from factory_designer_gtk.geometry import Coordinate2D
from factory_designer_gtk.widgets import (
    FactoryDesignerWidget,
    InteractionMode,
    TaggableButton,
    TaggableEntryBuffer,
    TagBox,
)


ALL_BUILDINGS = None
MAIN_WINDOW_DEFAULT_WIDTH = 1920
MAIN_WINDOW_DEFAULT_HEIGHT = 1080
MAIN_WINDOW_TITLE_BASE = 'Satisfactory Designer'


class MainWindow(Gtk.ApplicationWindow):
    '''
    The main factory designer window.

      - filename: A file created by satisfactory.factories.Factory.save which the window is to be
            initialized with.
    '''

    def __init__(self,
        *args,
        filename: str = None,
        width: int = MAIN_WINDOW_DEFAULT_WIDTH,
        height: int = MAIN_WINDOW_DEFAULT_HEIGHT,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.blueprint = None
        self.blueprintFile = filename
        self.buildings = []
        self.unsaved_changes = False

        self.filters = {
            'availability': True,
            'building_category': False,
            'name': False
        }

        self.set_default_size(width, height)
        self.__build_ui_helpers()
        self.__build_window()

        if filename:
            self.load_blueprint(filename)

        self.update_window()


    # Common Functions

    def block_all_signals(self):
        '''
        Places a block on all signal handlers, preventing them from emitting events until you run
        unblock_all_signals. For this to work, any signals you need to block need to be registered
        to `self.windowSignals`.
        '''

        for handler in self.windowSignals:
            GObject.signal_handler_block(handler[0], handler[1])

    def confirm_discard(self, callback):
        '''
        Presents a GTKDialog asking the user if it's okay to discard unsaved changes.
        '''

        dlgDiscardChanges = ConfirmOrCancelWindow(self,
            'Discard Unsaved Changes?',
            'You have unsaved changes. Proceed?',
            callback)
        dlgDiscardChanges.present()

    @staticmethod
    def get_building_options():
        '''
        Returns a list of all buildings the library is aware of; caches the result for quick access.
        '''

        global ALL_BUILDINGS
        if ALL_BUILDINGS is None:
            ALL_BUILDINGS = [ ResourceNode(), InfiniteSupplyNode() ]
            for bldg in get_all_buildings():
                ALL_BUILDINGS.append(bldg())
            #ALL_BUILDINGS.extend([ bldg() for bldg in get_all_buildings()])
            ALL_BUILDINGS.extend([ bldg() for bldg in get_all_storages()])
        return ALL_BUILDINGS

    def load_blueprint(self,
        filename: str
    ):
        '''
        Opens a factory blueprint file for use with the application and triggers a UI update.
        '''

        try:
            # Load the blueprint and store it in the class as separate actions,
            # resulting in no change if an exception is thrown at load time.
            loadedBlueprint = Blueprint.load(filename)
            self.blueprintFile = filename
            self.blueprint = loadedBlueprint
            self.blueprint.selected = None
            self.factoryDesigner.blueprint = self.blueprint
            self.unsaved_changes = False
            self.update_window()
        except IOError as ex:
            dlgError = Gtk.AlertDialog()
            dlgError.set_modal(True)
            dlgError.set_message(
                f'An error occurred when loading a blueprint from file {filename}\n  {ex}')
            dlgError.show(self)

    def set_tier_and_upgrade(self,
        tier: int = None,
        upgrade: int = None
    ):
        '''
        Sets the active values in the combo boxes for tier and upgrade

            - tier: The tier to set the factory unlock level to
            - upgrade: The upgrade level to set in the factory
        '''

        if self.blueprint:
            self.block_all_signals()
            # Update the factory model first
            if tier is not None:
                self.blueprint.factory.availability.tier = tier
            if upgrade is not None:
                self.blueprint.factory.availability.upgrade = upgrade

            # Set the tier value in the combo box
            self.cboTier.set_active(self.blueprint.factory.availability.tier)

            # Populate the appropriate upgrade values
            self.cboUpgrade.remove_all()
            for upgrade in Availability.get_upgrade_strings(self.blueprint.factory.availability.tier):
                self.cboUpgrade.append(upgrade, upgrade)
            self.cboUpgrade.set_active(self.blueprint.factory.availability.upgrade - 1)
            self.unblock_all_signals()

    def set_window_title(self):
        '''
        Update the window's title appropriately
        '''

        title_prefix = f'{"*" if self.unsaved_changes else ""}'
        title_suffix = f' ({self.blueprintFile.split('/')[-1]})' if self.blueprintFile else ''
        self.set_title(f'{title_prefix}{MAIN_WINDOW_TITLE_BASE}{title_suffix}')

    def unblock_all_signals(self):
        '''
        Removes a block from all signal handlers, restoring their ability to emit signals. These
        signals were likely placed by block_all_signals. For this to work, any signal you wish to
        unblock must be registered with `self.windowSignals`.
        '''

        for handler in self.windowSignals:
            GObject.signal_handler_unblock(handler[0], handler[1])

    def update_buildings_list(self):
        '''
        Updates the list of buildings in the left panel, taking into account all filters.
        '''

        if self.blueprint:
            # Determine the available buildings
            all_buildings = MainWindow.get_building_options()
            if self.filters['availability']:
                avail_buildings = []
                for building in all_buildings:
                    if self.blueprint.factory.availability.tier > building.availability.tier:
                        avail_buildings.append(building)
                    elif self.blueprint.factory.availability.tier == building.availability.tier:
                        if self.blueprint.factory.availability.upgrade >= building.availability.upgrade:
                            avail_buildings.append(building)
            else:
                avail_buildings = all_buildings

            # Filter out anything that doesn't match the building category
            if self.filters['building_category'] and self.cboBuildingCategory.get_active() != -1:
                avail_buildings = [ building for building in avail_buildings
                    if building.building_category.name == self.cboBuildingCategory.get_active_text().upper() ]

            # Filter out anything that doesn't match the name
            if self.filters['name'] and self.entryNameFilter.get_buffer().get_text() != '':
                avail_buildings = [ building for building in avail_buildings
                    if self.entryNameFilter.get_buffer().get_text().lower() in building.name.lower() ]

            # Sort the list alphabetically
            avail_buildings = sorted(avail_buildings, key=lambda x: x.name)

            # Convert the list to a ListStore, pulling in images where possible. At the same time,
            # update the window's list of buildings to make this data accessible later.
            self.buildings = []
            listStore = Gtk.ListStore(Pixbuf, str)
            for building in avail_buildings:
                listStore.append((
                    self.pixelBuffers['building_options'][building.__class__.__name__],
                    building.name))
                self.buildings.append(building.__class__)
            self.lstBuildings = listStore
            self.icovwBuildings.set_model(self.lstBuildings)
            self.icovwBuildings.set_pixbuf_column(0)
            self.icovwBuildings.set_text_column(1)

    def update_component_context(self,
        skip: list = []
    ):
        '''
        Populates the widgets in the component context panel which display read-only information
        about the state of the selected component.
        '''

        if self.blueprint and self.blueprint.selected:
            # This makes the rest of this code read better
            c = self.blueprint.selected

            # Update the building type
            if isinstance(c, Building):
                self.lblComponentBuildingType.set_text(
                    f'Building type: {c.building_type.name.title()}')
                self.lblComponentBuildingType.set_visible(True)
            else:
                self.lblComponentBuildingType.set_visible(False)

            # Update the availability display
            self.lblComponentAvailability.set_text(
                f'Available at Tier {c.availability.tier}, Upgrade {c.availability.upgrade}')

            # Update the dimensions
            if hasattr(c, 'dimensions'):
                self.lblComponentDimensions.set_text(
                    f'Dimensions: {c.dimensions.width} x {c.dimensions.length} x {c.dimensions.height}')
                self.lblComponentDimensions.set_visible(True)
            else:
                self.lblComponentDimensions.set_visible(False)

            # Update the base power usage
            if hasattr(c, 'base_power_usage'):
                self.lblComponentBasePowerUsage.set_text(
                    f'Base Power Usage: {c.base_power_usage}W')
                self.lblComponentBasePowerUsage.set_visible(True)
            else:
                self.lblComponentBasePowerUsage.set_visible(False)

            # Update the links
            self.linkWiki.set_uri(c.wiki_url)
            self.linkImage.set_uri(c.image_url)

            # Update the component name
            if self.entryComponentName not in skip:
                self.entryComponentName.get_buffer().set_text(c.name, -1)

            # Update the clock rate, but not everything has one
            if isinstance(c, Building) \
                and not isinstance(c, Conveyance) \
                and not isinstance(c, ConveyorMerger) \
                and not isinstance(c, ConveyorSplitter):
                    if self.spinComponentClockRate not in skip:
                        self.spinComponentClockRate.set_value(c.clock_rate)
                    self.boxComponentClockRate.set_visible(True)
            else:
                self.boxComponentClockRate.set_visible(False)

            # Update booleans
            self.chkComponentConstructed.set_active(c.constructed)
            if isinstance(c, Building):
                self.chkComponentStandby.set_active(c.standby)
                self.chkComponentStandby.set_visible(True)
            else:
                self.chkComponentStandby.set_visible(False)

            # Update available and selected recipes
            if isinstance(c, Building) \
                and not isinstance(c, Conveyance) \
                and not isinstance(c, Storage):
                    # Always filter compatible recipes by building type
                    compatible_recipes = [ (recipe_name, recipe) for recipe_name, recipe in get_all_recipes()
                        if recipe.building_type == c.building_type]
                    # If the user has availability filtering enabled, filter by that as well
                    available_recipes = []
                    if self.chkAvailability.get_active():
                        for _, recipe in compatible_recipes:
                            if (recipe.availability.tier is None
                                or recipe.availability.tier < self.blueprint.factory.availability.tier):
                                    available_recipes.append(recipe)
                            elif recipe.availability.tier == self.blueprint.factory.availability.tier:
                                if recipe.availability.upgrade is None \
                                    or recipe.availability.upgrade <= self.blueprint.factory.availability.upgrade:
                                        available_recipes.append(recipe)
                    else:
                        available_recipes = compatible_recipes

                    compatible_recipes.sort(key=lambda x: x[0])

                    # Recreate the contents of the recipe selector
                    if self.cboComponentSelectedRecipe not in skip:
                        self.cboComponentSelectedRecipe.remove_all()
                        for recipe_name, recipe in compatible_recipes:
                            self.cboComponentSelectedRecipe.append(recipe_name, recipe.name)
                        if c.recipe:
                            current_recipe = c.recipe.programmatic_name()
                            # Determine index of current recipe and set the recipe selector to that
                            current_recipe_id = None
                            for i in range(len(compatible_recipes)):
                                if compatible_recipes[i][0] == current_recipe:
                                    current_recipe_id = i
                                    break
                            if current_recipe is not None:
                                self.cboComponentSelectedRecipe.set_active(current_recipe_id)

                    if c.recipe:
                        consumes_store = Gtk.ListStore(Pixbuf, str)
                        produces_store = Gtk.ListStore(Pixbuf, str)
                        if c.recipe.consumes:
                            for ingredient in c.recipe.consumes:
                                ing_rate = ingredient.rate * c.clock_rate
                                consumes_store.append((
                                    self.pixelBuffers['items'][ingredient.item.programmatic_name()],
                                    f'{ing_rate}x {ingredient.item.name} /m'))
                        if c.recipe.produces:
                            for ingredient in c.recipe.produces:
                                if isinstance(c, Miner):
                                    if c.inputs[0].source and c.inputs[0].source.attached_to:
                                        ing_rate = ingredient.rate * c.inputs[0].source.attached_to.purity.value
                                    else:
                                        ing_rate = ingredient.rate
                                else:
                                    ing_rate = ingredient.rate
                                ing_rate *= c.clock_rate
                                produces_store.append((
                                    self.pixelBuffers['items'][ingredient.item.programmatic_name()],
                                    f'{ing_rate}x {ingredient.item.name} /m'))
                        self.icovwConsumes.set_model(consumes_store)
                        self.icovwConsumes.set_pixbuf_column(0)
                        self.icovwConsumes.set_text_column(1)
                        self.icovwProduces.set_model(produces_store)
                        self.icovwProduces.set_pixbuf_column(0)
                        self.icovwProduces.set_text_column(1)
                        self.boxSelectedRecipe.set_visible(True)
                    else:
                        self.boxSelectedRecipe.set_visible(False)

                    # Ensure it's visible
                    self.boxResourceNodeRecipe.set_visible(False)
                    self.boxComponentSelectedRecipe.set_visible(True)
                    self.boxISNRecipe.set_visible(False)
            elif isinstance(c, InfiniteSupplyNode):
                # Set the spin button up properly
                if self.spinISNRecipeRate not in skip:
                    self.spinISNRecipeRate.set_value(c.rate or 0.0)

                # Filter out items that can't be conveyed
                items = [(item_name, item) for item_name, item in get_all_items()
                    if item.conveyance_type is not None]

                # If the availability filter is on, filter those out, too
                if self.chkAvailability.get_active():
                    items = [(item_name, item) for item_name, item in items
                        if item.availability.tier <= self.blueprint.factory.availability.tier
                        and item.availability.upgrade <= self.blueprint.factory.availability.upgrade]

                # Populate the combo box
                if self.cboISNRecipeItem not in skip:
                    self.cboISNRecipeItem.remove_all()
                    for item_name, item in items:
                        self.cboISNRecipeItem.append(item_name, item.name)
                    current_item = c.item.programmatic_name()
                    current_item_id = None

                    # Set the current item as active
                    for i in range(len(items)):
                        if items[i][0] == current_item:
                            current_item_id = i
                            break
                    if current_item is not None:
                        self.cboISNRecipeItem.set_active(current_item_id)

                # Make sure the right widgets are presented
                self.boxISNRecipe.set_visible(True)
                self.boxComponentSelectedRecipe.set_visible(False)
                self.boxResourceNodeRecipe.set_visible(False)
                self.boxSelectedRecipe.set_visible(False)
            elif isinstance(c, ResourceNode):
                # Set item dropdown by index
                if self.cboResourceNodeItem not in skip:
                    node_item_index = self.node_items.index(c.item.programmatic_name())
                    self.cboResourceNodeItem.set_active(node_item_index)

                # Set purity dropdown by index
                if self.cboResourceNodePurity not in skip:
                    purity_index = self.purities.index(c.purity)
                    self.cboResourceNodePurity.set_active(purity_index)

                # Set what we can see
                self.boxResourceNodeRecipe.set_visible(True)
                self.boxISNRecipe.set_visible(False)
                self.boxComponentSelectedRecipe.set_visible(False)
                self.boxSelectedRecipe.set_visible(False)
            else:
                # Hide all of these widgets
                self.boxISNRecipe.set_visible(False)
                self.boxComponentSelectedRecipe.set_visible(False)
                self.boxResourceNodeRecipe.set_visible(False)
                self.boxSelectedRecipe.set_visible(False)

            # Update the build cost of the component
            recipe_store = Gtk.ListStore(Pixbuf, str)

            # Prepare to set up current connection data by clearing out the old data
            for i in range(len(self.icovwInputs)):
                self.boxComponentInputs.remove(self.icovwInputs[i])
                self.boxComponentInputs.remove(self.btnConnectInputs[i])
            for i in range(len(self.icovwOutputs)):
                self.boxComponentOutputs.remove(self.icovwOutputs[i])
                self.boxComponentOutputs.remove(self.btnConnectOutputs[i])

            # Update inputs
            self.boxComponentInputs.remove(self.lblNoInputs)
            self.icovwInputs = []  # Clear out the list of IconViews showing the inputs
            self.btnConnectInputs = []
            for i in range(len(c.inputs)):  # Create one IconView and Button per input
                icovw = Gtk.IconView()
                store = Gtk.ListStore(Pixbuf, str)
                for ingredient in c.inputs[i].ingredients:
                    store.append((
                        self.pixelBuffers['items'][ingredient.item.programmatic_name()],
                        f'{ingredient.rate}x {ingredient.item.name} /m'
                    ))
                icovw.set_model(store)
                icovw.set_pixbuf_column(0)
                icovw.set_text_column(1)
                self.icovwInputs.append(icovw)

                button = TaggableButton(tags={
                    'component': c,
                    'connection': c.inputs[i],
                    'connection_index': i})
                button.set_label('Manage...')
                button.connect('clicked', self.__btnConnection_clicked)
                self.btnConnectInputs.append(button)

            # Show either the IconViews or a "None" label
            if len(self.icovwInputs) == 0:
                self.boxComponentInputs.append(self.lblNoInputs)
            for i in range(len(self.icovwInputs)):
                self.boxComponentInputs.append(self.icovwInputs[i])
                self.boxComponentInputs.append(self.btnConnectInputs[i])

            # Update the outputs in the same way
            self.boxComponentOutputs.remove(self.lblOutputs)
            self.icovwOutputs = []
            self.btnConnectOutputs = []
            for i in range(len(c.outputs)):
                icovw = Gtk.IconView()
                store = Gtk.ListStore(Pixbuf, str)
                for ingredient in c.outputs[i].ingredients:
                    store.append((
                        self.pixelBuffers['items'][ingredient.item.programmatic_name()],
                        f'{ingredient.rate}x {ingredient.item.name} /m'
                    ))
                icovw.set_model(store)
                icovw.set_pixbuf_column(0)
                icovw.set_text_column(1)
                self.icovwOutputs.append(icovw)

                button = TaggableButton(tags={
                    'component': c,
                    'connection': c.outputs[i],
                    'connection_index': i})
                button.set_label('Manage...')
                button.connect('clicked', self.__btnConnection_clicked)
                self.btnConnectOutputs.append(button)

            # Show either the IconView or a "None" label
            if len(self.icovwOutputs) > 0:
                self.boxComponentOutputs.append(self.lblOutputs)
            for i in range(len(self.icovwOutputs)):
                self.boxComponentOutputs.append(self.icovwOutputs[i])
                self.boxComponentOutputs.append(self.btnConnectOutputs[i])

            # Get the recipe to build the component so we can update the build cost
            try:
                comp_recipe_name, comp_recipe = [ (name, recipe) for name, recipe
                    in get_all_recipes()
                    if name == c.__class__.__name__ ][0]
            except IndexError:
                logging.debug('Failed to get the component recipe')
                comp_recipe = None

            # If there is a recipe, display it
            self.boxComponentRecipe.remove(self.lblComponentRecipe)
            self.boxComponentRecipe.remove(self.icovwComponentRecipe)
            if comp_recipe:
                for ingredient in comp_recipe.consumes:
                    recipe_store.append((
                        self.pixelBuffers['items'][ingredient.item.programmatic_name()],
                        f'{ingredient.amount}x {ingredient.item.name}'))
                self.icovwComponentRecipe.set_model(recipe_store)
                self.icovwComponentRecipe.set_pixbuf_column(0)
                self.icovwComponentRecipe.set_text_column(1)
                self.boxComponentRecipe.append(self.lblComponentRecipe)
                self.boxComponentRecipe.append(self.icovwComponentRecipe)

            # Update component errors listing
            for lbl in self.lblComponentErrors:
                self.boxComponentErrors.remove(lbl)
            self.lblComponentErrors = []
            if len(c.errors) > 0:
                for err in c.errors:
                    lbl = Gtk.Label()
                    lbl.set_markup(f'<b>· {err.level.name.title()}:</b> {err.message}')
                    lbl.set_wrap(True)
                    self.lblComponentErrors.append(lbl)
            else:
                self.lblComponentErrors.append(Gtk.Label(label='None'))

            for lbl in self.lblComponentErrors:
                self.boxComponentErrors.append(lbl)

            # Update tags listing
            if self.boxComponentTags not in skip:
                self.boxComponentTags.component = self.blueprint.selected
                self.boxComponentTags.repopulate()

            # Make sure everything is visible
            self.boxComponentDetails.set_visible(True)
        else:
            # If nothing is selected, just hide all these controls
            self.boxComponentDetails.set_visible(False)

    def update_window(self,
        skip: list = [],
    ):
        '''
        When the factory context of the MainWindow changes, call this function to update all of the
        UI elements depending on that context.
        '''

        self.block_all_signals()
        self.set_window_title()
        self.update_component_context(skip=skip)

        # Set availability of various widgets
        if self.blueprint:
            self.boxFactoryFunctions.set_sensitive(True)
            self.btnSaveFactory.set_sensitive(self.unsaved_changes)
            self.boxFilters.set_sensitive(True)
            if self.entryFactoryName not in skip:
                self.entryFactoryName.get_buffer().set_text(self.blueprint.factory.name, -1)
            self.set_tier_and_upgrade()
            self.update_buildings_list()
        else:
            self.btnSaveFactory.set_sensitive(False)
            self.boxFactoryFunctions.set_sensitive(False)
            self.boxFilters.set_sensitive(False)
        self.factoryDesigner.queue_draw()
        self.unblock_all_signals()


    # Layout Construction

    def __build_window(self):
        '''
        Builds the contents of the main window. A strip of application/factory-level functions appear
        across the top. A column along the left displays building options. A column along the right
        displays info based on the current context. A space through the middle is the main factory
        designer area.
        '''

        # Track all signals so we can block/unblock them easily
        self.windowSignals = []

        # Build a vertical box layout to give us a strip on top for factory tools
        self.boxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Add the main split panel container on the bottom of the vbox
        self.paneLeft = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxMain.append(self.paneLeft)

        # Build the left-hand panel containing the list of buildings
        self.__build_buildings_options()
        self.paneLeft.set_start_child(self.paneBuildingsOptions)
        self.paneLeft.set_position(350)
        self.paneLeft.set_vexpand(True)

        # Build the right-hand panel as another split panel with the designer on the left and some
        # panels providing context on the factory and components on the right.
        self.paneRight = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paneRight.set_position(1000)
        self.paneLeft.set_end_child(self.paneRight)

        # Build the main panel containing the factory designer
        self.__build_factory_designer()
        self.paneRight.set_start_child(self.scrollFactoryDesigner)

        # Build the content of the context panel on the right
        self.__build_context_panel()
        self.paneRight.set_end_child(self.paneContext)

        # Add the top bar last since it causes the rest of the UI to update
        self.boxMain.prepend(self.__build_top_bar())

        # Connect signal handlers only after constructing everything
        self.__connect_handlers()

        # The main vbox becomes the top level element on the window
        self.set_child(self.boxMain)

    def __build_buildings_options(self):
        '''
        Builds the contents of the left-hand pane, primarily containing a list of buildings
        available to the user.
        '''

        # Start with two vertical panes
        self.paneBuildingsOptions = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.paneBuildingsOptions.set_position(150)

        # Top pane: filtering options for the bottom pane
        self.scrollBuildingFilters = Gtk.ScrolledWindow()
        self.boxFilters = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxFilters.set_margin_start(5)
        self.boxFilters.set_margin_end(5)
        self.boxFilters.set_margin_bottom(5)
        self.boxFilters.set_margin_top(5)
        self.boxFilters.set_spacing(5)

        # Top pane: Factory availability checkbox
        self.chkAvailability = Gtk.CheckButton(label='Availability')
        self.chkAvailability.set_active(True)
        self.boxFilters.append(self.chkAvailability)
        self.scrollBuildingFilters.set_child(self.boxFilters)

        # Top pane: Building Category selection
        self.boxBuildingCategory = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.chkBuildingCategory = Gtk.CheckButton(label='Building category: ')
        self.cboBuildingCategory = Gtk.ComboBoxText()
        self.cboBuildingCategory.set_hexpand(True)
        for category in BuildingCategory:
            self.cboBuildingCategory.append(category.name, category.name.title())

        self.boxBuildingCategory.append(self.chkBuildingCategory)
        self.boxBuildingCategory.append(self.cboBuildingCategory)
        self.boxFilters.append(self.boxBuildingCategory)

        # Top pane: Name filter
        self.boxNameFilter = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.chkNameFilter = Gtk.CheckButton(label='Name: ')
        self.entryNameFilter = Gtk.Entry()
        self.entryNameFilter.set_hexpand(True)
        self.boxNameFilter.append(self.chkNameFilter)
        self.boxNameFilter.append(self.entryNameFilter)
        self.boxFilters.append(self.boxNameFilter)

        # Bottom pane: Box to organize things
        self.boxBuildings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Bottom pane: list of buildings
        self.scrollBuildings = Gtk.ScrolledWindow()
        self.icovwBuildings = Gtk.IconView()
        self.icovwBuildings.set_spacing(5)
        self.icovwBuildings.set_vexpand(True)
        self.scrollBuildings.set_child(self.icovwBuildings)
        self.scrollBuildings.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Bottom pane: Build button
        self.btnBuild = Gtk.Button(label='Build')

        # Pack the box
        self.boxBuildings.append(self.btnBuild)
        self.boxBuildings.append(self.scrollBuildings)

        # Compile panel contents
        self.paneBuildingsOptions.set_start_child(self.scrollBuildingFilters)
        self.paneBuildingsOptions.set_end_child(self.boxBuildings)

    def __build_component_context_panel(self):
        '''
        Builds the right-side panel containing info about the selected component.
        '''

        # Wrap everything in a scrollable view
        self.scrollComponentDetails = Gtk.ScrolledWindow()

        # Set up read-only details in a box
        self.boxComponentDetails = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxComponentDetails.set_margin_start(5)
        self.boxComponentDetails.set_margin_end(5)
        self.boxComponentDetails.set_margin_bottom(5)
        self.boxComponentDetails.set_margin_top(5)
        self.boxComponentDetails.set_spacing(5)

        # Place a bold header for the section
        self.lblComponentHeader = Gtk.Label()
        self.lblComponentHeader.set_markup('<b>Component Details</b>')
        self.boxComponentDetails.append(self.lblComponentHeader)

        # Labels for basic details
        self.lblComponentBuildingType = Gtk.Label(label=f'Building type:')
        self.lblComponentAvailability = Gtk.Label(label='')
        self.lblComponentDimensions = Gtk.Label()
        self.lblComponentBasePowerUsage = Gtk.Label()

        # Box to contain links to wiki and image
        self.boxComponentLinks = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentLinks.set_halign(Gtk.Align.CENTER)
        self.linkWiki = Gtk.LinkButton().new_with_label(uri='', label='Wiki')
        self.linkImage = Gtk.LinkButton().new_with_label(uri='', label='Image')
        self.boxComponentLinks.append(self.linkWiki)
        self.boxComponentLinks.append(self.linkImage)

        # Pack the outer details box with all of these labels and such
        self.boxComponentDetails.append(self.lblComponentBuildingType)
        self.boxComponentDetails.append(self.lblComponentAvailability)
        self.boxComponentDetails.append(self.lblComponentDimensions)
        self.boxComponentDetails.append(self.lblComponentBasePowerUsage)
        self.boxComponentDetails.append(self.boxComponentLinks)

        # Name controls
        self.boxComponentName = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentName.set_spacing(5)
        self.lblComponentName = Gtk.Label(label='Name:')
        self.entryComponentName = Gtk.Entry()
        self.entryComponentName.set_hexpand(True)
        self.boxComponentName.append(self.lblComponentName)
        self.boxComponentName.append(self.entryComponentName)
        self.boxComponentDetails.append(self.boxComponentName)

        # Checkboxes for togglables in a box
        self.boxComponentBooleans = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentBooleans.set_halign(Gtk.Align.CENTER)
        self.chkComponentConstructed = Gtk.CheckButton(label='Constructed')
        self.chkComponentStandby = Gtk.CheckButton(label='Standby')
        self.boxComponentBooleans.append(self.chkComponentConstructed)
        self.boxComponentBooleans.append(self.chkComponentStandby)
        self.boxComponentDetails.append(self.boxComponentBooleans)

        # Processing recipe
        self.boxComponentSelectedRecipe = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentSelectedRecipe.set_spacing(5)
        self.boxComponentSelectedRecipe.set_halign(Gtk.Align.CENTER)
        self.lblComponentSelectedRecipe = Gtk.Label(label='Recipe:')
        self.cboComponentSelectedRecipe = Gtk.ComboBoxText()
        self.boxComponentSelectedRecipe.append(self.lblComponentSelectedRecipe)
        self.boxComponentSelectedRecipe.append(self.cboComponentSelectedRecipe)
        self.boxComponentDetails.append(self.boxComponentSelectedRecipe)

        # Clock rate controls
        self.boxComponentClockRate = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentClockRate.set_halign(Gtk.Align.CENTER)
        self.lblComponentClockRate = Gtk.Label(label='Clock rate:')
        self.adjClockSpeed = Gtk.Adjustment(
            lower=0.0,
            upper=2.5,
            step_increment=0.1,
            page_increment=1.0)
        self.adjClockSpeed.set_step_increment(0.1)
        self.spinComponentClockRate = Gtk.SpinButton(adjustment=self.adjClockSpeed)
        self.spinComponentClockRate.set_digits(2)
        self.boxComponentClockRate.append(self.lblComponentClockRate)
        self.boxComponentClockRate.append(self.spinComponentClockRate)
        self.boxComponentDetails.append(self.boxComponentClockRate)

        # Build a set of controls to display when ResourceNodes are selected
        self.boxResourceNodeRecipe = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxResourceNodeRecipe.set_spacing(5)
        self.boxResourceNodeRecipe.set_halign(Gtk.Align.CENTER)
        self.lblResourceNodeItem = Gtk.Label(label='Item:')
        self.cboResourceNodeItem = Gtk.ComboBoxText()

        for item in self.node_items:
            self.cboResourceNodeItem.append(item, item)

        # Pack the item widgets
        self.boxResourceNodeRecipe.append(self.lblResourceNodeItem)
        self.boxResourceNodeRecipe.append(self.cboResourceNodeItem)

        # Populate a combo box with node purity levels
        self.lblResourceNodePurity = Gtk.Label(label='Purity:')
        self.cboResourceNodePurity = Gtk.ComboBoxText()
        for purity in Purity.__members__:
            self.cboResourceNodePurity.append(purity, purity.title())

        # Pack the resource node widgets
        self.boxResourceNodeRecipe.append(self.lblResourceNodePurity)
        self.boxResourceNodeRecipe.append(self.cboResourceNodePurity)
        self.boxComponentDetails.append(self.boxResourceNodeRecipe)

        # Build a set of controls to display when InfiniteSupplyNodes are selected
        self.boxISNRecipe = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxISNRecipe.set_spacing(5)
        self.boxISNRecipe.set_halign(Gtk.Align.CENTER)
        self.lblISNRecipe = Gtk.Label(label='Recipe:')
        self.spinISNRecipeRate = Gtk.SpinButton()
        self.adjISNRecipeRate = Gtk.Adjustment(
            lower=0,
            upper=1000,
            step_increment=1,
            page_increment=10,
            page_size=10)
        self.spinISNRecipeRate.set_adjustment(self.adjISNRecipeRate)
        self.cboISNRecipeItem = Gtk.ComboBoxText()
        self.boxISNRecipe.append(self.lblISNRecipe)
        self.boxISNRecipe.append(self.spinISNRecipeRate)
        self.boxISNRecipe.append(self.cboISNRecipeItem)
        self.boxComponentDetails.append(self.boxISNRecipe)

        # Selected recipe consumes/produces details
        self.boxSelectedRecipe = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxSelectedRecipe.set_halign(Gtk.Align.FILL)
        self.boxSelectedRecipe.set_hexpand(True)
        self.boxSelectedRecipe.set_spacing(5)

        self.boxConsumes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxConsumes.set_halign(Gtk.Align.FILL)
        self.boxConsumes.set_hexpand(True)
        self.lblConsumes = Gtk.Label()
        self.lblConsumes.set_markup('<b>Consumes</b>')
        self.icovwConsumes = Gtk.IconView()
        self.boxConsumes.append(self.lblConsumes)
        self.boxConsumes.append(self.icovwConsumes)

        self.boxProduces = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxProduces.set_halign(Gtk.Align.FILL)
        self.boxProduces.set_hexpand(True)
        self.lblProduces = Gtk.Label()
        self.lblProduces.set_markup('<b>Produces</b>')
        self.icovwProduces = Gtk.IconView()
        self.boxProduces.append(self.lblProduces)
        self.boxProduces.append(self.icovwProduces)

        # Pack the outer box
        self.boxSelectedRecipe.append(self.boxConsumes)
        self.boxSelectedRecipe.append(self.boxProduces)
        self.boxComponentDetails.append(self.boxSelectedRecipe)

        # Add a visual separator
        self.sepBeforeConnections = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentDetails.append(self.sepBeforeConnections)

        # Connections
        self.boxComponentConnections = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentConnections.set_halign(Gtk.Align.FILL)
        self.boxComponentConnections.set_hexpand(True)
        self.boxComponentConnections.set_spacing(5)

        self.boxComponentInputs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxComponentInputs.set_halign(Gtk.Align.FILL)
        self.boxComponentInputs.set_hexpand(True)
        self.lblInputs = Gtk.Label()
        self.lblInputs.set_markup('<b>Inputs</b>')
        self.icovwInputs = [Gtk.IconView()]
        self.btnConnectInputs = [Gtk.Button()]
        self.boxComponentInputs.append(self.lblInputs)
        self.boxComponentInputs.append(self.icovwInputs[0])
        self.boxComponentInputs.append(self.btnConnectInputs[0])

        self.boxComponentOutputs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxComponentOutputs.set_halign(Gtk.Align.FILL)
        self.boxComponentOutputs.set_hexpand(True)
        self.lblOutputs = Gtk.Label()
        self.lblOutputs.set_markup('<b>Outputs</b>')
        self.icovwOutputs = [Gtk.IconView()]
        self.btnConnectOutputs = [Gtk.Button()]
        self.boxComponentOutputs.append(self.lblOutputs)
        self.boxComponentOutputs.append(self.icovwOutputs[0])
        self.boxComponentOutputs.append(self.btnConnectOutputs[0])

        # Labels for when there is no input or output
        self.lblNoInputs = Gtk.Label(label='None')
        self.lblNoOutputs = Gtk.Label(label='None')
        self.lblNoInputs.set_margin_top(10)

        # Pack the outer box
        self.boxComponentConnections.append(self.boxComponentInputs)
        self.boxComponentConnections.append(self.boxComponentOutputs)
        self.boxComponentDetails.append(self.boxComponentConnections)

        # Component errors
        self.boxComponentErrors = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxComponentErrors.set_spacing(5)
        self.lblComponentErrorsHeader = Gtk.Label()
        self.lblComponentErrorsHeader.set_markup('<b>Simulation Errors</b>')
        self.lblComponentErrors = []
        self.boxComponentDetails.append(self.lblComponentErrorsHeader)
        self.boxComponentDetails.append(self.boxComponentErrors)

        # Box to contain the build cost recipe for the component
        self.boxComponentRecipe = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.lblComponentRecipe = Gtk.Label()
        self.lblComponentRecipe.set_markup('<b>Component Build Cost</b>')
        self.lblComponentRecipe.set_margin_top(10) # Put a little visual space here
        self.icovwComponentRecipe = Gtk.IconView()
        self.icovwComponentRecipe.set_item_orientation(Gtk.Orientation.HORIZONTAL)
        self.boxComponentRecipe.append(self.lblComponentRecipe)
        self.boxComponentRecipe.append(self.icovwComponentRecipe)
        self.boxComponentDetails.append(self.boxComponentRecipe)

        # A grid of tag data and widgets (which mostly gets set up in update_window calls)
        self.boxComponentTags = TagBox(component=None, callback=self.__boxComponentTags_changed)
        self.boxComponentDetails.append(self.boxComponentTags)

        # Label for when there are no tags
        self.lblNoComponentTags = Gtk.Label(label='None')

        # Button to delete the component
        self.sepDangerZone = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.btnDeleteComponent = Gtk.Button(label='Delete Component')
        self.boxComponentDetails.append(self.sepDangerZone)
        self.boxComponentDetails.append(self.btnDeleteComponent)

        # Add it all to the scrollwindow
        self.scrollComponentDetails.set_child(self.boxComponentDetails)

    def __build_context_panel(self):
        '''
        Builds the right-hand panel showing context about the factory and selected component. This
        is made of two stacked panels showing factory and component details.
        '''

        self.paneContext = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.__build_factory_context_panel()
        self.paneContext.set_start_child(self.scrollFactoryFunctions)

        self.__build_component_context_panel()
        self.paneContext.set_end_child(self.scrollComponentDetails)
        self.paneContext.set_position(100)

    def __build_factory_context_panel(self):
        '''
        Builds the right-side panel containing factory details.
        '''

        # Wrap everything in a scrollwindow
        self.scrollFactoryFunctions = Gtk.ScrolledWindow()

        # Contain all the factory-level functions within a box so they can all be enabled and
        # disabled by doing so to this one widget
        self.boxFactoryFunctions = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxFactoryFunctions.set_spacing(5)
        self.boxFactoryFunctions.set_margin_start(5)
        self.boxFactoryFunctions.set_margin_end(5)
        self.boxFactoryFunctions.set_margin_bottom(5)
        self.boxFactoryFunctions.set_margin_top(5)
        self.boxFactoryFunctions.set_sensitive(True if self.blueprint else False)

        # Place a header
        self.lblFactoryHeader = Gtk.Label()
        self.lblFactoryHeader.set_markup('<b>Factory Details</b>')
        self.boxFactoryFunctions.append(self.lblFactoryHeader)

        # Build the text box showing the name of the factory
        self.boxFactoryName = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxFactoryName.set_hexpand(True)
        self.boxFactoryName.set_spacing(5)
        self.lblFactoryName = Gtk.Label(label='Factory Name:')
        self.lblFactoryName.set_margin_start(5)
        self.entryFactoryName = Gtk.Entry()
        self.entryFactoryName.set_hexpand(True)
        self.boxFactoryName.append(self.lblFactoryName)
        self.boxFactoryName.append(self.entryFactoryName)
        self.boxFactoryFunctions.append(self.boxFactoryName)

        # Build the controls allowing tier/upgrade selection
        self.boxTierUpgrade = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxTierUpgrade.set_spacing(5)
        self.lblTierUpgrade = Gtk.Label(label='Tier/Upgrade:')
        self.lblTierUpgrade.set_margin_start(5)
        self.boxTierUpgrade.append(self.lblTierUpgrade)

        # The "Tier" combo box is populated from the satisfactory.base.Availability class
        self.cboTier = Gtk.ComboBoxText()
        for tier in Availability.get_tier_strings():
            self.cboTier.append(tier, tier)
        self.cboTier.set_active(0)
        self.boxTierUpgrade.append(self.cboTier)

        # The "/" character between the combo boxes
        self.lblTierUpgradeSlash = Gtk.Label(label='/')
        self.boxTierUpgrade.append(self.lblTierUpgradeSlash)

        # The "Upgrade" combo box gets populated based on the "Tier" selection
        self.cboUpgrade = Gtk.ComboBoxText()
        self.__cboTier_changed(self.cboUpgrade)
        self.boxTierUpgrade.append(self.cboUpgrade)

        self.boxFactoryFunctions.append(self.boxTierUpgrade)
        self.scrollFactoryFunctions.set_child(self.boxFactoryFunctions)

    def __build_factory_designer(self):
        '''
        Builds the middle panel with the factory designer display
        '''

        self.scrollFactoryDesigner = Gtk.ScrolledWindow()
        self.factoryDesigner = FactoryDesignerWidget(self, self.blueprint)
        self.scrollFactoryDesigner.set_child(self.factoryDesigner)

    def __build_top_bar(self):
        '''
        Builds the UI controls which run across the top bar of the window.
        '''

        # The bar's top level object is a horizontal box with some padding
        self.boxTopBar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxTopBar.set_spacing(10)
        self.boxTopBar.set_margin_top(10)
        self.boxTopBar.set_margin_bottom(10)
        self.boxTopBar.set_margin_start(10)
        self.boxTopBar.set_margin_end(10)

        # Build the "New" button
        self.btnNewFactory = Gtk.Button()
        self.btnNewFactory.set_icon_name('document-new')

        # Build the "Open" button
        self.btnOpenFactory = Gtk.Button()
        self.btnOpenFactory.set_icon_name('document-open')

        # Build the "Save" button
        self.btnSaveFactory = Gtk.Button()
        self.btnSaveFactory.set_icon_name('document-save')

        # Build the "Save As" button
        self.btnSaveFactoryAs = Gtk.Button()
        self.btnSaveFactoryAs.set_icon_name('document-save-as')

        # Build the "Simulate" and "Clean" buttons
        self.btnSimulate = Gtk.Button()
        self.btnSimulate.set_icon_name('media-playback-start')
        self.btnSimulate.set_margin_start(20)
        self.btnPurge = Gtk.Button()
        self.btnPurge.set_icon_name('edit-clear')

        # Add all the buttons to the main hbox
        self.boxTopBar.append(self.btnNewFactory)
        self.boxTopBar.append(self.btnOpenFactory)
        self.boxTopBar.append(self.btnSaveFactory)
        self.boxTopBar.append(self.btnSaveFactoryAs)
        self.boxTopBar.append(self.btnSimulate)
        self.boxTopBar.append(self.btnPurge)

        return self.boxTopBar

    def __build_ui_helpers(self):
        '''
        Builds reusable items which are unique to this application
        '''

        # Populate the special resource node settings widgets and show them.
        # Those items should be ones that can be produced by miner recipes.
        miner_recipes = [ (recipe_name, recipe) for recipe_name, recipe in get_all_recipes()
            if recipe.building_type == BuildingType.MINER ]
        node_items = []
        for _, recipe in miner_recipes:
            node_items.extend([ ingredient.item.programmatic_name() \
                for ingredient in recipe.produces])
        self.node_items = sorted(set(node_items))

        self.purities = [ purity[1] for purity in Purity.__members__.items() ]

        self.satFileFilter = Gtk.FileFilter()
        self.satFileFilter.set_name('Satisfactory Blueprints (*.sat)')
        self.satFileFilter.add_pattern('*.sat')
        self.fileFilters = Gio.ListStore.new(Gtk.FileFilter)
        self.fileFilters.append(self.satFileFilter)
        self.__load_images()

    def __connect_handlers(self):
        '''
        Connects signals for the widgets on this window. This is done as a separate task after the
        window has been fully constructed. This prevents signals from being emitted before the
        window is functional.

        Each signal is registered to the global windowSignals list so that the signals can be
        suppressed during widget updates, preventing infinite signal loops.
        '''

        self.windowSignals.extend([
            # Signals for this window
            (self, self.connect('close-request', self.__mainWindow_closeRequested)),

            # Signals for widgets in the top bar containing factory-level options
            (self.btnNewFactory,
                self.btnNewFactory.connect('clicked', self.__btnNewFactory_clicked)),
            (self.btnOpenFactory,
                self.btnOpenFactory.connect('clicked', self.__btnOpenFactory_clicked)),
            (self.btnSaveFactory,
                self.btnSaveFactory.connect('clicked', self.__btnSaveFactory_clicked)),
            (self.btnSaveFactoryAs,
                self.btnSaveFactoryAs.connect('clicked', self.__btnSaveFactoryAs_clicked)),
            (self.btnSimulate,
                self.btnSimulate.connect('clicked', self.__btnSimulate_clicked)),
            (self.btnPurge,
                self.btnPurge.connect('clicked', self.__btnPurge_clicked)),

            # Signals for the buildings panel
            (self.chkAvailability,
                self.chkAvailability.connect_after('toggled', self.__chkAvailability_toggled)),
            (self.chkBuildingCategory,
                self.chkBuildingCategory.connect_after(
                    'toggled',
                    self.__chkBuildingCategory_toggled)),
            (self.cboBuildingCategory,
                self.cboBuildingCategory.connect_after(
                    'changed',
                    self.__cboBuildingCategory_changed)),
            (self.chkNameFilter,
                self.chkNameFilter.connect_after('toggled', self.__chkNameFilter_toggled)),
            (self.entryNameFilter.get_buffer(),
                self.entryNameFilter.get_buffer().connect_after('deleted-text',
                    self.__entryNameFilter_deleted)),
            (self.entryNameFilter.get_buffer(),
                self.entryNameFilter.get_buffer().connect_after('inserted-text',
                    self.__entryNameFilter_inserted)),
            (self.btnBuild,
                self.btnBuild.connect('clicked', self.__btnBuild_clicked)),

            # Signals for component detail widgets
            (self.entryFactoryName.get_buffer(),
                self.entryFactoryName.get_buffer().connect_after('deleted-text',
                    self.__entryFactoryName_deleted)),
            (self.entryFactoryName.get_buffer(),
                self.entryFactoryName.get_buffer().connect('inserted-text',
                    self.__entryFactoryName_inserted)),
            (self.cboTier,
                self.cboTier.connect_after('changed', self.__cboTier_changed)),
            (self.cboUpgrade,
                self.cboUpgrade.connect('changed', self.__cboUpgrade_changed)),
            (self.entryComponentName.get_buffer(),
                self.entryComponentName.get_buffer().connect_after('deleted-text',
                    self.__entryComponentName_deleted)),
            (self.entryComponentName.get_buffer(),
                self.entryComponentName.get_buffer().connect_after('inserted-text',
                    self.__entryComponentName_inserted)),
            (self.spinComponentClockRate,
                self.spinComponentClockRate.connect(
                    'value-changed',
                    self.__spinComponentClockRate_changed)),
            (self.chkComponentConstructed,
                self.chkComponentConstructed.connect_after('toggled',
                    self.__chkComponentConstructed_toggled)),
            (self.chkComponentStandby,
                self.chkComponentStandby.connect_after('toggled',
                    self.__chkComponentStandby_toggled)),
            (self.cboComponentSelectedRecipe,
                self.cboComponentSelectedRecipe.connect_after(
                    'changed',
                    self.__cboComponentSelectedRecipe_changed)),
            (self.spinISNRecipeRate,
                self.spinISNRecipeRate.connect_after(
                    'value-changed',
                    self.__spinISNRecipeRate_value_changed)),
            (self.cboResourceNodeItem,
                self.cboResourceNodeItem.connect_after(
                    'changed',
                    self.__cboResourceNodeItem_changed)),
            (self.cboResourceNodePurity,
                self.cboResourceNodePurity.connect_after(
                    'changed',
                    self.__cboResourceNodePurity_changed)),
            (self.cboISNRecipeItem,
                self.cboISNRecipeItem.connect_after(
                    'changed',
                    self.__cboISNRecipeItem_changed)),

            # Widgets in the "danger zone"
            (self.btnDeleteComponent,
                self.btnDeleteComponent.connect('clicked', self.__btnDeleteComponent_clicked)),
        ])

    def __load_images(self):
        '''
        Load all images that get used in this window from disk and store them in memory.
        '''

        pixbuf = Pixbuf()
        self.pixelBuffers = {}
        building_pixbufs = {}
        item_pixbufs = {}

        # Load building pixel buffers
        all_buildings = MainWindow.get_building_options()
        for building in all_buildings:
            imageFile = Path(f'./static/images/components/{building.__class__.__name__}.png')
            if imageFile.exists():
                #pb = pixbuf.new_from_file_at_size(str(imageFile), 64, 64)
                pb = pixbuf.new_from_file_at_size(str(imageFile), 64, 64)
            else:
                pb = None
            building_pixbufs[building.__class__.__name__] = pb
        self.pixelBuffers['building_options'] = building_pixbufs

        # Load item pixel buffers
        all_items = get_all_items()
        for itemname, item in all_items:
            imageFile = Path(f'./static/images/components/{itemname}.png')
            if imageFile.exists():
                pb = pixbuf.new_from_file_at_size(str(imageFile), 32, 32)
            else:
                pb = None
            item_pixbufs[itemname] = pb
        self.pixelBuffers['items'] = item_pixbufs


    # Signal Handlers

    # + Signal handlers for this window
    def __mainWindow_closeRequested(self, window):
        '''
        The user has clicked the "X" on this window or otherwise told it to close. We intercept that
        request and make sure no unsaved changes will be lost.
        '''

        if self.unsaved_changes:
            self.confirm_discard(self.__discard_response_close_window)
            return True
        else:
            return False

    def __discard_response_close_window(self, response):
        '''
        The user has tried to close the window, but they had unsaved changes. We asked them if it's
        okay to discard their changes, and they have given us a response. If it's okay, close the
        window, but otherwise return them to the designer so they can save.
        '''

        if response:
            self.destroy()

    # + "New" button signal handlers

    def __btnNewFactory_clicked(self, btn):
        '''
        The user has clicked the New Factory button
        '''

        if self.unsaved_changes:
            self.confirm_discard(self.__discard_response_new_factory)
        else:
            self.__discard_response_new_factory(True)

    def __discard_response_new_factory(self, response):
        '''
        The user has clicked the New Factory button, but they have unsaved changes. They have been
        given a warning to this effect, and have responded either "Okay" (True) or "Cancel" (False).
        Alternatively, there are no unsaved changes, and response is True anyway.
        '''

        if response:
            self.blueprint = Blueprint(factory=Factory(name='New Factory'))
            self.factoryDesigner.blueprint = self.blueprint
            self.unsaved_changes = True
            self.update_window()

    # + "Open" button signal handlers

    def __btnOpenFactory_clicked(self, btn):
        '''
        The user has clicked the Open Factory button
        '''

        if self.unsaved_changes:
            self.confirm_discard(self.__discard_response_open_factory)
        else:
            self.__discard_response_open_factory(True)

    def __discard_response_open_factory(self, response):
        '''
        The user has clicked the Open Factory button, but they have unsaved changes. They have been
        given a warning to this effect, and have responded either "Okay" (True) or "Cancel" (False).
        Alternatively, there are no unsaved changes, and response is True anyway.
        '''

        if response:
            dlgOpenFactory = Gtk.FileDialog()
            dlgOpenFactory.set_title('Open Factory')
            dlgOpenFactory.set_filters(self.fileFilters)
            dlgOpenFactory.set_default_filter(self.satFileFilter)
            dlgOpenFactory.open(self, None, self.__dlgOpenFactory_response)

    def __dlgOpenFactory_response(self, dlg, response):
        '''
        The user has selected a factory file to open
        '''

        try:
            blueprintFile = dlg.open_finish(response)
            self.load_blueprint(blueprintFile.get_path())
        except Exception as ex:
            print(f'[DEBUG] Couldn\'t open the blueprint: {ex}')

    # + "Save" button signal handlers

    def __btnSaveFactory_clicked(self, btn):
        '''
        The user has clicked the "Save" button
        '''

        if self.unsaved_changes:
            if self.blueprintFile:
                self.blueprint.save(self.blueprintFile)
                self.unsaved_changes = False
                self.set_window_title()
            else:
                dlgSaveFactory = Gtk.FileDialog()
                dlgSaveFactory.set_title('Save Factory...')
                dlgSaveFactory.set_filters(self.fileFilters)
                dlgSaveFactory.set_default_filter(self.satFileFilter)
                dlgSaveFactory.save(self, None, self.__dlgSaveFactoryAs_response)

    def __btnSaveFactoryAs_clicked(self, btn):
        '''
        The user cliked the "Save As" button.
        '''

        dlgSaveFactoryAs = Gtk.FileDialog()
        dlgSaveFactoryAs.set_title('Save Factory As...')
        dlgSaveFactoryAs.set_filters(self.fileFilters)
        dlgSaveFactoryAs.set_default_filter(self.satFileFilter)
        dlgSaveFactoryAs.save(self, None, self.__dlgSaveFactoryAs_response)

    def __dlgSaveFactoryAs_response(self, dlg, response):
        '''
        The user either clicked "Save" without having an already active blueprint file, or they
        clicked "Save As". They then either selected a file (response is True) or canceled
        the window (response is False).
        '''

        if response:
            try:
                # Try the save first so we don't change the app context if it fails
                blueprintFile = dlg.save_finish(response).get_path()
                self.blueprint.save(blueprintFile)
                self.blueprintFile = blueprintFile
                self.unsaved_changes = False
                self.update_window()
            except IOError as ex:
                print(f'[DEBUG] Error saving blueprint at file {blueprintFile}:\n  {ex}')
                # TODO: Replace with real error dialog
            except Exception as ex:
                print(f'[DEBUG] Could not save the blueprint: {ex}')

    # + Simulate/Purge button signal handlers

    def __btnSimulate_clicked(self, btn):
        self.blueprint.factory.purge()
        self.blueprint.factory.simulate()
        self.blueprint.invalidate_geometry()
        self.unsaved_changes = True
        self.update_window()

    def __btnPurge_clicked(self, btn):
        self.blueprint.factory.purge()
        self.blueprint.invalidate_geometry()
        self.unsaved_changes = True
        self.update_window()

    # + Factory Name Entry signal handlers

    def __entryFactoryName_changed(self, text):
        if text != self.blueprint.factory.name:
            self.blueprint.factory.name = text
            self.unsaved_changes = True
            self.update_window(skip=[self.entryFactoryName])

    def __entryFactoryName_deleted(self, buffer, position, chars):
        self.__entryFactoryName_changed(buffer.get_text())

    def __entryFactoryName_inserted(self, buffer, position, chars, nchars):
        self.__entryFactoryName_changed(buffer.get_text())

    # + "Tier" combo box signal handlers

    def __cboTier_changed(self, cbo):
        '''
        The "Tier" combo box has had its value changed. We need to populate the "Upgrade" combo box
        accordingly.
        '''

        self.set_tier_and_upgrade(tier=cbo.get_active())
        self.update_buildings_list()

    # + "Upgrade" combo box signal handlers

    def __cboUpgrade_changed(self, cbo):
        self.blueprint.factory.availability.upgrade = self.cboUpgrade.get_active() + 1
        self.unsaved_changes = True
        self.update_window()

    # + Building option filters signal handlers

    def __chkAvailability_toggled(self, chk):
        self.filters['availability'] = chk.get_active()
        self.update_window()

    def __chkBuildingCategory_toggled(self, chk):
        self.filters['building_category'] = chk.get_active()
        self.update_buildings_list()

    def __cboBuildingCategory_changed(self, cbo):
        if self.filters['building_category']:
            self.update_buildings_list()

    def __chkNameFilter_toggled(self, chk):
        self.filters['name'] = chk.get_active()
        self.update_buildings_list()

    def __entryNameFilter_deleted(self, buffer, position, chars):
        if self.filters['name']:
            self.update_buildings_list()

    def __entryNameFilter_inserted(self, buffer, position, chars, nchars):
        if self.filters['name']:
            self.update_buildings_list()

    def __btnBuild_clicked(self, btn):
        center_x = self.blueprint.viewport.region.left + (self.blueprint.viewport.region.width / 2)
        center_x /= self.blueprint.viewport.scale
        center_y = self.blueprint.viewport.region.top + (self.blueprint.viewport.region.height / 2)
        center_y /= self.blueprint.viewport.scale

        # Get the only selected item, which should be a class for the building, or do nothing
        selected = self.icovwBuildings.get_selected_items()
        if len(selected) > 0:
            selected = selected[0].get_indices()[0]

            # Create a default instance of that kind of component and set it to be added to the
            # blueprint when the user clicks somewhere there.
            if self.buildings[selected] == ResourceNode:
                new_component = self.buildings[selected](
                    item=IronOre)
            else:
                new_component = self.buildings[selected]()
            self.blueprint.add_component(new_component, self.blueprint.viewport.region.location)
            self.blueprint.selected = new_component

        self.update_window()

    # + Component detail widget signal handlers

    def __entryComponentName_changed(self, text):
        self.blueprint.selected.name = text
        self.unsaved_changes = True
        self.update_window(skip=[self.entryComponentName])

    def __entryComponentName_deleted(self, buffer, position, chars):
        if self.blueprint and self.blueprint.selected:
            self.__entryComponentName_changed(buffer.get_text())

    def __entryComponentName_inserted(self, buffer, position, chars, nchars):
        if self.blueprint and self.blueprint.selected:
            self.__entryComponentName_changed(buffer.get_text())

    def __spinComponentClockRate_changed(self, range):
        rate = round(self.spinComponentClockRate.get_value(), 2)
        self.blueprint.selected.clock_rate = rate
        self.unsaved_changes = True
        self.update_window()
        # self.update_window(skip=[self.spinComponentClockRate])

    def __chkComponentConstructed_toggled(self, chk):
        if self.blueprint and self.blueprint.selected:
            self.blueprint.selected.constructed = chk.get_active()
            if not isinstance(self.blueprint.selected, Conveyance):
                geo = self.blueprint.geometry.get(self.blueprint.selected.id)
                geo.calculate(
                    scale=self.blueprint.viewport.scale,
                    translate=self.blueprint.viewport.region.location)
                # geo._ComponentGeometry__calculate_badges()
            self.unsaved_changes = True
            self.update_window()

    def __chkComponentStandby_toggled(self, chk):
        if self.blueprint and self.blueprint.selected:
            self.blueprint.selected.standby = chk.get_active()
            if not isinstance(self.blueprint.selected, Conveyance):
                geo = self.blueprint.geometry.get(self.blueprint.selected.id)
                geo.calculate(
                    scale=self.blueprint.viewport.scale,
                    translate=self.blueprint.viewport.region.location)
                # geo._ComponentGeometry__calculate_badges()
            self.unsaved_changes = True
            self.update_window()

    def __cboComponentSelectedRecipe_changed(self, cbo):
        if self.blueprint and self.blueprint.selected \
            and isinstance(self.blueprint.selected, Building):
                recipe_name = cbo.get_active_text().title().replace(' ', '')
                try:
                    recipe = [ recipe for name, recipe in get_all_recipes() \
                        if name == recipe_name ][0]
                    self.blueprint.selected.recipe = recipe
                    self.unsaved_changes = True
                    self.update_window(skip=[self.cboComponentSelectedRecipe])
                except IndexError:
                    logging.debug(f'No recipe called {recipe_name} was found')

    def __spinISNRecipeRate_value_changed(self, spin):
        if self.blueprint and self.blueprint.selected:
            self.blueprint.selected.rate = spin.get_value()
            self.blueprint.unsaved_changes = True
            self.update_window(skip=[self.spinISNRecipeRate])

    def __cboISNRecipeItem_changed(self, cbo):
        if self.blueprint and self.blueprint.selected \
            and isinstance(self.blueprint.selected, InfiniteSupplyNode):
                item_name = cbo.get_active_text().title().replace(' ', '')
                try:
                    item = [ item for name, item in get_all_items() \
                        if name == item_name ][0]
                    self.blueprint.selected.item = item
                    self.unsaved_changes = True
                    self.update_window(skip=[self.cboISNRecipeItem])
                except IndexError:
                    logging.debug(f'No item called {item_name} was found')

    def __cboResourceNodeItem_changed(self, cbo):
        if self.blueprint and self.blueprint.selected \
            and isinstance(self.blueprint.selected, ResourceNode):
                item_name = cbo.get_active_id()
                try:
                    item = [ item for name, item in get_all_items() \
                        if name == item_name][0]
                    self.blueprint.selected.item = item
                    self.unsaved_changes = True
                    self.update_window(skip=[self.cboResourceNodeItem])
                except IndexError:
                    logging.debug(f'No item called {item_name} was found')

    def __cboResourceNodePurity_changed(self, cbo):
        if self.blueprint and self.blueprint.selected \
            and isinstance(self.blueprint.selected, ResourceNode):
                purity_name = cbo.get_active_id()
                try:
                    purity = [ purity for name, purity in Purity.__members__.items()
                        if name == purity_name ][0]
                    self.blueprint.selected.purity = purity
                    self.unsaved_changes = True
                    self.update_window(skip=[self.cboResourceNodePurity])
                except IndexError:
                    logging.debug(f'No item called {item_name} was found')

    def __btnConnection_clicked(self, btn):
        wdwConnection = ConnectionManagementWindow(
            self,
            btn.tags['component'],
            btn.tags['connection'],
            btn.tags['connection_index'],
            self.__wdwConnection_closed)

    def __wdwConnection_closed(self, response: ConnectionManagementWindowResponse):
        # If a change is to be made, dig up the things the response indicates
        if response.changed:
            self.blueprint.draw_locked = True
            source_component = None
            source_conn = None
            target_component = None
            target_conn = None
            old_target_component = None
            old_target_conn = None

            # Get the source component and connection objects
            if None not in [response.source_component_id, response.source_connection_index]:
                source_component = self.blueprint.factory.get_component_by_id(
                    response.source_component_id)
                source_connections = source_component.outputs \
                    if response.source_connection_is_output \
                    else source_component.inputs
                source_conn = source_connections[response.source_connection_index]

            # Get the target component and connection objects
            if None not in [response.target_component_id, response.target_connection_index]:
                target_component = self.blueprint.factory.get_component_by_id(
                    response.target_component_id)
                target_connections = target_component.inputs \
                    if response.source_connection_is_output \
                    else target_component.outputs
                target_conn = target_connections[response.target_connection_index]

            # Get the old target component and connection objects
            if None not in [response.old_target_component_id, response.old_target_connection_index]:
                old_target_component = self.blueprint.factory.get_component_by_id(
                    response.old_target_component_id)
                old_target_connections = old_target_component.inputs \
                    if response.source_connection_is_output \
                        else old_target_component.outputs
                old_target_conn = old_target_connections[response.old_target_connection_index]

            # If the connection hasn't changed...
            if old_target_conn is not None and old_target_conn == target_conn:
                # If the conveyance type hasn't changed...
                if response.conveyance_class == type(source_conn.remote.attached_to):
                    # Then don't do anything, only unlock the drawing routines
                    self.blueprint.draw_locked = False
                    return

            # If there's an existing connection, we have to detect it and get rid of it
            old_conveyance = None
            if old_target_component is not None:
                # If the connection isn't between a miner and resource node, then there is a
                # conveyance we need to delete before building the new connection.
                if not (issubclass(source_component.__class__, Miner) and source_conn.is_input()) \
                    and not isinstance(source_component, ResourceNode):
                        old_conveyance, *_ = source_conn.connected_to()

                # Clear that conveyance out of everywhere we store info about it.
                if old_conveyance is not None:
                    old_conveyance.inputs[0].source.target = None
                    old_conveyance.outputs[0].target.source = None
                    self.blueprint.remove_component(old_conveyance.id)
                else:
                    # There is no conveyance between the source and existing target. Just disconnect
                    # them manually.
                    if source_conn.is_output():
                        source_conn.target.source = None
                        source_conn.target = None
                    else:
                        source_conn.source.target = None
                        source_conn.source = None

            # If the response indicates a connection to be made, create that connection
            if source_conn and target_conn:
                # If the connection is between a miner and resource node, connect them directly
                if issubclass(source_component.__class__, Miner) and \
                    isinstance(target_component, ResourceNode):
                        source_conn.connect(target_conn)
                elif isinstance(source_component, ResourceNode) and \
                    issubclass(target_component.__class__, Miner):
                        source_conn.connect(target_conn)
                # If the connection is between any other kind of component, connect them using a conveyance
                else:
                    new_conveyance = response.conveyance_class()
                    if response.source_connection_is_output:
                        source_conn.connect(new_conveyance.inputs[0])
                        new_conveyance.outputs[0].connect(target_conn)
                    else:
                        source_conn.connect(new_conveyance.outputs[0])
                        new_conveyance.inputs[0].connect(target_conn)
                    self.blueprint.add_component(new_conveyance, Coordinate2D())

        # Make sure the changes get drawn
        self.blueprint.invalidate_geometry()
        self.blueprint.draw_locked = False
        self.factoryDesigner.queue_draw()

    # + Component tagging widget signal handlers

    def __boxComponentTags_changed(self):
        self.unsaved_changes = True
        self.update_window(skip=[self.boxComponentTags])

    # + Component danger zone signal handlers

    def __btnDeleteComponent_clicked(self, btn):
        if self.blueprint and self.blueprint.selected:
            dlgConfirmComponentDelete = ConfirmOrCancelWindow(
                self,
                'Delete Component?',
                f'Delete {self.blueprint.selected.name}?',
                self.__dlgConfirmComponentDelete_responded)

    def __dlgConfirmComponentDelete_responded(self, confirmed: bool):
        if confirmed and self.blueprint and self.blueprint.selected:
            comp = self.blueprint.selected

            # Delete any conveyances connecting the components' connections
            for conn in comp.inputs:
                source_output = conn.source
                if source_output:
                    attached_to = source_output.attached_to
                    # attached_to should be a conveyance. We need to find what that's connected to
                    if attached_to:
                        source_building = attached_to.inputs[0].source.attached_to
                        source_building.outputs[0].target = None
                        self.blueprint.remove_component(attached_to.id)
            for conn in comp.outputs:
                target_input = conn.target
                if target_input:
                    attached_to = conn.target.attached_to
                    if attached_to:
                        target_building = attached_to.outputs[0].target.attached_to
                        target_building.inputs[0].source = None
                        self.blueprint.remove_component(attached_to.id)

            # Delete the component itself, deselect everything, update the window
            self.blueprint.remove_component(comp.id)
            self.blueprint.selected = None
            self.unsaved_changes = True
            self.update_window()
