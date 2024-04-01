import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk


#class ConfirmDiscardChangesWindow(Gtk.Window):
class ConfirmDiscardChangesWindow(Gtk.MessageDialog):
    '''
    Creates a dialog window to show when a user is about to take a destructive action, confirming
    that they want to proceed.
    '''

    def __init__(self, parent: Gtk.ApplicationWindow):
        super().__init__(title='Discard Unsaved Changes', transient_for=parent)
        self.set_modal(True)
        self.response = None
        self.__build_layout()
        self.show()

    def __build_layout(self):
        self.boxLayout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.boxLayout.set_spacing(10)

        self.boxButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boxButtons.set_hexpand(True)
        self.boxButtons.set_halign(Gtk.Align.CENTER)

        self.lblMessage = Gtk.Label(label='You have unsaved changes. Proceed?')
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
        self.response = False
        self.close()

    def __btnOK_clicked(self, btn):
        self.response = True
        self.close()
