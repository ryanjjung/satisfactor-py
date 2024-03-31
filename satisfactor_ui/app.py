#!/bin/env python3

GTK_APP_ID="com.github.ryanjjung.satisfactor_py"

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk
from satisfactor_py.base import Availability


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(1000, 800)
        self.set_title('Satisfactory Designer')
        self.__build_window()

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
    
    def __cboTier_changed(self, cbo):
        self.cboUpgrade.remove_all()
        for upgrade in Availability.get_upgrade_strings(self.cboTier.get_active()):
            self.cboUpgrade.append(upgrade, upgrade)

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


class FactoryDesigner(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.mainWindow = MainWindow(application=app)
        self.mainWindow.present()

