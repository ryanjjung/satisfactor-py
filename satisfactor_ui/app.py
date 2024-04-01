#!/bin/env python3

GTK_APP_ID="com.github.ryanjjung.satisfactor_py"

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio
from satisfactor_py.base import Availability
from satisfactor_py.factories import Factory
from satisfactor_ui.dialogs import ConfirmDiscardChangesWindow


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, filename=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.factory = None
        self.unsaved_changes = True
        if filename:
            self.__load_factory(filename)
        self.set_default_size(1000, 800)
        self.set_title('Satisfactory Designer')
        self.__build_window()

    def load_factory(self, filename):
        self.factory = Factory.load(filename) if filename else None
        self.window_update_for_factory_change()

    def window_update_for_factory_change(self):
        self.set_title(f'Satisfactory Designer ({self.factory.name})')
        self.boxTopBar.set_sensitive(True)
        self.cboTier.set_active(self.factory.tier)
        self.__cboTier_changed(self.cboTier)
        self.cboUpgrade.set_active(self.factory.upgrade - 1)

    # Layout construction

    def __build_window(self):
        '''
        Builds the contents of the main window. A strip of factory-level functions appear across
        the top. A column along the left displays building options. A column along the right
        displays info based on the current context. A space through the middle is the main factory
        designer area.
        '''

        # Build a vertical box layout to give us a strip on top for factory tools
        self.boxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxMain.append(self.__top_bar())

        # Build the main split panel container
        self.paneLeft = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxMain.append(self.paneLeft)

        # Build the left-hand panel containing the list of buildings
        self.lblBuildings = Gtk.Label(label='Buildings Options')
        self.paneLeft.set_start_child(self.lblBuildings)
        self.paneLeft.set_position(200)
        self.paneLeft.set_vexpand(True)

        # Build the right-hand panel, containing context info
        self.paneRight = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paneRight.set_position(600)
        self.paneLeft.set_end_child(self.paneRight)

        lblDesigner = Gtk.Label(label='Factory Designer')  # Placeholder
        self.paneRight.set_start_child(lblDesigner)

        lblContext = Gtk.Label(label='Context Info')  # Placeholder
        self.paneRight.set_end_child(lblContext)

        self.set_child(self.boxMain)

    def __top_bar(self):
        '''
        Builds the UI controls which run across the top bar of the window.
        '''

        self.boxTopBar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxTopBar.set_spacing(10)
        self.boxTopBar.set_margin_top(10)
        self.boxTopBar.set_margin_bottom(10)
        self.boxTopBar.set_margin_start(10)
        self.boxTopBar.set_margin_end(10)
        self.boxTopBar.set_sensitive(True if self.factory else False)

        self.btnNewFactory = Gtk.Button()
        self.btnNewFactory.set_icon_name('document-new')
        self.btnNewFactory.connect('clicked', self.__btnNew_clicked)

        self.btnOpenFactory = Gtk.Button()
        self.btnOpenFactory.set_icon_name('document-open')
        self.btnOpenFactory.connect('clicked', self.__btnOpen_clicked)

        self.btnSaveFactory = Gtk.Button()
        self.btnSaveFactory.set_icon_name('document-save')
        self.btnSaveFactory.connect('clicked', self.__btnSave_clicked)

        self.boxTopBar.append(self.btnNewFactory)
        self.boxTopBar.append(self.btnOpenFactory)
        self.boxTopBar.append(self.btnSaveFactory)

        self.lblTierUpgrade = Gtk.Label(label='Tier/Upgrade:')
        self.boxTopBar.append(self.lblTierUpgrade)

        self.cboTier = Gtk.ComboBoxText()
        for tier in Availability.get_tier_strings():
            self.cboTier.append(tier, tier)
        self.cboTier.set_active(0)
        self.boxTopBar.append(self.cboTier)

        self.lblTierUpgradeSlash = Gtk.Label(label='/')
        self.boxTopBar.append(self.lblTierUpgradeSlash)

        self.cboUpgrade = Gtk.ComboBoxText()
        self.__cboTier_changed(self.cboUpgrade)
        self.boxTopBar.append(self.cboUpgrade)

        self.cboTier.connect('changed', self.__cboTier_changed)

        return self.boxTopBar

    # Widget action hooks

    def __cboTier_changed(self, cbo):
        self.cboUpgrade.remove_all()
        for upgrade in Availability.get_upgrade_strings(self.cboTier.get_active()):
            self.cboUpgrade.append(upgrade, upgrade)

    def __btnNew_clicked(self, btn):
        if self.unsaved_changes:
            self.newFactoryDiscardChangesDialog = ConfirmDiscardChangesWindow(self)
            self.newFactoryDiscardChangesDialog.connect('response',
                self.__newFactoryDiscardChangesDialog_response)
            self.newFactoryDiscardChangesDialog.present()

    def __newFactoryDiscardChangesDialog_response(self, dialog, user_data):
        if dialog.response == True:
            self.factory = Factory(name='New Factory')
            self.window_update_for_factory_change()

    def __btnOpen_clicked(self, btn):
        print('btnOpen clicked')

    def __btnSave_clicked(self, btn):
        print('btnSave clicked')


class FactoryDesigner(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mainWindow = None
        self.set_flags(Gio.ApplicationFlags.HANDLES_OPEN)
        self.connect('activate', self.on_activate)
        self.connect('open', self.on_open)

    def on_activate(self, app):
        if not self.mainWindow:
            self.mainWindow = MainWindow(application=app)
        self.mainWindow.present()

    def on_open(self, app, files, n_files, hint):
        self.on_activate(app)
        if n_files > 1:
            raise ValueError('Factory Designer can open only one factory at a time')
        self.mainWindow.load_factory(files[0].get_path())
