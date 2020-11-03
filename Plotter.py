
'''
 Created on Mar 6, 2018

 @author: Ilia Kulikov
'''
#===============================================================================#
# TODO: Write this plotter properly! it should be able to plot points, plot lines and plot datasets

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import cw_spectrum

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import Frame, BOTH, NW, TOP

# you can have lines as a result of plot(). lines can ghave visibility 1 or 0. We use it for disabling spectra
class Plotter:
    title = ''
    xlabel = 'B [G]'
    ylabel = 'Intensity [a.u.]'
    figure = plt.Figure
    subplot = plt.subplot
    rootframe = Frame

    dax = [] # dartaset axes. List. each dataset is separate axes
    x_lines = [] # list of x_components
    y_lines = [] # list of y_components

    liveaxis = 0 # to be assigned in add_live_plot
    averaged_axis = 0 # same here

    liveline = 0 # live plotting
    averaged_line = 0 # live plotting of averaged data

    def __init__(self, rootframe: Frame):

        self.figure = plt.Figure(figsize=(1,1), dpi=120)
        fig = self.figure
        self.subplot = fig.add_subplot(111)

        #self.subplot = self.figure.add_subplot(111)

        #self.subplot.plot([1,20,3,1,3,2,4,1,1,1,3,2,4,1,2])
        self.subplot.set_xlabel(self.xlabel)
        self.subplot.set_ylabel(self.ylabel)
        self.subplot.set_title(self.title)
        self.frame = rootframe
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        toolbar = NavigationToolbar2Tk(self.canvas, self.frame)  # nav toolbar
        toolbar.update()

        self.canvas.get_tk_widget().pack(fill = BOTH, anchor = NW, expand = True)
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


        # implement dataframes? df.plot(kind='Chart Type such as bar', legend=True, ax=ax)

    def add_plot(self, spectrum: cw_spectrum.cw_spectrum):
        ax1 = self.subplot.twinx()
        self.dax.append(ax1)

        # plot its x component and add that line to the x_lines list
        linex = ax1.plot(spectrum.bvalues, spectrum.x_channel, linewidth=1.0, color='navy')
        liney = ax1.plot(spectrum.bvalues, spectrum.y_channel, linewidth=1.0, color='red')
        linex[0].set_visible(True)
        liney[0].set_visible(True)

        self.x_lines.append(linex) # x chan = blue
        self.y_lines.append(liney) # y chan = red

        self.update()


    def add_live_plot(self,bstart,bstop): # adding axes for the live plot. plot live data on this axes
        if self.liveaxis == 0:
            self.liveaxis = self.subplot.twinx()
        self.liveaxis.set_xlim(bstart, bstop)
        self.update()

    def plot_live_data(self,xs,ys,arg): # plot live data on the live axes.
        self.liveaxis.clear()
        self.liveline = self.liveaxis.plot(xs,ys,arg, linewidth=0.25)
        self.update()

    def add_average_plot(self, bstart, bstop):

        if self.averaged_axis == 0:
            self.averaged_axis=self.subplot.twinx()
        self.averaged_axis.set_xlim(bstart, bstop)
        self.update()

    def plot_averaged_data(self,xs,ys,arg):
        self.averaged_axis.clear()
        self.averaged_line = self.averaged_axis.plot(xs, ys, arg, linewidth=0.45)
        self.update()


    def set_visibility_of_selected_spectrum_compon(self, spectrum: cw_spectrum.cw_spectrum, component: str, show: bool):
        # clear the corresponding axes and plot only x component of the spectrum. Stupid but what can I do?!
        #get_current_axis of the spectrum. It is its index.
        linex = self.x_lines[spectrum.index]
        liney = self.y_lines[spectrum.index] #crooked numbering of lines

        if component == 'x':
            linex[0].set_visible(show)
        else:
            if component == 'y':
                liney[0].set_visible(show)
            else:
                print('only x and y components to change. check input.')

        self.update()

    def replot_axes(self, spectrum: cw_spectrum.cw_spectrum):
        # clear corresponding axes
        # plot spectrum on that axes
        ax1 = self.dax[spectrum.index]
        ax1.clear()

        linex = ax1.plot(spectrum.bvalues, spectrum.x_channel, linewidth=1.0, color='navy')
        liney = ax1.plot(spectrum.bvalues, spectrum.y_channel, linewidth=1.0, color='red')

        # also refreshing the lines in the plot.
        self.x_lines[spectrum.index] = linex
        self.y_lines[spectrum.index] = liney

        self.update()
        print("and now replot the scaled spectrum!")


    def set_title(self, title):
        self.title = title
        self.subplot.set_title(title)

    def set_axes(self,xaxis: str, yaxis: str):
        self.xlabel = xaxis
        self.ylabel = yaxis
        self.subplot.set_xlabel(xaxis)
        self.subplot.set_ylabel(yaxis)

    def plot_points(self, xs, ys, arg:str):
        self.subplot.plot(xs,ys,arg)




    def set_live_xlim(self,xstart,xstop):
        self.subplot.set_xlim(xstart, xstop)
        self.update()
        #self.subplot.autoscale(False)

    def plot_data(self,xs, ys, arg):
        self.subplot.plot(xs, ys, arg)

    def clear_plot(self):
        self.subplot.cla()
        self.set_title(self.title)
        self.set_axes(self.xlabel, self.ylabel)

    def update(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

