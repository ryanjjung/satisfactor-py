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
from satisfactor_py.storages import get_all as get_all_storages
from satisfactor_ui.dialogs import ConfirmDiscardChangesWindow


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

        logging.debug('Initiating main window')
        self.factory = None
        self.factoryFile = None
        self.unsaved_changes = False
        self.updating = False

        self.filters = {
            'availability': True,
            'building_category': False,
            'name': False
        }

        self.set_default_size(width, height)
        self.__build_ui_helpers()
        self.__build_window()

        if filename:
            self.load_factory(filename)
        else:
            self.update_window()


    # Common Functions

    def block_all_signals(self):
        '''
        Places a block on all signal handlers, preventing them from emitting events until you run
        unblock_all_signals.
        '''

        logging.debug('Blocking all signals')
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
            logging.debug('Initializing buildings list')
            ALL_BUILDINGS = [ ResourceNode(), InfiniteSupplyNode() ]
            ALL_BUILDINGS.extend([ bldg() for bldg in get_all_buildings()])
            ALL_BUILDINGS.extend([ bldg() for bldg in get_all_conveyances()])
            ALL_BUILDINGS.extend([ bldg() for bldg in get_all_storages()])
        return ALL_BUILDINGS

    def load_factory(self, filename: str):
        '''
        Opens a factory file for use with the application and triggers a UI update.
        '''

        try:
            # Load the factory and store it in the class as separate actions,
            # resulting in no change if an exception is thrown at load time.
            logging.debug(f'Loading factory from file {filename}')
            loadedFactory = Factory.load(filename)
            self.factoryFile = filename
            self.factory = loadedFactory
            self.unsaved_changes = False
            self.update_window()
        except IOError as ex:
            logging.error(f'An error occurred when loading a factory from file {filename}\n  {ex}')
            # TODO: Replace with an actual ErrorDialog

    def set_tier_and_upgrade(self,
        tier: int = None,
        upgrade: int = None
    ):
        '''
        Sets the active values in the combo boxes for tier and upgrade

            - tier: The tier to set the factory unlock level to
            - upgrade: The upgrade level to set in the factory
        '''

        if self.factory:
            self.block_all_signals()
            # Update the factory model first
            if tier is not None:
                self.factory.tier = tier
            if upgrade:
                self.factory.upgrade = upgrade
            logging.debug(f'Selecting tier/upgrade values: {self.factory.tier}/{self.factory.upgrade}')

            # Set the tier value in the combo box
            self.cboTier.set_active(self.factory.tier)

            # Populate the appropriate upgrade values
            self.cboUpgrade.remove_all()
            for upgrade in Availability.get_upgrade_strings(self.factory.tier):
                self.cboUpgrade.append(upgrade, upgrade)
            self.cboUpgrade.set_active(self.factory.upgrade - 1)
            self.unblock_all_signals()

    def set_window_title(self):
        '''
        Update the window's title appropriately
        '''

        logging.debug('Setting window title')
        title_prefix = f'{"*" if self.unsaved_changes else ""}'
        title_suffix = f' ({self.factoryFile.split('/')[-1]})' if self.factoryFile else ''
        self.set_title(f'{title_prefix}{MAIN_WINDOW_TITLE_BASE}{title_suffix}')

    def unblock_all_signals(self):
        '''
        Removes a block from all signal handlers, restoring their ability to emit signals. These
        signals were likely placed by block_all_signals.
        '''

        logging.debug('Unblocking all signals')
        for handler in self.windowSignals:
            GObject.signal_handler_unblock(handler[0], handler[1])

    def update_buildings_list(self):
        '''
        Updates the list of buildings in the left panel, taking into account all filters.
        '''

        if self.factory:
            logging.debug('Updating building options list')
            # Determine the available buildings
            all_buildings = MainWindow.get_building_options()
            if self.filters['availability']:
                avail_buildings = []
                for building in all_buildings:
                    if self.factory.tier > building.availability.tier:
                        avail_buildings.append(building)
                    elif self.factory.tier == building.availability.tier:
                        if self.factory.upgrade >= building.availability.upgrade:
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

    def update_window(self):
        '''
        When the factory context of the MainWindow changes, call this function to update all of the
        UI elements depending on that context.
        '''

        logging.debug('Updating window')
        if not self.updating:
            self.updating = True
            self.block_all_signals()
            self.set_window_title()
            if self.factory:
                self.btnSaveFactory.set_sensitive(self.unsaved_changes)
                self.boxFactoryFunctions.set_sensitive(True)
                self.boxFilters.set_sensitive(True)
                self.entryFactoryName.get_buffer().set_text(self.factory.name, -1)
                self.set_tier_and_upgrade()
                self.update_buildings_list()
            else:
                self.btnSaveFactory.set_sensitive(False)
                self.boxFactoryFunctions.set_sensitive(False)
                self.boxFilters.set_sensitive(False)
            self.unblock_all_signals()
            self.updating = False


    # Layout Construction

    def __build_window(self):
        '''
        Builds the contents of the main window. A strip of application/factory-level functions appear
        across the top. A column along the left displays building options. A column along the right
        displays info based on the current context. A space through the middle is the main factory
        designer area.
        '''

        logging.debug('Building the main window')
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
        self.paneLeft.set_position(600)
        self.paneLeft.set_vexpand(True)

        # Build the right-hand panel as another split panel
        self.paneRight = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paneRight.set_position(800)
        self.paneLeft.set_end_child(self.paneRight)

        # Build the center panel containing the factory designer
        lblDesigner = Gtk.Label(label='Factory Designer')  # Placeholder
        self.paneRight.set_start_child(lblDesigner)

        # Build the content of the right-hand context panel
        lblContext = Gtk.Label(label='Context Info')  # Placeholder
        self.paneRight.set_end_child(lblContext)

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

        logging.debug('Building widgets for building options')
        # Start with two vertical panes
        self.paneBuildingsOptions = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.paneBuildingsOptions.set_position(150)

        # Top pane: filtering options for the bottom pane
        self.scrollBuildingFilters = Gtk.ScrolledWindow()
        self.boxFilters = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxFilters.set_spacing(10)

        # Top pane: Factory availability checkbox
        self.chkAvailability = Gtk.CheckButton(label='Availability')
        self.chkAvailability.set_active(True)
        self.boxFilters.append(self.chkAvailability)
        self.scrollBuildingFilters.set_child(self.boxFilters)

        # Top pane: Building Category selection
        self.boxBuildingCategory = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.chkBuildingCategory = Gtk.CheckButton(label='Building category: ')
        self.cboBuildingCategory = Gtk.ComboBoxText()
        for category in BuildingCategory:
            self.cboBuildingCategory.append(category.name, category.name.title())

        self.boxBuildingCategory.append(self.chkBuildingCategory)
        self.boxBuildingCategory.append(self.cboBuildingCategory)
        self.boxFilters.append(self.boxBuildingCategory)

        # Top pane: Name filter
        self.boxNameFilter = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.chkNameFilter = Gtk.CheckButton(label='Name: ')
        self.entryNameFilter = Gtk.Entry()
        self.boxNameFilter.append(self.chkNameFilter)
        self.boxNameFilter.append(self.entryNameFilter)
        self.boxFilters.append(self.boxNameFilter)

        # Bottom pane: list of buildings
        self.scrollBuildings = Gtk.ScrolledWindow()
        self.icovwBuildings = Gtk.IconView()
        self.icovwBuildings.set_spacing(10)
        self.scrollBuildings.set_child(self.icovwBuildings)
        self.scrollBuildings.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Compile panel contents
        self.paneBuildingsOptions.set_start_child(self.scrollBuildingFilters)
        self.paneBuildingsOptions.set_end_child(self.scrollBuildings)

    def __build_top_bar(self):
        '''
        Builds the UI controls which run across the top bar of the window.
        '''

        logging.debug('Building the top bar')

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

        # Contain all the factory-level functions within a box so they can all be enabled and
        # disabled by doing so to this one widget
        self.boxFactoryFunctions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxFactoryFunctions.set_sensitive(True if self.factory else False)
        self.boxTopBar.append(self.boxFactoryFunctions)

        # Build the text box showing the name of the factory
        self.entryFactoryName = Gtk.Entry()
        self.entryFactoryName.set_size_request(300, -1)
        self.boxFactoryFunctions.append(self.entryFactoryName)

        # Build the controls allowing tier/upgrade selection
        self.lblTierUpgrade = Gtk.Label(label='Tier/Upgrade:')
        self.lblTierUpgrade.set_margin_start(10)
        self.lblTierUpgrade.set_margin_end(10)
        self.boxFactoryFunctions.append(self.lblTierUpgrade)

        # The "Tier" combo box is populated from the satisfactor_py.base.Availability class
        self.cboTier = Gtk.ComboBoxText()
        for tier in Availability.get_tier_strings():
            self.cboTier.append(tier, tier)
        self.cboTier.set_active(0)
        self.boxFactoryFunctions.append(self.cboTier)

        # The "/" character between the combo boxes
        self.lblTierUpgradeSlash = Gtk.Label(label='/')
        self.boxFactoryFunctions.append(self.lblTierUpgradeSlash)

        # The "Upgrade" combo box gets populated based on the "Tier" selection
        self.cboUpgrade = Gtk.ComboBoxText()
        self.__cboTier_changed(self.cboUpgrade)
        self.boxFactoryFunctions.append(self.cboUpgrade)

        return self.boxTopBar

    def __connect_handlers(self):
        '''
        Connects signals for the widgets on this window. This is done as a separate task after the
        window has been fully constructed. This prevents signals from being emitted before the
        window is functional.
        '''

        logging.debug('Connecting widget signals')

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

        logging.debug('Loading images')
        pixbuf = Pixbuf()
        self.pixelBuffers = {}
        building_pixbufs = {}
        all_buildings = MainWindow.get_building_options()
        for building in all_buildings:
            imageFile = Path(f'./static/images/{building.__class__.__name__}.png')
            if imageFile.exists():
                pb = pixbuf.new_from_file_at_size(str(imageFile), 64, 64)
            else:
                pb = None
            building_pixbufs[building.__class__.__name__] = pb
        self.pixelBuffers['building_options'] = building_pixbufs

    def __build_ui_helpers(self):
        '''
        Builds reusable items which are unique to this application
        '''

        logging.debug('Building resuable UI helpers')
        self.satFileFilter = Gtk.FileFilter()
        self.satFileFilter.set_name('SatisFactories (*.sat)')
        self.satFileFilter.add_pattern('*.sat')
        self.fileFilters = Gio.ListStore.new(Gtk.FileFilter)
        self.fileFilters.append(self.satFileFilter)
        self.__load_images()


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
            self.factory = Factory(name='New Factory')
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
            factoryFile = dlg.open_finish(response)
            self.load_factory(factoryFile.get_path())
        except Exception as ex:
            print(f'[DEBUG] Couldn\'t finish open: {ex}')

    # + "Save" button signal handlers
    def __btnSaveFactory_clicked(self, btn):
        '''
        The user has clicked the "Save" button
        '''

        if self.unsaved_changes:
            self.factory.save(self.factoryFile)
            self.unsaved_changes = False
            self.set_window_title()

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
        The user clicked "Save As" and then either selected a file (response is True) or canceled
        the window (response is False).
        '''

        if response:
            try:
                # Try the save first so we don't change the app context if it fails
                factoryFile = dlg.save_finish(response).get_path()
                self.factory.save(factoryFile)
                self.factoryFile = factoryFile
                self.unsaved_changes = False
                self.update_window()
            except IOError as ex:
                print(f'[DEBUG] Error saving factory at file {factoryFile}:\n  {ex}')
                # TODO: Replace with real error dialog
            except Exception as ex:
                print(f'[DEBUG] Could not finish the save action: {ex}')


    # + Factory Name Entry signal handlers

    def __entryFactoryName_deleted(self, buffer, position, chars):
        newName = self.entryFactoryName.get_buffer().get_text()
        if newName != self.factory.name and newName != '':
            self.factory.name = buffer.get_text()
            self.unsaved_changes = True
            self.update_window()

    def __entryFactoryName_inserted(self, buffer, position, chars, nchars):
        newName = self.entryFactoryName.get_buffer().get_text()
        if newName != self.factory.name and newName != '':
            self.factory.name = buffer.get_text()
            self.unsaved_changes = True
            self.update_window()

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
        self.factory.upgrade = self.cboUpgrade.get_active() + 1
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

