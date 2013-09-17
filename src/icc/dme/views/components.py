
from gi.repository import Gtk
from icc.xray.views.drawing import *
from icc.rake.views.base import ConfirmationDialog, InputDialog
import icc.rake.views.components
import icc.rake.interfaces

from interfaces import *
import zope.component

from matplotlib.figure import Figure
import matplotlib
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

import jsonpickle
import numpy

SAVE_DEPTH = 0  # 0 means 50 according to pyxser source pyxser.c


def gsm():
    return zope.component.getGlobalSiteManager()

class DMENavigatorToolbar(NavigationToolbar):
    pass


class View(icc.rake.views.components.View):
    """
    """
    resource=__name__

    def __init__(self, model=None, parent=None):
        icc.rake.views.components.View.__init__(
            self, model=model, parent=parent)

class DMEPlotView(View):
    """
    """

    template="ui/project_view.glade"
    widget_names=["data", "sim", "model", "data_box", "sim_box", "model_box"]

    def __init__(self, model=None, parent=None):
        """
        """
        #import pdb; pdb.set_trace()
        View.__init__(self, model=model, parent=parent)
        self.parent_ui=pui=gsm().getUtility(
            icc.rake.views.interfaces.IApplication
        )

        frame=self.get_main_frame()
        vbox=self.ui.sim_box

        fig = Figure(figsize=(5,4), dpi=120,
            subplotpars=matplotlib.figure.SubplotParams(
                left=0.03,
                right=0.96,
                bottom=0.03,
                top=0.96)
        )

        self.ui.fig = fig
        #self.ui.ax = fig.add_subplot(111)

        canvas=FigureCanvas(fig)
        self.ui.canvas=canvas
        canvas.set_size_request(600,400)
        vbox.pack_start(canvas, True, True, 0)
        toolbar=DMENavigatorToolbar(canvas, self)

        parent.connect("project-open", self.on_project_open)
        parent.connect("project-save", self.on_project_save)

    def on_model_changed(self, model):
        self.paint_model()

    def paint_model(self):
        model = self.model
        fig = self.ui.fig
        fig.clear()
        if not model:
            return

        self.ui.ax = ax = fig.add_subplot(111)
        ax.set_ylabel("Amount/Volumes")
        ax.set_xlabel("Years")

        t = numpy.arange(0.0,3.0,0.01)
        s = numpy.sin(2*numpy.pi*t)
        pl= ax.plot(t,s, aa=True, linewidth=0.5, alpha=0.5)

    def on_project_open(self, widget, filename):
        if 1:
        #try:
            i=open(filename, "r")
        #except IO:
        s=i.read()
        i.close()
        model=jsonpickle.decode(s)
        self.set_model(model)
        print 'Model loaded.'
        return True

    def on_project_save(self, widget, filename):
        assert (self.model != None), "the model should be not None"
        o=open(filename, "w")
        w=jsonpickle.encode(self.model)
        o.write(w)
        o.close()
        return True
