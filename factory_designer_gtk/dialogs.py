import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk
from satisfactory import conveyances
from satisfactory.base import (
    BuildingType,
    Component,
    Connection,
    Conveyance,
    ConveyanceType,
    Input,
    Output,
    ResourceNode,
)
from satisfactory.buildings import Miner
from satisfactory.factories import Factory
from typing import Callable


class ConfirmOrCancelWindow(Gtk.MessageDialog):
    '''
    Creates a dialog window to show when a user is about to take a destructive action, confirming
    that they want to proceed.
    '''

    def __init__(self,
        parent: Gtk.ApplicationWindow,
        title: str,
        message: str,
        callback: Callable
    ):
        super().__init__(title=title, transient_for=parent)
        self.set_modal(True)
        self.message = message
        self.callback = callback
        self.__build_layout()
        self.show()

    def __build_layout(self):
        '''
        Builds the overall layout of the dialog
        '''

        self.boxLayout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxLayout.set_spacing(10)

        self.boxButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxButtons.set_hexpand(True)
        self.boxButtons.set_halign(Gtk.Align.CENTER)

        self.lblMessage = Gtk.Label(label=self.message)
        self.btnCancel = Gtk.Button(label='Cancel')
        self.btnCancel.connect('clicked', self.__btnCancel_clicked)
        self.btnOK = Gtk.Button(label='OK')
        self.btnOK.connect('clicked', self.__btnOK_clicked)

        self.boxLayout.append(self.lblMessage)
        self.boxLayout.append(self.boxButtons)
        self.boxButtons.append(self.btnCancel)
        self.boxButtons.append(self.btnOK)
        self.set_child(self.boxLayout)

    def __btnCancel_clicked(self, btn):
        '''
        User canceled the action. Response is False.
        '''

        self.close()
        self.callback(False)

    def __btnOK_clicked(self, btn):
        '''
        User okayed the action. Response is True.
        '''

        self.close()
        self.callback(True)


class ConnectionManagementWindowResponse(object):
    '''
    One of these gets passed into the callback function of a ConnectionManagementWindow to describe
    the outcome of the user's interaction with it.
    '''

    def __init__(self,
        changed: bool,
        connect_output: bool,
        source_component_id: str = None,
        source_connection_id: str = None,
        target_component_id: str = None,
        target_connection_id: str = None,
        conveyance_class: type = None
    ):
        self.changed = changed
        self.connect_output = connect_output
        self.source_component_id = source_component_id
        if source_connection_id is not None:
            self.source_connection_id = int(source_connection_id)
        else:
            self.source_connection_id = None
        self.target_component_id = target_component_id
        if target_connection_id is not None:
            self.target_connection_id = int(target_connection_id)
        else:
            self.target_connection_id = None
        self.conveyance_class = conveyance_class
    

class ConnectionManagementWindow(Gtk.Window):
    '''
    A window allowing a user to manage a single connection on a single component.

        - parent: The factory_designer_gtk.main_window.MainWindow to attach this modal window to.
        - component: The component whose connection we are managing.
        - connection: The connection itself
        - factory: The satisfactory.factories.Factory containing the component and other components
            which we might want to connect to.
        - callback: A function to call when this window closes. Must accept as its sole argument a
            ConnectionManagementWindowResponse.
    '''

    def __init__(self,
        parent: Gtk.ApplicationWindow,
        component: Component,
        connection: Connection,
        callback: Callable
    ):
        # Window init
        super().__init__()
        self.set_modal(True)
        self.set_transient_for(parent)

        # Internal variables
        self.callback = callback
        self.component = component
        self.connection = connection
        self.factory = parent.blueprint.factory
        self.parent = parent

        # Detect direction of the connection and get the index of the source connection
        self.connect_output = True if isinstance(connection, Output) else False
        if self.connect_output:
            self.connection_id = self.component.outputs.index(self.connection)
        else:
            self.connection_id = self.component.inputs.index(self.connection)
        
        # Set the title depending on direction
        title = f'{self.component.name}: Manage {"out" if self.connect_output else "in"}put'
        self.set_title(title)

        self.__build_layout()
        self.__connect_handlers()
        self.__update_cboComponent()
        self.__update_cboConveyance()
        self.__update_btnDisconnect()
        self.__update_btnSave()
        self.present()
    
    def __build_layout(self):
        '''
        Constructs the widgets that pack this window.
        '''

        # Create a row for selecting which component to connect to
        self.boxComponent = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxComponent.set_spacing(5)
        self.boxComponent.set_halign(Gtk.Align.CENTER)
        self.lblComponent = Gtk.Label(label='Component:')
        self.cboComponent = Gtk.ComboBoxText()
        self.btnDisconnect = Gtk.Button()
        self.btnDisconnect.set_icon_name('list-remove')
        self.boxComponent.append(self.lblComponent)
        self.boxComponent.append(self.cboComponent)
        self.boxComponent.append(self.btnDisconnect)

        # Create a row for selecting the connection on that component
        self.boxConnection = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxConnection.set_spacing(5)
        self.boxConnection.set_halign(Gtk.Align.CENTER)
        self.boxConnection.set_hexpand(True)
        self.lblConnection = Gtk.Label(label=f'{"In" if self.connect_output else "Out"}put:')
        self.cboConnection = Gtk.ComboBoxText()
        self.cboConnection.set_hexpand(True)
        self.boxConnection.append(self.lblConnection)
        self.boxConnection.append(self.cboConnection)

        # Create a row for selecting the conveyance when that's relevant
        self.boxConveyance = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxConveyance.set_spacing(5)
        self.boxConveyance.set_halign(Gtk.Align.CENTER)
        self.boxConveyance.set_hexpand(True)
        self.lblConveyance = Gtk.Label(label='Conveyance:')
        self.cboConveyance = Gtk.ComboBoxText()
        self.cboConveyance.set_hexpand(True)
        self.boxConveyance.append(self.lblConveyance)
        self.boxConveyance.append(self.cboConveyance)

        # Create a row of buttons to cancel or accept changes
        self.boxActions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxActions.set_spacing(5)
        self.boxActions.set_halign(Gtk.Align.CENTER)
        self.btnCancel = Gtk.Button(label='Cancel')
        self.btnSave = Gtk.Button(label='Save')
        self.boxActions.append(self.btnCancel)
        self.boxActions.append(self.btnSave)

        # Pack it all in a box
        self.boxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxMain.set_spacing(5)
        self.boxMain.set_margin_bottom(10)
        self.boxMain.set_margin_top(10)
        self.boxMain.set_margin_start(10)
        self.boxMain.set_margin_end(10)
        self.boxMain.append(self.boxComponent)
        self.boxMain.append(self.boxConnection)
        self.boxMain.append(self.boxConveyance)
        self.boxMain.append(self.boxActions)

        # Pack the box into the window
        self.set_child(self.boxMain)

    def __connect_handlers(self):
        '''
        Connect signals from these widgets to their handlers.
        '''

        self.cboComponent.connect('changed', self.__cboComponent_changed)
        self.cboConnection.connect('changed', self.__cboConnection_changed)
        self.cboConveyance.connect('changed', self.__cboConveyance_changed)
        self.btnCancel.connect('clicked', self.__btnCancel_clicked)
        self.btnSave.connect('clicked', self.__btnSave_clicked)
        self.btnDisconnect.connect('clicked', self.__btnDisconnect_clicked)
    
    def __update_btnDisconnect(self):
        '''
        Sets the appropriate sensitivity for the disconnect button.
        '''

        if self.connect_output:
            if self.connection.target:
                self.btnDisconnect.set_sensitive(True)
            else:
                self.btnDisconnect.set_sensitive(False)
        else:
            if self.connection.source:
                self.btnDisconnect.set_sensitive(True)
            else:
                self.btnDisconnect.set_sensitive(False)

    def __update_btnSave(self):
        '''
        Sets the appropriate sensitivity for the disconnect button.
        '''

        selections = [
            self.cboComponent.get_active_id(),
            self.cboConnection.get_active_id(),
            self.cboConveyance.get_active_id()]

        # If all selections are made, allow saving
        if all(selections):
            self.btnSave.set_sensitive(True)
        # If no selections are made, allow saving (meaning we will disconnect)
        elif all([False if selection else True for selection in selections]):
            self.btnSave.set_sensitive(True)
        else:
            self.btnSave.set_sensitive(False)

    def __update_cboComponent(self):
        '''
        Finds all possible connections in the factory which are compatible with the connection the
        user is trying to wire up, then populates self.cboComponent with those options. Sets a value
        if there's already a connection.
        '''

        # Detect compatible components with disconnected, compatible connections
        self.available_connections = {}
        for component in self.factory.components:
            if component == self.component:
                continue
            if issubclass(component.__class__, Conveyance):
                continue
            connections = component.inputs if self.connect_output else component.outputs
            avail_conn_ids = []
            for i in range(len(connections)):
                # Filter out unsupported conveyance types
                if connections[i].conveyance_type != self.connection.conveyance_type:
                    continue
                # If we are connecting an Output, it must be targeting an Input, and therefore we
                # have to check that Connection's target to see if it's connected.
                if self.connect_output:
                    logging.debug(f'Component: {component}; connections[i]: {connections[i]}')
                    logging.debug(f'Source: {connections[i].source}')
                    if not connections[i].source:
                        avail_conn_ids.append(i)
                else:
                    if not connections[i].target:
                        avail_conn_ids.append(i)
                
            if len(avail_conn_ids) > 0:
                self.available_connections[component.id] = avail_conn_ids

        # Populate the component drop-down with a list of potential components
        self.cboComponent.remove_all()
        for component_id in self.available_connections.keys():
            target_component = self.factory.get_component_by_id(component_id)
            self.cboComponent.append(component_id, target_component.name)

        # If the connection is already connected, set the right component
        target_component = None
        if self.connect_output:
            if self.connection.target:
                target_component = self.connection.target.attached_to
        else:
            if self.connection.source:
                target_component = self.connection.source.attached_to
        # This emits a signal that causes cboConnections to update
        if target_component:
            self.cboComponent.set_active_id(target_component.id)
        
    def __update_cboConveyance(self):
        if issubclass(self.component.__class__, Miner) and isinstance(self.connection, Input):
            self.boxConveyance.set_visible(False)
        elif isinstance(self.component, ResourceNode):
            self.boxConveyance.set_visible(False)
        else:
            # Create dummy instances of the conveyances so we can get at their properties
            compatible_conveyances = [ conv() for conv in conveyances.get_all() ]

            # Filter by type
            compatible_conveyances = [ conv for conv in compatible_conveyances
                if conv.conveyance_type == self.connection.conveyance_type ]

            # Filter by availability if that's turned on
            if self.parent.chkAvailability.get_active():
                compatible_conveyances = [ conv for conv in compatible_conveyances
                    if conv.availability.tier <= self.factory.availability.tier
                    and conv.availability.upgrade <= self.factory.availability.upgrade ]
            
            # Build contents of cboConveyance and show it
            self.cboConveyance.remove_all()
            for conv in compatible_conveyances:
                self.cboConveyance.append(conv.programmatic_name, conv.name)
            self.boxConveyance.set_visible(True)

    # Signal handlers

    def __btnCancel_clicked(self, btn):
        self.close()
        # Report no change, ignore other values
        self.callback(ConnectionManagementWindowResponse(False, self.connect_output))
    
    def __btnDisconnect_clicked(self, btn):
        self.cboComponent.set_active_id(None)
        self.cboConveyance.set_active_id(None)
        self.__update_btnSave()

    def __btnSave_clicked(self, btn):
        self.close()

        # Report a change to the assembled values
        conveyance_class = None
        if not (issubclass(self.component.__class__, Miner) \
            and isinstance(self.connection, Input)) \
            and not isinstance(self.component, ResourceNode):
                conveyance_class = getattr(conveyances, self.cboConveyance.get_active_id())

        self.callback(ConnectionManagementWindowResponse(
            True,
            self.connect_output,
            source_component_id=self.component.id,
            source_connection_id=self.connection_id,
            target_component_id=self.cboComponent.get_active_id(),
            target_connection_id=self.cboConnection.get_active_id(),
            conveyance_class=conveyance_class))
    
    def __cboComponent_changed(self, cbo):
        '''
        When the component changes, we update the list of connections that are available
        '''
        
        selected_component_id = self.cboComponent.get_active_id()
        if selected_component_id:
            selected_component = self.factory.get_component_by_id(selected_component_id)
            self.cboConnection.remove_all()
            for i in range(len(self.available_connections[selected_component_id])):
                self.cboConnection.append(str(i), str(i + 1))
            conns = selected_component.inputs if self.connect_output else selected_component.outputs
            try:
                conn_id = None
                if self.connect_output:
                    if self.connection.target:
                        conn_id = conns.index(self.connection.target)
                else:
                    if self.connection.source:
                        conn_id = conns.index(self.connection.source)
                if conn_id is not None:
                    self.cboConnection.set_active_id(str(conn_id))
            except ValueError:
                pass
        else:
            self.cboConnection.remove_all()
        
        self.__update_btnDisconnect()
        self.__update_btnSave()
    
    def __cboConnection_changed(self, cbo):
        self.__update_btnSave()

    def __cboConveyance_changed(self, cbo):
        self.__update_btnSave()