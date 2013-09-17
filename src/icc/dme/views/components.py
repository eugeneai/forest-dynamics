
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
import types

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
    widget_names=["data", "sim", "model", "data_box", "sim_box", "model_box", "ag_simulation"]

    def __init__(self, model=None, parent=None):
        """
        """
        View.__init__(self, model=model, parent=parent)
        self.parent_ui=pui=gsm().getUtility(
            icc.rake.views.interfaces.IApplication
        )


        self.add_actions_to_toolbar(self.ui.ag_simulation, important_only=False)
        self.add_actions_to_menu(self.ui.ag_simulation, label="Simulation")

        frame=self.get_main_frame()
        vbox=self.ui.sim_box

        fig = Figure(figsize=(5,4), dpi=120,
            subplotpars=matplotlib.figure.SubplotParams(
                left=0.1,
                right=0.96,
                bottom=0.1,
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

    def on_model_changed(self, view, model):
        self.paint_model()

    def paint_model(self):
        model = self.model
        fig = self.ui.fig
        fig.clear()
        if not model or not model.prepared:
            return

        self.ui.ax = ax = fig.add_subplot(111)
        ax.set_ylabel("Amount/Volumes")
        ax.set_xlabel("Years")

        t = model.modeller.trajectories.time

        def _plot(name, val):
            pl= ax.plot(t, val, aa=True, linewidth=0.5, alpha=0.9, label=name)

        def _each(model_parameter, pref=[]):
            if type(model_parameter) == types.InstanceType:
                for k in model_parameter.keys():
                    v = model_parameter.item(k)
                    _each(v, pref=pref+[k])
            else:
                _plot(".".join(pref), model_parameter)

        _each(model.result.plot)

        ax.grid(b=True, aa=False, alpha=0.3)
        ax.minorticks_on()

        FONT_SIZE=7
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(FONT_SIZE)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(FONT_SIZE)

        legend=ax.legend(
            loc="center right",
            shadow=True)
        # Set the fontsize
        for label in legend.get_texts():
            label.set_fontsize(FONT_SIZE)

        for label in legend.get_lines():
            label.set_linewidth(0.5)  # the legend line width

        self.ui.canvas.draw_idle()

    def on_project_open(self, widget, filename):
        if 1:
        #try:
            i=open(filename, "r")
        #except IO:
        s=i.read()
        i.close()
        model=jsonpickle.decode(s)
        model.prepared=False
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

    def on_ac_simulate_activate(self, widget):
        print "Simulation"
        model=self.model
        model.simulate()
        if model.computed:
            self.invalidate_model(self.model)
