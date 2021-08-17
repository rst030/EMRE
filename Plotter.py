
'''
 Created on Mar 6, 2018

 @author: Ilia Kulikov
'''
# =============================================================================== #
# TODO: Write this plotter properly! it should be able to plot points, plot lines and plot datasets

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

#import mplcyberpunk # cyberpunk style
#plt.style.use("cyberpunk")
#mplcyberpunk.add_glow_effects()

import cw_spectrum

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import Frame, BOTH, NW, TOP
import numpy as np

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

    liveaxis_x = 0 # to be assigned in add_live_plot x component
    liveaxis_y = 0 # to be assigned in add_live_plot y component

    averaged_axis_x = 0 # same here
    averaged_axis_y = 0  # same here

    liveline = 0 # live plotting
    averaged_line = 0 # live plotting of averaged data

    OFFSET_FOR_LIVE_DATA_X = 1e-4 # for nice plotting
    OFFSET_FOR_LIVE_DATA_Y = 2e-4  # for nice plotting
    OFFSET_FOR_AVERAGED_DATA_X = 3e-4  # offset for x
    OFFSET_FOR_AVERAGED_DATA_Y = 4e-4  # offset for x

    def __init__(self, rootframe: Frame):

        plt.style.use('dark_background')
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
        linex = ax1.plot(spectrum.bvalues, spectrum.x_channel, linewidth=1.0, color='cyan')
        liney = ax1.plot(spectrum.bvalues, spectrum.y_channel, linewidth=1.0, color='yellow')
        linex[0].set_visible(True)
        liney[0].set_visible(True)

        self.x_lines.append(linex) # x chan = blue
        self.y_lines.append(liney) # y chan = red

        self.update()

    def add_live_plot(self,bstart,bstop): # adding axes for the live plot. plot live data on this axes
        if self.liveaxis_x == 0:
            self.liveaxis_x = self.subplot.twinx()
        self.clear_live_plot_x() # when add new live plot old plot goes away
        self.liveaxis_x.set_xlim(bstart, bstop)
        self.liveaxis_x.autoscale(False)
        self.liveaxis_x.set_ylim(-1e-2, 1e-2)


        if self.liveaxis_y == 0:
            self.liveaxis_y = self.subplot.twinx()
        self.clear_live_plot_y()  # when add new live plot old plot goes away
        self.liveaxis_y.set_xlim(bstart, bstop)
        self.liveaxis_x.autoscale(False)
        self.liveaxis_y.set_ylim(-1e-2, 1e-2)

        self.update()

    def plot_live_data_x(self,xs,ys): # plot live data on the live axes.
        self.liveaxis_x.cla()
        self.liveline = self.liveaxis_x.plot(xs,ys,'r-', linewidth=0.45)
        self.liveaxis_x.autoscale(False)

        #self.set_y_limits_of_x_live_axis(low + self.OFFSET_FOR_LIVE_DATA_X, high + self.OFFSET_FOR_LIVE_DATA_X)

        self.update()

    def plot_live_data_y(self,xs,ys): # plot live data on the live axes.
        self.liveaxis_y.cla()
        self.liveline = self.liveaxis_y.plot(xs,ys,color = 'lime', linewidth=0.45)
        self.liveaxis_y.autoscale(False)
        #if high > low:
        #    self.set_y_limits_of_y_live_axis(low  + self.OFFSET_FOR_LIVE_DATA_Y, high + self.OFFSET_FOR_LIVE_DATA_Y)

        #self.update()


    def add_average_plot(self, bstart, bstop):

        if self.averaged_axis_x == 0:
            self.averaged_axis_x=self.subplot.twinx()
        self.averaged_axis_x.set_xlim(bstart, bstop)

        if self.averaged_axis_y == 0:
            self.averaged_axis_y = self.subplot.twinx()
        self.averaged_axis_y.set_xlim(bstart, bstop)

        self.update()


    def set_y_limits_of_x_averaged_axis(self, low,high):
        self.averaged_axis_x.set_ylim([low,high])

    def set_y_limits_of_y_averaged_axis(self, low,high):
        self.averaged_axis_y.set_ylim([low,high])

    def set_y_limits_of_x_live_axis(self, low,high):
        self.averaged_axis_x.set_ylim([low,high])

    def set_y_limits_of_y_live_axis(self, low,high):
        self.averaged_axis_y.set_ylim([low,high])



    def plot_averaged_data(self, list_of_cw_spectra: [cw_spectrum.cw_spectrum]):
        '''it plots in the special averaged_axis_x and axis_y '''

        if len(list_of_cw_spectra) > 0:

            # If something is in the list:
            container = list_of_cw_spectra[0]
            bvalues = np.array(container.bvalues)
            averaged_signal_x = np.array(container.x_channel) * 0
            averaged_signal_y = np.array(container.y_channel) * 0
            # lets average now

            for sctrm in list_of_cw_spectra: # going through the list of cw_spectra
                averaged_signal_x = averaged_signal_x + np.array(sctrm.x_channel)
                averaged_signal_y = averaged_signal_y + np.array(sctrm.y_channel)

            averaged_signal_x = averaged_signal_x/(len(list_of_cw_spectra)+1) # normalization
            averaged_signal_y = averaged_signal_y/(len(list_of_cw_spectra)+1) # normalization

            self.averaged_axis_x.cla()
            self.averaged_axis_y.cla()

            self.averaged_line_x = self.averaged_axis_x.plot(bvalues, averaged_signal_x, 'y-', linewidth=0.2)
            self.averaged_line_y = self.averaged_axis_y.plot(bvalues, averaged_signal_y, 'c-', linewidth=0.2)

#            self.set_y_limits_of_x_averaged_axis(min(averaged_signal_x)+self.OFFSET_FOR_AVERAGED_DATA_X,max(averaged_signal_x)+self.OFFSET_FOR_AVERAGED_DATA_X)
#            self.set_y_limits_of_y_averaged_axis(min(averaged_signal_y)+self.OFFSET_FOR_AVERAGED_DATA_Y, max(averaged_signal_y)+self.OFFSET_FOR_AVERAGED_DATA_Y)

            self.update()


    def set_visibility_of_selected_spectrum_compon(self, spectrum: cw_spectrum.cw_spectrum, component: str, show: bool):
        # clear the corresponding axes and plot only x component of the spectrum. Stupid but what can I do?!
        #get_current_axis of the spectrum. It is its index.
        linex = self.x_lines[spectrum.index]
        liney = self.y_lines[spectrum.index]  # crooked numbering of lines

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

        linex = ax1.plot(spectrum.bvalues, spectrum.x_channel, linewidth=1.0, color='white')
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
        self.update()




    #def set_live_xlim(self,xstart,xstop):
    #    self.subplot.set_xlim(xstart, xstop)
    #    self.update()
    #    #self.subplot.autoscale(False)

    def plot_data(self,xs, ys, arg):
        self.subplot.plot(xs, ys, arg)

    def clear_live_plot_x(self):
        self.liveaxis_x.clear()

        self.liveline_x = []

    def clear_live_plot_y(self):
        self.liveaxis_y.clear()

        self.liveline_y = []


    def clear_plot(self):
        self.subplot.cla()
        self.set_title(self.title)
        self.set_axes(self.xlabel, self.ylabel)

    def update(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

