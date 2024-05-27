import logging
logging.basicConfig(level=logging.DEBUG)

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import GObject, Gtk
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
        source_component_id: str = None,
        source_connection_index: int = None,
        source_connection_is_output: bool = None,
        target_component_id: str = None,
        target_connection_index: int = None,
        conveyance_class: type = None
    ):
        self.changed = changed
        self.source_component_id = source_component_id
        self.source_connection_is_output = source_connection_is_output
        self.target_component_id = target_component_id

        # The index values are sourced from a ComboBoxText which uses strings.
        # We have to convert them back into ints.
        if source_connection_index is not None:
            self.source_connection_index = int(source_connection_index)
        else:
            self.source_connection_index = None
        if target_connection_index is not None:
            self.target_connection_index = int(target_connection_index)
        else:
            self.target_connection_index = None
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
        connection_index: int,
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
        self.connection_index = connection_index
        self.factory = parent.blueprint.factory
        self.parent = parent

        # Set the title depending on direction
        title = f'{self.component.name}: Manage {"out" if self.connection.is_output() else "in"}put'
        self.set_title(title)

        # Get the known connection if one exists
        connected_comp, connected_conn, connected_conn_id = \
            self.connection.connected_to(skip_conveyances=True)
        if connected_comp is not None:
            self.current_connection = {
                'component': connected_comp,
                'connection': connected_conn,
                'connection_index': connected_conn_id }
        else:
            self.current_connection = None

        self.__build_layout()
        self.__connect_handlers()
        self.__update_available_connections()


        # Determine if any values should be set at init time
        active_component = None
        active_connection = None
        active_conveyance = None
        if self.current_connection:
            active_component = self.current_connection['component']
            active_connection = str(self.current_connection['connection_index'])

            # The active conveyance is only set if the connection is connected to a conveyance
            closest_comp, closest_conn, closest_conn_id = \
                self.connection.connected_to()
            if closest_comp is not None and issubclass(closest_comp.__class__, Conveyance):
                active_conveyance = closest_comp.__class__.__name__

        # Update all the widgets appropriately
        self.__block_all_signals()
        self.__update_cboComponent(active_id=active_component.id if active_component else None)
        self.__update_cboConnection(active_id=active_connection)
        self.__update_cboConveyance(active_id=active_conveyance)
        self.__update_btnSave()
        self.__unblock_all_signals()
        self.present()


    # Aggregate signal manipulation functions

    def __block_all_signals(self):
        for handler in self.windowSignals:
            GObject.signal_handler_block(handler[0], handler[1])

    def __unblock_all_signals(self):
        for handler in self.windowSignals:
            GObject.signal_handler_unblock(handler[0], handler[1])


    # Window construction and widget manipulation

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
        self.lblConnection = Gtk.Label(
            label=f'{"In" if self.connection.is_output() else "Out"}put:')
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

        self.windowSignals = [
            (self.cboComponent, self.cboComponent.connect('changed', self.__cboComponent_changed)),
            (self.cboConnection, self.cboConnection.connect('changed', self.__cboConnection_changed)),
            (self.cboConveyance, self.cboConveyance.connect('changed', self.__cboConveyance_changed)),
            (self.btnCancel, self.btnCancel.connect('clicked', self.__btnCancel_clicked)),
            (self.btnSave, self.btnSave.connect('clicked', self.__btnSave_clicked)),
            (self.btnDisconnect, self.btnDisconnect.connect('clicked', self.__btnDisconnect_clicked)),
        ]

    def __update_available_connections(self):
        # Start our list with all available compabible connections in the factory
        available_connections = self.factory.get_available_connections(
            compatible_with=self.connection)

        # Merge the current connection into the available connections
        if self.current_connection is not None:
            if self.current_connection['component'].id in available_connections:
                available_connections[self.current_connection['component'].id].append(
                    self.current_connection)
            else:
                available_connections[self.current_connection['component'].id] = \
                    [self.current_connection]

        self.available_connections = available_connections

    def __update_btnSave(self):
        '''
        Sets the appropriate sensitivity for the Save button.
        '''

        selections = [
            self.cboComponent.get_active_id(),
            self.cboConnection.get_active_id()]

        if self.boxConveyance.get_visible():
            selections.append(self.cboConveyance.get_active_id())

        # If all selections are made, allow saving
        if all(selections):
            self.btnSave.set_sensitive(True)
        # If no selections are made, allow saving (meaning we will disconnect)
        elif all([False if selection else True for selection in selections]):
            self.btnSave.set_sensitive(True)
        else:
            self.btnSave.set_sensitive(False)

    def __update_cboComponent(self, active_id: str = None):
        '''
        Populates cboComponent with valid values. If active_id is set, selects that entry.
        '''

        self.cboComponent.remove_all()
        for component_id, conn_data in self.available_connections.items():
            self.cboComponent.append(
                component_id,
                self.factory.get_component_by_id(component_id).name)
        self.cboComponent.set_active_id(active_id)

    def __update_cboConnection(self, active_id: str = None):
        '''
        Populates cboConnection with valid values. If active_id is set, selects that entry.
        '''

        self.cboConnection.remove_all()
        target_component_id = self.cboComponent.get_active_id()
        if target_component_id:
            for conn_data in self.available_connections[target_component_id]:
                index = conn_data['connection_index']
                self.cboConnection.append(str(index), str(index + 1))
        self.cboConnection.set_active_id(active_id)

    def __update_cboConveyance(self, active_id: str = None):
        '''
        Populates cboConveyance with a list of conveyance types, sometimes subject to the
        availability filter. If active_id is set, selects that entry. If the connection being set up
        is between a Miner and Resource Node, these options are not presented to the user.
        '''

        if (issubclass(self.component.__class__, Miner) and self.connection.is_input()) \
            or isinstance(self.component, ResourceNode):
                self.boxConveyance.set_visible(False)
                self.cboConveyance.set_active_id(None)
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
                self.cboConveyance.append(conv.__class__.__name__, conv.name)
            self.cboConveyance.set_active_id(active_id)
            self.boxConveyance.set_visible(True)


    # Signal handlers

    def __btnCancel_clicked(self, btn):
        self.close()
        # Report no change, ignore other values
        self.callback(ConnectionManagementWindowResponse(False))

    def __btnDisconnect_clicked(self, btn):
        self.cboComponent.set_active_id(None)
        self.cboConnection.set_active_id(None)
        self.cboConveyance.set_active_id(None)
        self.__update_btnSave()

    def __btnSave_clicked(self, btn):
        self.close()

        # Report a change to the assembled values
        conveyance_class = None
        if self.boxConveyance.get_visible():
            active_conveyance = self.cboConveyance.get_active_id()
            if active_conveyance is not None:
                conveyance_class = getattr(conveyances, active_conveyance)

        self.callback(ConnectionManagementWindowResponse(
            True,
            source_component_id=self.component.id,
            source_connection_index=self.connection_index,
            source_connection_is_output=self.connection.is_output(),
            target_component_id=self.cboComponent.get_active_id(),
            target_connection_index=self.cboConnection.get_active_id(),
            conveyance_class=conveyance_class))

    def __cboComponent_changed(self, cbo):
        '''
        When the component changes, we update the list of connections that are available
        '''

        self.__update_cboConnection()
        self.__update_btnSave()
        # __update_btnSave is called via signal handler as a result of the above call

    def __cboConnection_changed(self, cbo):
        self.__update_btnSave()

    def __cboConveyance_changed(self, cbo):
        self.__update_btnSave()
