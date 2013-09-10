
from gi.repository import Gtk
from icc.xray.views.drawing import *
import icc.rake.views.components
import icc.rake.interfaces

from interfaces import *
import zope.component

def gsm():
    return zope.component.getGlobalSiteManager()

class DMENavigatorToolbar(NavigationToolbar):
    pass


class View(icc.rake.views.components.View):
    """
    """
    resource=__name__

    #def __init__(self, ):
    #    """
    #    """

class DMEPlotView(View):
    """
    """

    def __init__(self, parent=None, model=None):
        """
        """
        View.__init__(self, model=model, parent=parent)
        self.parent_ui=pui=gsm().getUtility(
            icc.rake.interfaces.IApplication
        )

        frame=Gtk.Frame()
        vbox=Gtk.Vbox()
        frame.add(vbox)

        fig = Figure(figsize=(5,4), dpi=120,
            subplotpars=matplotlib.figure.SubplotParams(
                left=0.03,
                right=0.96,
                bottom=0.03,
                top=0.96)
        )

        canvas=FigureCanvas(fig)
        canvas.set_size_request(600,400)
        vbox.pack_start(canvas, True, True, 0)
        toolbar=DMENavigatorToolbar(canvas, self)
        self.invalidate_model(model)
