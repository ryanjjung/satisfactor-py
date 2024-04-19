import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject
from satisfactor_py.buildings import Foundry
import satisfactor_ui.drawing as drawing



class FactoryDesignerWidget(Gtk.Widget):
    '''
    A FactoryDesginerWidget is a GTK Widget that draws a factory's components in a 2D visible space
    and allows a user to interact with those components.
    '''

    def __init__(self,
        blueprint: drawing.Blueprint = None
    ):
        super().__init__()
        self.blueprint = blueprint if blueprint else drawing.Blueprint()

        # Test component
        self.testComponent = Foundry()
        self.blueprint.add_component(self.testComponent, drawing.Coordinate2D(50, 50))

    def do_snapshot(self,
        snapshot: Gtk.Snapshot
    ):
        '''
        Draws the entire factory designer widget
        '''

        self.blueprint.viewport.size = drawing.Size2D(self.get_width(), self.get_height())
        self.blueprint.draw_frame(snapshot)
