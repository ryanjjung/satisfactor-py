#!/bin/env python3

GTK_APP_ID="com.github.ryanjjung.satisfactor_py"

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(1000, 800)
        self.set_title('Satisfactory Designer')
        self.__build_layout()

    def __build_layout(self):
        # Build a vertical box layout to give us a strip on top for factory tools
        self.boxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.btnTop = Gtk.Button(label='Top')
        self.boxMain.append(self.btnTop)

        # Build the main split panel container
        self.paneMain = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxMain.append(self.paneMain)

        # Build the left-hand frame containing the list of buildings
        self.frameBuildings = Gtk.Frame()
        self.paneMain.set_start_child(self.frameBuildings)
        self.paneMain.set_position(200)

        # Build the right-hand frame, which will be further split
        self.frameRightLayout = Gtk.Frame()
        self.paneMain.set_end_child(self.frameRightLayout)
        self.paneMain.set_vexpand(True)

        # Split the right panel into two more panels
        self.paneRightLayout = Gtk.Paned()
        self.paneRightLayout.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.frameRightLayout.set_child(self.paneRightLayout)

        # Build out the right two panels
        self.frameFactory = Gtk.Frame()
        self.frameInfo = Gtk.Frame()
        self.paneRightLayout.set_start_child(self.frameFactory)
        self.paneRightLayout.set_end_child(self.frameInfo)
        self.paneRightLayout.set_position(600)


        self.btnBuildings = Gtk.Button(label='Buildings')
        self.frameBuildings.set_child(self.btnBuildings)

        self.btnFactory = Gtk.Button(label='Factory')
        self.frameFactory.set_child(self.btnFactory)

        self.btnInfo = Gtk.Button(label='Info')
        self.frameInfo.set_child(self.btnInfo)

        self.set_child(self.boxMain)


class FactoryDesigner(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.mainWindow = MainWindow(application=app)
        self.mainWindow.present()

