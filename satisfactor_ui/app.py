#!/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio
from satisfactor_ui.mainwindow import MainWindow

GTK_APP_ID="com.github.ryanjjung.satisfactor_py.FactoryDesigner"


class FactoryDesigner(Gtk.Application):
    '''
    Top-level GTKApplication object for the factory designer
    '''

    def __init__(self, **kwargs):
        logging.debug('Initializing GTK application')
        super().__init__(application_id=GTK_APP_ID, **kwargs)
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
