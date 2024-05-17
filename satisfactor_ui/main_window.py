import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject
from gi.repository.GdkPixbuf import Pixbuf
from pathlib import Path
from satisfactor_py.base import (
    Availability,
    BuildingCategory,
    ResourceNode,
    InfiniteSupplyNode
)
from satisfactor_py.buildings import get_all as get_all_buildings
from satisfactor_py.conveyances import get_all as get_all_conveyances
from satisfactor_py.factories import Factory
from satisfactor_py.items import get_all as get_all_items
from satisfactor_py.recipes import get_all as get_all_recipes
from satisfactor_py.storages import get_all as get_all_storages
from satisfactor_ui.dialogs import ConfirmDiscardChangesWindow
from satisfactor_ui.drawing import Blueprint
from satisfactor_ui.widgets import FactoryDesignerWidget


ALL_BUILDINGS = None
MAIN_WINDOW_DEFAULT_WIDTH = 1920
MAIN_WINDOW_DEFAULT_HEIGHT = 1080
MAIN_WINDOW_TITLE_BASE = 'Satisfactory Designer'


class MainWindow(Gtk.ApplicationWindow):
    '''
    The main factory designer window.

      - filename: A file created by satisfactor_py.factories.Factory.save which the window is to be
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
        unblock_all_signals.
        '''

        for handler in self.windowSignals:
            GObject.signal_handler_block(handler[0], handler[1])

    def confirm_discard(self, callback):
        '''
        Presents a GTKDialog asking the user if it's okay to discard unsaved changes.
        '''

        dlgDiscardChanges = ConfirmDiscardChangesWindow(self, callback)
        dlgDiscardChanges.present()

    @staticmethod
    def get_building_options():
        '''
        Returns a list of all buildings the library is aware of; caches the result for quick access.
        '''

        global ALL_BUILDINGS
        if ALL_BUILDINGS is None:
            ALL_BUILDINGS = [ ResourceNode(), InfiniteSupplyNode() ]
            ALL_BUILDINGS.extend([ bldg() for bldg in get_all_buildings()])
            ALL_BUILDINGS.extend([ bldg() for bldg in get_all_conveyances()])
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
            self.factoryDesigner.blueprint = self.blueprint
            self.unsaved_changes = False
            self.update_window()
        except IOError as ex:
            logging.error(f'An error occurred when loading a blueprint from file {filename}\n  {ex}')
            # TODO: Replace with an actual ErrorDialog

    def set_component_context(self):
        '''
        Populates the widgets in the component context panels.
        '''

        if self.blueprint and self.blueprint.selected:
            # Update the availability display
            c = self.blueprint.selected  # This just makes the rest of this code read better
            self.lblComponentAvailability.set_text(
                f'Available at Tier {c.availability.tier}, Upgrade {c.availability.upgrade}')

            # Recipe displays show an item image and the amount/rate
            recipe_store = Gtk.ListStore(Pixbuf, str)

            # Get the recipe to build the component
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
                        self.pixelBuffers['items'][ingredient.item.programmatic_name],
                        f'{ingredient.amount}x {ingredient.item.name}'))
                self.icovwComponentRecipe.set_model(recipe_store)
                self.icovwComponentRecipe.set_pixbuf_column(0)
                self.icovwComponentRecipe.set_text_column(1)
                self.boxComponentRecipe.append(self.lblComponentRecipe)
                self.boxComponentRecipe.append(self.icovwComponentRecipe)

            # Update the links
            self.linkWiki.set_uri(c.wiki_url)
            self.linkImage.set_uri(c.image_url)

            # Clear out the old connection data
            for icovw in self.icovwInputs:
                self.boxComponentInputs.remove(icovw)
            for icovw in self.icovwOutputs:
                self.boxComponentOutputs.remove(icovw)

            # Update inputs and outputs
            self.boxComponentInputs.remove(self.lblInputs)
            self.icovwInputs = []
            for conn in c.inputs:
                icovw = Gtk.IconView()
                store = Gtk.ListStore(Pixbuf, str)
                for ingredient in conn.ingredients:
                    store.append((
                        self.pixelBuffers['items'][ingredient.item.programmatic_name],
                        f'{ingredient.rate}x {ingredient.item.name} /m'
                    ))
                icovw.set_model(store)
                icovw.set_pixbuf_column(0)
                icovw.set_text_column(1)
                self.icovwInputs.append(icovw)

            if len(self.icovwInputs) > 0:
                self.boxComponentInputs.append(self.lblInputs)
            for icovw in self.icovwInputs:
                self.boxComponentInputs.append(icovw)

            self.boxComponentOutputs.remove(self.lblOutputs)
            self.icovwOutputs = []
            for conn in c.outputs:
                icovw = Gtk.IconView()
                store = Gtk.ListStore(Pixbuf, str)
                for ingredient in conn.ingredients:
                    store.append((
                        self.pixelBuffers['items'][ingredient.item.programmatic_name],
                        f'{ingredient.rate}x {ingredient.item.name} /m'
                    ))
                icovw.set_model(store)
                icovw.set_pixbuf_column(0)
                icovw.set_text_column(1)
                self.icovwOutputs.append(icovw)

            if len(self.icovwOutputs) > 0:
                self.boxComponentOutputs.append(self.lblOutputs)
            for icovw in self.icovwOutputs:
                self.boxComponentOutputs.append(icovw)

            self.boxComponentReadOnlyDetails.set_visible(True)
        else:
            self.boxComponentReadOnlyDetails.set_visible(False)

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
        signals were likely placed by block_all_signals.
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

            # Convert the list to a ListStore, pulling in images where possible
            listStore = Gtk.ListStore(Pixbuf, str)
            for building in avail_buildings:
                listStore.append((
                    self.pixelBuffers['building_options'][building.__class__.__name__],
                    building.name))
            self.lstBuildings = listStore
            self.icovwBuildings.set_model(self.lstBuildings)
            self.icovwBuildings.set_pixbuf_column(0)
            self.icovwBuildings.set_text_column(1)

    def update_window(self,
        skip_entryFactoryName: bool = False
    ):
        '''
        When the factory context of the MainWindow changes, call this function to update all of the
        UI elements depending on that context.
        '''

        self.block_all_signals()
        self.set_window_title()
        self.set_component_context()

        # Set availability of various widgets
        if self.blueprint:
            self.boxFactoryFunctions.set_sensitive(True)
            self.btnSaveFactory.set_sensitive(self.unsaved_changes)
            self.boxFilters.set_sensitive(True)
            if not skip_entryFactoryName:
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

        # Bottom pane: list of buildings
        self.scrollBuildings = Gtk.ScrolledWindow()
        self.icovwBuildings = Gtk.IconView()
        self.icovwBuildings.set_spacing(5)
        self.scrollBuildings.set_child(self.icovwBuildings)
        self.scrollBuildings.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Compile panel contents
        self.paneBuildingsOptions.set_start_child(self.scrollBuildingFilters)
        self.paneBuildingsOptions.set_end_child(self.scrollBuildings)

    def __build_component_context_panel(self):
        '''
        Builds the right-side panel containing info about the selected component.
        '''

        # editable
        #   - name
        #   - tags
        #   - constructed
        #   - processing recipe
        #   - clock_rate
        #   - standby
        #   - dimensions
        #   - base power usage

        # Build a panel sorting contents on read-only or editable traits
        self.paneComponentDetails = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.paneComponentDetails.set_position(400)

        # Wrap everything in a scrollable view
        self.scrollComponentReadOnlyDetails = Gtk.ScrolledWindow()
        self.scrollComponentEditableDetails = Gtk.ScrolledWindow()

        # Set up read-only details in a box
        self.boxComponentReadOnlyDetails = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxComponentReadOnlyDetails.set_margin_start(5)
        self.boxComponentReadOnlyDetails.set_margin_end(5)
        self.boxComponentReadOnlyDetails.set_margin_bottom(5)
        self.boxComponentReadOnlyDetails.set_margin_top(5)

        # Place a header
        self.lblComponentHeader = Gtk.Label()
        self.lblComponentHeader.set_markup('<b>Component Details</b>')
        self.boxComponentReadOnlyDetails.append(self.lblComponentHeader)

        self.lblComponentAvailability = Gtk.Label(label='')

        self.boxComponentRecipe = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.lblComponentRecipe = Gtk.Label(label='Component Build Cost:')
        self.lblComponentRecipe.set_margin_top(10) # Put a little visual space here
        self.icovwComponentRecipe = Gtk.IconView()
        self.icovwComponentRecipe.set_item_orientation(Gtk.Orientation.HORIZONTAL)
        self.boxComponentRecipe.append(self.lblComponentRecipe)
        self.boxComponentRecipe.append(self.icovwComponentRecipe)

        self.boxComponentReadOnlyDetails.append(self.lblComponentAvailability)
        self.boxComponentReadOnlyDetails.append(self.boxComponentRecipe)

        self.boxComponentLinks = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponentLinks.set_halign(Gtk.Align.CENTER)
        self.lblLinks = Gtk.Label(label='Links:')
        self.linkWiki = Gtk.LinkButton().new_with_label(uri='', label='Wiki')
        self.linkImage = Gtk.LinkButton().new_with_label(uri='', label='Image')
        self.boxComponentLinks.append(self.lblLinks)
        self.boxComponentLinks.append(self.linkWiki)
        self.boxComponentLinks.append(self.linkImage)
        self.boxComponentReadOnlyDetails.append(self.boxComponentLinks)

        # Connections
        self.boxComponentInputs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.lblInputs = Gtk.Label(label='Inputs')
        self.icovwInputs = [Gtk.IconView()]
        self.boxComponentInputs.append(self.lblInputs)
        self.boxComponentInputs.append(self.icovwInputs[0])

        self.boxComponentOutputs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.lblOutputs = Gtk.Label(label='Outputs')
        self.icovwOutputs = [Gtk.IconView()]
        self.boxComponentOutputs.append(self.lblOutputs)
        self.boxComponentOutputs.append(self.icovwOutputs[0])

        self.boxComponentReadOnlyDetails.append(self.boxComponentInputs)
        self.boxComponentReadOnlyDetails.append(self.boxComponentOutputs)

        # Set up editable details
        self.boxComponentEditableDetails = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxComponentEditableDetails.set_margin_start(5)
        self.boxComponentEditableDetails.set_margin_end(5)
        self.boxComponentEditableDetails.set_margin_bottom(5)
        self.boxComponentEditableDetails.set_margin_top(5)
        self.lblComponentEditableDetails = Gtk.Label(label='Component Editable Details')
        self.boxComponentEditableDetails.append(self.lblComponentEditableDetails)

        # Add it all to the scrollwindow
        self.scrollComponentReadOnlyDetails.set_child(self.boxComponentReadOnlyDetails)
        self.scrollComponentEditableDetails.set_child(self.boxComponentEditableDetails)

        # Fill the panes
        self.paneComponentDetails.set_start_child(self.scrollComponentReadOnlyDetails)
        self.paneComponentDetails.set_end_child(self.scrollComponentEditableDetails)

    def __build_context_panel(self):
        '''
        Builds the bottom panel showing context about the factory and selected component.
        '''

        self.paneContext = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.__build_factory_context_panel()
        self.paneContext.set_start_child(self.scrollFactoryFunctions)

        self.__build_component_context_panel()
        self.paneContext.set_end_child(self.paneComponentDetails)
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

        # The "Tier" combo box is populated from the satisfactor_py.base.Availability class
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

        # Add all the buttons to the main hbox
        self.boxTopBar.append(self.btnNewFactory)
        self.boxTopBar.append(self.btnOpenFactory)
        self.boxTopBar.append(self.btnSaveFactory)
        self.boxTopBar.append(self.btnSaveFactoryAs)

        return self.boxTopBar

    def __build_ui_helpers(self):
        '''
        Builds reusable items which are unique to this application
        '''

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
        '''

        # Signals for widgets in the top bar containing factory-level options
        self.windowSignals.append((
            self.btnNewFactory,
            self.btnNewFactory.connect('clicked', self.__btnNewFactory_clicked)))
        self.windowSignals.append((
            self.btnOpenFactory,
            self.btnOpenFactory.connect('clicked', self.__btnOpenFactory_clicked)))
        self.windowSignals.append((
            self.btnSaveFactory,
            self.btnSaveFactory.connect('clicked', self.__btnSaveFactory_clicked)))
        self.windowSignals.append((
            self.btnSaveFactoryAs,
            self.btnSaveFactoryAs.connect('clicked', self.__btnSaveFactoryAs_clicked)))
        self.windowSignals.append((
            self.entryFactoryName.get_buffer(),
            self.entryFactoryName.get_buffer().connect_after('deleted-text',
                self.__entryFactoryName_deleted)))
        self.windowSignals.append((
            self.entryFactoryName.get_buffer(),
            self.entryFactoryName.get_buffer().connect('inserted-text',
                self.__entryFactoryName_inserted)))
        self.windowSignals.append((
            self.cboTier,
            self.cboTier.connect_after('changed', self.__cboTier_changed)))
        self.windowSignals.append((
            self.cboUpgrade,
            self.cboUpgrade.connect('changed', self.__cboUpgrade_changed)))

        # Signals for the building options filter panel
        self.windowSignals.append((
            self.chkAvailability,
            self.chkAvailability.connect_after('toggled', self.__chkAvailability_toggled)
        ))
        self.windowSignals.append((
            self.chkBuildingCategory,
            self.chkBuildingCategory.connect_after('toggled', self.__chkBuildingCategory_toggled)
        ))
        self.windowSignals.append((
            self.cboBuildingCategory,
            self.cboBuildingCategory.connect_after('changed', self.__cboBuildingCategory_changed)
        ))
        self.windowSignals.append((
            self.chkNameFilter,
            self.chkNameFilter.connect_after('toggled', self.__chkNameFilter_toggled)
        ))
        self.windowSignals.append((
            self.entryNameFilter.get_buffer(),
            self.entryNameFilter.get_buffer().connect_after('deleted-text',
                self.__entryNameFilter_deleted)
        ))
        self.windowSignals.append((
            self.entryNameFilter.get_buffer(),
            self.entryNameFilter.get_buffer().connect_after('inserted-text',
                self.__entryNameFilter_inserted)
        ))

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


    # + Factory Name Entry signal handlers

    def __entryFactoryName_deleted(self, buffer, position, chars):
        newName = self.entryFactoryName.get_buffer().get_text()
        if newName != self.blueprint.factory.name:
            self.blueprint.factory.name = buffer.get_text()
            self.unsaved_changes = True
            self.update_window(skip_entryFactoryName=True)

    def __entryFactoryName_inserted(self, buffer, position, chars, nchars):
        newName = self.entryFactoryName.get_buffer().get_text()
        if newName != self.blueprint.factory.name and newName != '':
            self.blueprint.factory.name = buffer.get_text()
            self.unsaved_changes = True
            self.update_window(skip_entryFactoryName=True)

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
        self.blueprint.upgrade = self.cboUpgrade.get_active() + 1
        self.unsaved_changes = True
        self.update_window()

    # + Building option filters signal handlers
    def __chkAvailability_toggled(self, chk):
        self.filters['availability'] = chk.get_active()
        self.update_buildings_list()

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

