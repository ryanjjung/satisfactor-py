#!/bin/env python3

GTK_APP_ID="com.github.ryanjjung.satisfactor_py"

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio
from satisfactor_py.base import Availability
from satisfactor_py.factories import Factory
from satisfactor_ui.dialogs import ConfirmDiscardChangesWindow


APP_ID='com.github.ryanjjung.satisfactory.FactoryDesigner'
MAIN_WINDOW_DEFAULT_WIDTH = 1000
MAIN_WINDOW_DEFAULT_HEIGHT = 800
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

        self.factory = None
        self.factoryFile = None
        self.unsaved_changes = False

        self.set_default_size(width, height)
        self.__ui_helpers()
        self.__build_window()

        if filename:
            self.load_factory(filename)
        else:
            self.update_window_after_factory_change()


    # Common Functions

    def confirm_discard(self, callback):
        '''
        Presents a GTKDialog asking the user if it's okay to discard unsaved changes.
        '''

        dlgDiscardChanges = ConfirmDiscardChangesWindow(self, callback)
        dlgDiscardChanges.present()

    def load_factory(self, filename: str):
        '''
        Opens a factory file for use with the application and triggers a UI update.
        '''

        try:
            # Load the factory and store it in the class as separate actions,
            # resulting in no change if an exception is thrown at load time.
            loadedFactory = Factory.load(filename)
            self.factoryFile = filename
            self.factory = loadedFactory
            self.unsaved_changes = False
            self.update_window_after_factory_change()
        except IOError as ex:
            print(f'[DEBUG] An error occurred when loading a factory from file {filename}\n  {ex}')
            # TODO: Replace with an actual ErrorDialog

    def set_window_title(self):
        '''
        Update the window's title appropriately
        '''

        title_prefix = f'{"*" if self.unsaved_changes else ""}'
        title_suffix = f' ({self.factoryFile.split('/')[-1]})' if self.factoryFile else ''
        self.set_title(f'{title_prefix}{MAIN_WINDOW_TITLE_BASE}{title_suffix}')

    def update_window_after_factory_change(self, skipFactoryName: bool = False):
        '''
        When the factory context of the MainWindow changes, call this function to update all of the
        UI elements depending on that context.
        '''

        self.set_window_title()
        if self.factory:
            self.btnSaveFactory.set_sensitive(self.unsaved_changes)
            self.boxFactoryFunctions.set_sensitive(True)
            if not skipFactoryName:
                self.entryFactoryName.get_buffer().set_text(self.factory.name, -1)
            self.cboTier.set_active(self.factory.tier)
            self.__cboTier_changed(self.cboTier)
            self.cboUpgrade.set_active(self.factory.upgrade - 1)
        else:
            self.btnSaveFactory.set_sensitive(False)
            self.boxFactoryFunctions.set_sensitive(False)


    # Layout Construction

    def __build_window(self):
        '''
        Builds the contents of the main window. A strip of application/factory-level functions appear
        across the top. A column along the left displays building options. A column along the right
        displays info based on the current context. A space through the middle is the main factory
        designer area.
        '''

        # Build a vertical box layout to give us a strip on top for factory tools
        self.boxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxMain.append(self.__top_bar())

        # Add the main split panel container on the bottom of the vbox
        self.paneLeft = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxMain.append(self.paneLeft)

        # Build the left-hand panel containing the list of buildings
        self.lblBuildings = Gtk.Label(label='Buildings Options')
        self.paneLeft.set_start_child(self.lblBuildings)
        self.paneLeft.set_position(200)
        self.paneLeft.set_vexpand(True)

        # Build the right-hand panel as another split panel
        self.paneRight = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paneRight.set_position(600)
        self.paneLeft.set_end_child(self.paneRight)

        # Build the center panel containing the factory designer
        lblDesigner = Gtk.Label(label='Factory Designer')  # Placeholder
        self.paneRight.set_start_child(lblDesigner)

        # Build the content of the right-hand context panel
        lblContext = Gtk.Label(label='Context Info')  # Placeholder
        self.paneRight.set_end_child(lblContext)

        # The main vbox becomes the top level element on the window
        self.set_child(self.boxMain)


    def __top_bar(self):
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
        self.btnNewFactory.connect('clicked', self.__btnNewFactory_clicked)

        # Build the "Open" button
        self.btnOpenFactory = Gtk.Button()
        self.btnOpenFactory.set_icon_name('document-open')
        self.btnOpenFactory.connect('clicked', self.__btnOpenFactory_clicked)

        # Build the "Save" button
        self.btnSaveFactory = Gtk.Button()
        self.btnSaveFactory.set_icon_name('document-save')
        self.btnSaveFactory.connect('clicked', self.__btnSaveFactory_clicked)

        # Build the "Save As" button
        self.btnSaveFactoryAs = Gtk.Button()
        self.btnSaveFactoryAs.set_icon_name('document-save-as')
        self.btnSaveFactoryAs.connect('clicked', self.__btnSaveFactoryAs_clicked)

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
        self.entryFactoryName.get_buffer().connect_after('deleted-text',
            self.__entryFactoryName_deleted)
        self.entryFactoryName.get_buffer().connect('inserted-text',
            self.__entryFactoryName_inserted)
        self.boxFactoryFunctions.append(self.entryFactoryName)

        # Build the controls allowing tier/upgrade selection
        self.lblTierUpgrade = Gtk.Label(label='Tier/Upgrade:')
        self.lblTierUpgrade.set_margin_end(10)
        self.boxFactoryFunctions.append(self.lblTierUpgrade)

        # The "Tier" combo box is populated from the satisfactor_py.base.Availability class
        self.cboTier = Gtk.ComboBoxText()
        for tier in Availability.get_tier_strings():
            self.cboTier.append(tier, tier)
        self.cboTier.set_active(0)
        self.cboTier.connect('changed', self.__cboTier_changed)
        self.boxFactoryFunctions.append(self.cboTier)

        # The "/" character between the combo boxes
        self.lblTierUpgradeSlash = Gtk.Label(label='/')
        self.boxFactoryFunctions.append(self.lblTierUpgradeSlash)

        # The "Upgrade" combo box gets populated based on the "Tier" selection
        self.cboUpgrade = Gtk.ComboBoxText()
        self.__cboTier_changed(self.cboUpgrade)
        self.boxFactoryFunctions.append(self.cboUpgrade)

        return self.boxTopBar

    def __ui_helpers(self):
        '''
        Builds reusable items which are unique to this application
        '''

        self.satFileFilter = Gtk.FileFilter()
        self.satFileFilter.set_name('SatisFactories (*.sat)')
        self.satFileFilter.add_pattern('*.sat')
        self.fileFilters = Gio.ListStore.new(Gtk.FileFilter)
        self.fileFilters.append(self.satFileFilter)

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
            self.update_window_after_factory_change()


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
            self.update_window_after_factory_change()

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
                self.update_window_after_factory_change()
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
            self.update_window_after_factory_change(skipFactoryName=True)

    def __entryFactoryName_inserted(self, buffer, position, chars, nchars):
        newName = self.entryFactoryName.get_buffer().get_text()
        if newName != self.factory.name and newName != '':
            self.factory.name = buffer.get_text()
            self.unsaved_changes = True
            self.update_window_after_factory_change(skipFactoryName=True)

    # + "Tier" combo box signal handlers
    def __cboTier_changed(self, cbo):
        '''
        The "Tier" combo box has had its value changed. We need to populate the "Upgrade" combo box
        accordingly.
        '''

        self.cboUpgrade.remove_all()
        for upgrade in Availability.get_upgrade_strings(self.cboTier.get_active()):
            self.cboUpgrade.append(upgrade, upgrade)


class FactoryDesigner(Gtk.Application):
    '''
    Top-level GTKApplication object for the factory designer
    '''

    def __init__(self, **kwargs):
        super().__init__(application_id=APP_ID, **kwargs)
        self.mainWindow = None
        self.set_flags(Gio.ApplicationFlags.HANDLES_OPEN)
        self.connect('activate', self.on_activate)
        self.connect('open', self.on_open)

    def on_activate(self, app):
        '''
        Create and display the application's main window
        '''

        if not self.mainWindow:
            self.mainWindow = MainWindow(application=app)
        self.mainWindow.present()

    def on_open(self, app, files, n_files, hint):
        '''
        Activate the main window, handling a file load at the same time
        '''

        self.on_activate(app)
        if n_files > 1:
            raise ValueError('Factory Designer can open only one factory at a time')
        self.mainWindow.load_factory(files[0].get_path())
