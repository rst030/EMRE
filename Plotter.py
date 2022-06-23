'''
    Ilia Kulikov
    16 June 2022
    ilia.kulikov@fu-berlin.de
plotter.
matplotlib based.
mpl window is imbedded into the parent that has to be passed to the constructor.
    '''

import matplotlib
import numpy
import cw_spectrum

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy
import math

class Plotter(FigureCanvas):
    '''Plotter based on FigureCanvasQTAgg'''
    xlabel = 'pirates'
    ylabel = 'crocodiles'
    title = 'ultimate grapfh'
    parent = None # parent widget, needs to be class var for live updates

    def __init__(self, parent=None):
        #plt.style.use('dark_background')
        fig = Figure(figsize=(16,16),dpi=100)
        self.axes = fig.add_subplot(111)
        fig.subplots_adjust(left = 0.18, right=0.99, top=0.94, bottom=0.1)
        self.compute_initial_figure()
        self.axes.grid()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.parent = parent

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.toolbar = NavigationToolbar(self, self.parent)  # nav toolbar

    def clear(self):
        self.axes.cla()

    def set_title(self,title:str):
        self.axes.set_title(title)
        self.update_plotter()

    def compute_initial_figure(self):
        self.clear()
        self.axes.plot([1,2,3],[2,3,5])
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)

    def preset_EPR(self):
        self.clear()
        self.xlabel = 'Magnetic Field [mT]'
        self.ylabel = 'EPR signal [V]'
        self.title = 'EPR [dummy]'
        # plot sample EPR
        dummy_b = [numpy.linspace(320,1,520)]
        dummy_spc = cw_spectrum.cw_spectrum(filepath='./dummies/dry_film_after_sonic_22dB_2G.akku2')
        self.plotEprData(dummy_spc)
        self.axes.grid()

    def preset_CV(self):
        self.clear()
        self.xlabel = 'Volttage [V]'
        self.ylabel = 'Current [A]'
        self.title = 'CV'
        # plot sample cv
        voltages_for_dummy_cv = [numpy.linspace(0,1,100),numpy.linspace(1,0,100)]
        currents_for_dummy_cv = numpy.sin(numpy.array(voltages_for_dummy_cv)*2*numpy.pi)
        self.plotCvData(voltages=voltages_for_dummy_cv,currents=currents_for_dummy_cv)
        self.axes.grid()



    def preset_CHG(self):
        self.clear()
        self.xlabel = 'Time [s]'
        self.ylabel = 'Voltage [V]'
        self.title = 'CHG'
        self.compute_initial_figure()

    def plotCvData(self, voltages, currents):
        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)

        self.axes.plot(voltages, currents, 'm+:', linewidth=1)
        self.axes.autoscale(True)
        self.update_plotter()

    def plotEprData(self, spectrum:cw_spectrum.cw_spectrum):
        #self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)

        self.axes.plot(spectrum.bvalues, spectrum.x_channel, 'k-', linewidth=1)
        self.axes.autoscale(True)
        self.update_plotter()


    def update_plotter(self): # very useful and important method for live plotting.
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()