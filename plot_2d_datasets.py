#!/usr/bin/env python
# should work with python 3.7
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab as pl
from matplotlib.widgets import Button, RadioButtons, Slider
from matplotlib import rcParams
from numpy import unravel_index
#import scipy.interpolate # for smoothing
#import scipy.ndimage.interpolation # for smoothing
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import tkinter.ttk as ttk
import ntpath
import pprint
#import load_files
import read_transient_fu as load_files
#import data_manipulation
import os
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']


def onTableClicked(event):
    global cur_index
    if len(ds)==0:
        return
    item = tree.identify('item',event.x,event.y)
    #print("you clicked on", tree.item(item,"text"))
    #print("you clicked on", tree.item(item))
    if tree.item(item, "text") == 'single scan':
        print("you clicked on single scan "+str(tree.item(item, "values")[0]))
    else:
        print("you clicked on averaged dataset")
        cur_index = tree.index(item) # only change dataset when clicked on averaged dataset
        changeDataset(cur_index)
    #print tree.index(item)
    return

def onRadioClicked(): # background correction
    if len(ds)==0:
        return
    if bgcorrVar.get()==1: # raw data
        print("switch to raw data")
    elif bgcorrVar.get()==2: # bg-corrected data
        print("switch to bg-corrected data")
    changeDataset(cur_index)
    return

def onPhaseSwitchClicked(): # real/imaginary switch
    if len(ds)==0:
        return
    if ds[cur_index].two_ch == False:
        phaseSwitchVar.set(1) # set to real part
        return
    phaseButton.config(relief="raised") # raise phaseButton
    if phaseSwitchVar.get()==1:
        print("real part")
        ds[cur_index].data = ds[cur_index].data_real
        ds[cur_index].data_bg_corr = ds[cur_index].data_real_bg_corr
    elif phaseSwitchVar.get()==2:
        print("imaginary part")
        ds[cur_index].data = ds[cur_index].data_imag
        ds[cur_index].data_bg_corr = ds[cur_index].data_imag_bg_corr
    changeDataset(cur_index)
    return

def rephaseData(event):
    phase_string = phaseEntry.get()
    if phase_string == '':
        return
    elif ds[cur_index].two_ch == True:
        phase = float(phase_string)
        print(phase)
        phaseSwitchVar.set(0) # deselect real/imaginary switch
        phaseButton.config(relief="sunken")
        data_comp = np.array(ds[cur_index].data_real, dtype=complex) # real part
        data_comp.imag = np.array(ds[cur_index].data_imag) # imaginary part
        ds[cur_index].data = np.multiply(np.exp(-1j*np.pi*phase/180), data_comp).real
        ds[cur_index].data_bg_corr = load_files.subtractBackground(ds[cur_index].x_vec, ds[cur_index].y_vec, ds[cur_index].data, ds[cur_index].trig_pos) # background correction
        changeDataset(cur_index)
    return

def onclick(event):
    if len(ds)==0:
        return
    x_ind = np.searchsorted(ds[cur_index].x_vec,event.xdata) # get x point from measurement
    y_ind = np.searchsorted(ds[cur_index].y_vec,event.ydata) # get y point from measurement
    # prevent problems when clicked outside of plot range
    if event.xdata < np.min(ds[cur_index].x_vec) or event.xdata > np.max(ds[cur_index].x_vec):
        return
    if event.ydata < np.min(ds[cur_index].y_vec) or event.ydata > np.max(ds[cur_index].y_vec):
        return
    Dataset.x_ind = x_ind
    Dataset.y_ind = y_ind
    add_crosshair()
    refresh_ax1()
    refresh_ax2()
    refresh_slider()
    f.canvas.draw_idle()
    return

def changeDataset(index):
    ax.clear()
    if ax1.lines:
        Dataset.text1.remove()
        ax1.clear()
    if ax2.lines:
        Dataset.text2.remove()
        ax2.clear()
    ax_sl_x.clear()
    ax_sl_y.clear()

    if ds[index].two_ch == False:
        phaseSwitchVar.set(1) # set to real data for one channel datasets
    if bgcorrVar.get()==1:
        #ax.contourf(ds[index].x_vec, ds[index].y_vec, ds[index].data, 40)
        #ax.pcolorfast(ds[index].x_vec, ds[index].y_vec, ds[index].data) # much faster than contourf, cmap='bwr_r'
        #max_val = max(abs(np.max(ds[index].data)),abs(np.min(ds[index].data)))
        #ax.pcolormesh(ds[index].x_vec, ds[index].y_vec, ds[index].data, cmap='bwr', vmin=-max_val, vmax=max_val) # too slow?
        ax.pcolormesh(ds[index].x_vec, ds[index].y_vec, ds[index].data, cmap='bwr') # too slow?
        ax1.set_ylim(np.min(ds[index].data), np.max(ds[index].data))
        ax2.set_ylim(np.min(ds[index].data), np.max(ds[index].data))
        #start_pos = unravel_index(ds[index].data.argmax(), ds[index].data.shape)
        start_pos = unravel_index(np.argmax(abs(ds[index].data)), ds[index].data.shape)
        print("plot raw dataset containing " + str(ds[index].num_scans) + " scan(s)")
    elif bgcorrVar.get()==2:
        #ax.contourf(ds[index].x_vec, ds[index].y_vec, ds[index].data_bg_corr, 40)
        #ax.pcolorfast(ds[index].x_vec, ds[index].y_vec, ds[index].data_bg_corr) # much faster than contourf
        max_val = max(abs(np.max(ds[index].data_bg_corr)),abs(np.min(ds[index].data_bg_corr)))
        ax.pcolormesh(ds[index].x_vec, ds[index].y_vec, ds[index].data_bg_corr, cmap='bwr', vmin=-max_val, vmax=max_val) # too slow?
        ax1.set_ylim(np.min(ds[index].data_bg_corr), np.max(ds[index].data_bg_corr))
        ax2.set_ylim(np.min(ds[index].data_bg_corr), np.max(ds[index].data_bg_corr))
        start_pos = unravel_index(np.argmax(abs(ds[index].data_bg_corr)), ds[index].data_bg_corr.shape)
        print("plot corrected dataset containing " + str(ds[index].num_scans) + " scan(s)")

    ax.axes.relim(visible_only=True) # may or may not help to speed up
    ax.set_xlabel(ds[index].x_label)
    ax.set_ylabel(ds[index].y_label)
    
    ax1.set_xlim(np.min(ds[index].x_vec),np.max(ds[index].x_vec))
    ax1.set_xlabel(ds[index].x_label)
    ax1.set_ylabel(ds[index].z_label)
    
    ax2.set_xlim(np.min(ds[index].y_vec),np.max(ds[index].y_vec))
    ax2.set_xlabel(ds[index].y_label)
    ax2.set_ylabel(ds[index].z_label)
    
    ds[index].x_startind = start_pos[1] # determine x and y indices for max values
    ds[index].y_startind = start_pos[0]
    Dataset.x_ind = ds[index].x_startind
    Dataset.y_ind = ds[index].y_startind
    
    # add cross hairs and fill slice plots
    add_crosshair()
    if bgcorrVar.get()==1:
        Dataset.l1, = ax1.plot(ds[index].x_vec, ds[index].data[Dataset.y_ind,:], color='b')
    elif bgcorrVar.get()==2:
        Dataset.l1, = ax1.plot(ds[index].x_vec, ds[index].data_bg_corr[Dataset.y_ind,:], color='b')
    Dataset.text1 = plt.text(0.63,0.85, 'y_ind = %d\nvalue = %0.2f'%(Dataset.y_ind,ds[index].y_vec[Dataset.y_ind]), transform=ax1.transAxes)
    if bgcorrVar.get()==1:
        Dataset.l2, = ax2.plot(ds[index].y_vec, ds[index].data[:,Dataset.x_ind], color='b')
    elif bgcorrVar.get()==2:
        Dataset.l2, = ax2.plot(ds[index].y_vec, ds[index].data_bg_corr[:,Dataset.x_ind], color='b')
    Dataset.text2 = plt.text(0.63,0.85, 'x_ind = %d\nvalue = %0.2f'%(Dataset.x_ind,ds[index].x_vec[Dataset.x_ind]), transform=ax2.transAxes)

    # add slider functionality
    Dataset.sl_x = Slider(ax_sl_x, ds[index].x_label, np.min(ds[index].x_vec), np.max(ds[index].x_vec), valinit=ds[index].x_vec[Dataset.x_ind])
    Dataset.sl_y = Slider(ax_sl_y, ds[index].y_label, np.min(ds[index].y_vec), np.max(ds[index].y_vec), valinit=ds[index].y_vec[Dataset.y_ind])
    Dataset.sl_x.on_changed(refresh_val_ax2)
    Dataset.sl_y.on_changed(refresh_val_ax1)
    f.canvas.draw_idle()
    
    # ----- refresh parameter window - can be moved to a separte function at some point
    paramfield.delete(1.0,'end')
    #paramfield.insert(1.0, "Test")
    paramfield.insert('end', pprint.pformat(ds[index].params, width=50) )
    
    return

def refresh_val_ax2(val):
    if len(ds)==0:
        return
    x_ind = np.searchsorted(ds[cur_index].x_vec,val) # get x index from measurement
    Dataset.x_ind = x_ind
    refresh_ax2()

def refresh_val_ax1(val):
    if len(ds)==0:
        return
    y_ind = np.searchsorted(ds[cur_index].y_vec,val) # get y index from measurement
    Dataset.y_ind = y_ind
    refresh_ax1()

def add_crosshair():
    if ax.lines:
        ax.lines[1].remove()
        ax.lines[0].remove()
    ax.plot( [np.min(ds[cur_index].x_vec),np.max(ds[cur_index].x_vec)], [ds[cur_index].y_vec[Dataset.y_ind], ds[cur_index].y_vec[Dataset.y_ind] ], color='k', lw=1)
    ax.plot( [ds[cur_index].x_vec[Dataset.x_ind], ds[cur_index].x_vec[Dataset.x_ind]], [np.min(ds[cur_index].y_vec),np.max(ds[cur_index].y_vec)], color='k', lw=1)
    return

def refresh_ax2(): # replot field slice after slider change
    if len(ds)==0:
        return
    if bgcorrVar.get()==1:
        Dataset.l2.set_ydata(ds[cur_index].data[:,Dataset.x_ind])
    elif bgcorrVar.get()==2:
        Dataset.l2.set_ydata(ds[cur_index].data_bg_corr[:,Dataset.x_ind])
    Dataset.text2.set_text('x_ind = %d\nvalue = %0.2f'%(Dataset.x_ind,ds[cur_index].x_vec[Dataset.x_ind]))
    return

def refresh_ax1(): # replot time slice after slider change
    if len(ds)==0:
        return
    if bgcorrVar.get()==1:
        Dataset.l1.set_ydata(ds[cur_index].data[Dataset.y_ind,:]) # probably faster than a complete replot
    elif bgcorrVar.get()==2:
        Dataset.l1.set_ydata(ds[cur_index].data_bg_corr[Dataset.y_ind,:]) # probably faster than a complete replot
    Dataset.text1.set_text('y_ind = %d\nvalue = %0.2f'%(Dataset.y_ind,ds[cur_index].y_vec[Dataset.y_ind]))
    return

def refresh_slider():
    Dataset.sl_x.set_val(ds[cur_index].x_vec[Dataset.x_ind])
    Dataset.sl_y.set_val(ds[cur_index].y_vec[Dataset.y_ind])
    return

def next_x(event):
    #Dataset.blub = event
    if event.key == 'shift':
        Dataset.x_ind += 10
    else:
        Dataset.x_ind += 1
    refresh_ax2()
    add_crosshair()
    refresh_slider()
    f.canvas.draw_idle()

def prev_x(event):
    if event.key == 'shift':
        Dataset.x_ind -= 10
    else:
        Dataset.x_ind -= 1
    refresh_ax2()
    add_crosshair()
    refresh_slider()
    f.canvas.draw_idle()

def next_y(event):
    if event.key == 'shift':
        Dataset.y_ind += 10
    else:
        Dataset.y_ind += 1
    refresh_ax1()
    add_crosshair()
    refresh_slider()
    f.canvas.draw_idle()

def prev_y(event):
    if event.key == 'shift':
        Dataset.y_ind -= 10
    else:
        Dataset.y_ind -= 1
    refresh_ax1()
    add_crosshair()
    refresh_slider()
    f.canvas.draw_idle()

def ch_button_clicked(self):
    add_crosshair()
    f.canvas.draw_idle()

def setMax_clicked(self):
    if len(ds)==0:
        return
    Dataset.x_ind = ds[cur_index].x_startind
    Dataset.y_ind = ds[cur_index].y_startind
    refresh_ax1()
    refresh_ax2()
    add_crosshair()
    refresh_slider()
    f.canvas.draw_idle()
    return

def onKeyPress(event):
    #print('key pressed:', event.key)
    #Dataset.bla = event
    if event.key == 'right':
        Dataset.x_ind += 1
        refresh_ax2()
    elif  event.key == 'left':
        Dataset.x_ind -= 1
        refresh_ax2()
    elif  event.key == 'up':
        Dataset.y_ind += 1
        refresh_ax1()
    elif  event.key == 'down':
        Dataset.y_ind -= 1
        refresh_ax1()
    add_crosshair()
    refresh_slider()
    f.canvas.draw_idle()
    
def load_dataset(self):
    global ds
    global cur_index
    cur_index +=1
    file_path = filedialog.askopenfilename(filetypes=[("meta Files","*.meta"),("all Files","*.*")])
    ds.append(Dataset(file_path))
    id = tree.insert("" , len(ds)-1,    text=ntpath.basename(file_path), values=(str(ds[cur_index].num_scans)+' (averaged)',"n/a"))
    if ds[cur_index].num_scans > 1: # add single scans to table
        for li in range(1,ds[cur_index].num_scans+1):
            tree.insert(id, "end", "meas "+str(len(ds))+", scan "+str(li), text="single scan", values=(str(li),"n/a"))
    changeDataset(cur_index)
    return

def exportPlot(event):
    print("Preparing Export Figure")
    index = cur_index
    if bgcorrVar.get()==1:
        plot_data = ds[index].data
    elif bgcorrVar.get()==2:
        plot_data = ds[index].data_bg_corr
    
    #ep = plt.figure(figsize=(12, 10))
    #ep = plt.figure() # generate export plot figure
    ep, ex = plt.subplots(1, 1, constrained_layout=True) # generate export plot figure
    ep.canvas.set_window_title('Export Plot Figure')
    #ex1 = ep.add_subplot(111)
    max_val = max(abs(np.max(plot_data)),abs(np.min(plot_data)))
    pcm = ex.pcolormesh(ds[index].x_vec, ds[index].y_vec, plot_data, cmap='bwr', vmin=-max_val, vmax=max_val)
    ex.set_xlabel(ds[index].x_label, fontsize=18)
    ex.set_ylabel(ds[index].y_label, fontsize=18)
    cbar = ep.colorbar(pcm, ax=ex)
    cbar.set_label(ds[index].z_label, rotation=270, fontsize=18, labelpad=20)
    #ex.set_title(ds[index].filename,fontsize=10)
    ep.suptitle(ds[index].filename,fontsize=10)
    ep.show()
    #ep.savefig('test.png', dpi=300, format='png')
    #print(''.join([os.path.splitext(ds[index].filename)[0], 'bla']))
    #ep.savefig(''.join([os.path.splitext(ds[index].filename)[0], '_exportplot.png']), dpi=300, format='png') # ':' in filename is replaced by '/', I do not know why
    ep.savefig(''.join([os.path.splitext(ds[index].filepath)[0], '_exportplot.png']), dpi=300, format='png') # save export figure in data directory 
    return

def exportWaterfallPlot(event):
    #sliceTimes = [0, 0.3, 1.0, 5.0, 10.0] # for the moment fixed, in µs
    #sliceTimes = slicesEntry.get()
    sliceEntryString = slicesEntry.get()
    sliceTimes = [float(i) for i in sliceEntryString.split(',')]
    
    print("Preparing Waterfall Export Figure")
    index = cur_index
    if bgcorrVar.get()==1:
        plot_data = ds[index].data
    elif bgcorrVar.get()==2:
        plot_data = ds[index].data_bg_corr
    
    ep, ex = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]}) # generate export plot figure
    ep.subplots_adjust(left=0.12, bottom=0.12, right=0.96, top=0.94, wspace=0.15, hspace=0.00)
    ep.canvas.set_window_title('Export Waterfall Plot Figure')
    max_val = max(abs(np.max(plot_data)),abs(np.min(plot_data)))
        
    # ----- contour plot
    pcm = ex[1].pcolormesh(ds[index].y_vec, ds[index].x_vec, np.transpose(plot_data), cmap='bwr', vmin=-max_val, vmax=max_val)
    ex[1].set_xlabel(ds[index].y_label, fontsize=18)
    ex[1].set_ylabel(ds[index].x_label, fontsize=18)
    ex[1].get_yaxis().set_label_coords(-0.11,0.5)
    cbar = ep.colorbar(pcm, ax=ex)
    cbar.set_label(ds[index].z_label, rotation=270, fontsize=18, labelpad=20)
    
    # ----- waterfall plot
    ex[0].set_xlim(ex[1].get_xlim()[0], ex[1].get_xlim()[1])
    ex[0].get_xaxis().set_visible(False)
    
    numSlices = np.size(sliceTimes)
    timeIndices = np.zeros(numSlices, dtype=int)
    curveSizes = np.zeros(numSlices)
    offsets = np.zeros(numSlices)
    for idx, val in enumerate(sliceTimes):
        timeIndices[idx] = load_files.find_nearest(ds[index].x_vec, val)
        curveSizes[idx] = max(plot_data[:,timeIndices[idx]]) - min(plot_data[:,timeIndices[idx]])
    averageCurveSize = curveSizes.mean()
    for idx, val in enumerate(sliceTimes):
        if idx >= 1:
            offsets[idx] = offsets[idx-1] + 1.0*abs( max(plot_data[:,timeIndices[idx-1]] - plot_data[:,timeIndices[idx]]) ) + 0.2*averageCurveSize
        curves = ex[0].plot(ds[index].y_vec, plot_data[:,timeIndices[idx]]+offsets[idx])
        ex[1].axhline(ds[index].x_vec[timeIndices[idx]], 0, 1, color=curves[-1].get_color())
    ex[0].set_ylabel(ds[index].z_label, fontsize=18)
    ex[0].get_yaxis().set_label_coords(-0.11,0.5)

    ep.suptitle(ds[index].filename,fontsize=10)
    ep.show()
    ep.savefig(''.join([os.path.splitext(ds[index].filepath)[0], '_exportwaterfallplot.png']), dpi=300, format='png') # save export figure in data directory 
    return

class Dataset:
    x_ind = 0 # class variables
    y_ind = 0

    def __init__(self, file_path):
        data_complex, data_bg_corr_complex, self.params, self.units, self.plotparams, two_ch = load_files.load_file(file_path)
        
        self.filepath = file_path
        self.filename = ntpath.basename(file_path)
        self.x_vec = self.plotparams['x_vec']
        self.y_vec = self.plotparams['y_vec']
        self.x_label = self.plotparams['x_label']
        self.y_label = self.plotparams['y_label']
        self.z_label = self.plotparams['z_label']
        self.trig_pos = self.params['trigpos']
        self.num_scans = self.plotparams['averaged_scans']
        self.two_ch = two_ch
        self.data_real = data_complex.real
        self.data_real_bg_corr = data_bg_corr_complex.real
        if self.two_ch == True:
            self.data_imag = data_complex.imag
            self.data_imag_bg_corr = data_bg_corr_complex.imag
        self.data = self.data_real # still needed?
        self.data_bg_corr = self.data_real_bg_corr # still needed?
        
##########
# "main" starts here
##########
ds = []
cur_index = -1

root = tk.Tk()

loadButton = tk.Button(root, text="Load New Dataset")
#loadButton.pack(fill="x", pady=10)
loadButton.grid(column=0, row=0, sticky='w')
loadButton.bind("<Button-1>", load_dataset)

bgcorrVar = tk.IntVar(value=1) # set default to raw data
bgcorrSwitch1 = tk.Radiobutton(root, text="Raw Data", variable=bgcorrVar, value=1, command=onRadioClicked).grid(column=0, row=1, sticky='w')
bgcorrSwitch2 = tk.Radiobutton(root, text="Pretrigger Offset + BG correction", variable=bgcorrVar, value=2, command=onRadioClicked).grid(column=0, row=2, sticky='w')

phaseSwitchVar = tk.IntVar(value=1) # set default to real data
realButton = tk.Radiobutton(root, text="Real Part", variable=phaseSwitchVar, value=1, command=onPhaseSwitchClicked, indicatoron=0).grid(column=0, row=3, sticky='w')
imagButton = tk.Radiobutton(root, text="Imaginary Part", variable=phaseSwitchVar, value=2, command=onPhaseSwitchClicked, indicatoron=0).grid(column=0, row=4, sticky='w')

phaseLabel = tk.Label(root, text= "Rephasing")
phaseLabel.grid(column=0, row=5, sticky='w')

phaseEntry = tk.Entry(root, width=5)
phaseEntry.grid(column=1, row=5, sticky='w')

phaseButton = tk.Button(root, text="Change Phase")
phaseButton.grid(column=2, row=5, sticky='w')
phaseButton.bind("<Button-1>", rephaseData)

exportButton = tk.Button(root, text="Export Contour Plot")
exportButton.grid(column=2, row=0, sticky='e')
exportButton.bind("<Button-1>", exportPlot)

sliceLabel = tk.Label(root, text="Slice Times:")
sliceLabel.grid(column=1, row=1, sticky='w')
slicesEntry = tk.Entry(root, width=16)
slicesEntry.grid(column=2, row=1, sticky='e')
slicesEntry.insert(0, '0.0, 0.3, 1.0, 5.0, 10.0') # set default values
#sliceTimes = slicesEntry.get()
exportWaterfallButton = tk.Button(root, text="Export Waterfall Plot")
exportWaterfallButton.grid(column=2, row=2, sticky='e')
exportWaterfallButton.bind("<Button-1>", exportWaterfallPlot)

tree = ttk.Treeview(root, selectmode="extended")
tree.master.title("Dataset Browser")
tree["columns"]=("one","two")
tree.column("#0", width=250, stretch=True)
tree.column("one", width=100 )
tree.column("two", width=100)
tree.heading("#0", text="Filename")
tree.heading("one", text="Scan Number")
tree.heading("two", text="Misc.")
#tree.pack(expand=1, fill="both", side="bottom")
tree.grid(columnspan=3, row=6, sticky="we")
tree.bind("<Button-1>", onTableClicked)

# ----- parameter field
paramfield = scrolledtext.ScrolledText(width=50, height=20)
paramfield.grid(columnspan=3, row=7,   sticky='ewns')

# plot
f = plt.figure(figsize=(12, 10))
f.canvas.set_window_title('2D Transient Dataset Viewer')

# plot without data and labels
ax = f.add_subplot(223)
ax1 = f.add_subplot(221)
ax2 = f.add_subplot(222)

cid = f.canvas.mpl_connect('button_press_event', onclick)

# add buttons
axprevx = plt.axes([0.60, 0.25, 0.1, 0.075])
axnextx = plt.axes([0.80, 0.25, 0.1, 0.075])
bnextx = Button(axnextx, '++')
bnextx.on_clicked(next_x)
bprevx = Button(axprevx, '--')
bprevx.on_clicked(prev_x)

axprevy = plt.axes([0.70, 0.15, 0.1, 0.075])
axnexty = plt.axes([0.70, 0.35, 0.1, 0.075])
bnexty = Button(axnexty, '++')
bnexty.on_clicked(next_y)
bprevy = Button(axprevy, '--')
bprevy.on_clicked(prev_y)

axch = plt.axes([0.71, 0.26, 0.08, 0.055])
bch = Button(axch, 'Cross Hair')
bch.on_clicked(ch_button_clicked)

axsetMax = plt.axes([0.81, 0.16, 0.08, 0.055])
bsetMax = Button(axsetMax, 'Set to Max')
bsetMax.on_clicked(setMax_clicked)

# add sliders
ax_sl_x = pl.axes([0.58, 0.10, 0.35, 0.03])
ax_sl_y = pl.axes([0.58, 0.05, 0.35, 0.03])

# detect keypress events when plot window is active
f.canvas.mpl_connect('key_press_event', onKeyPress)

plt.show(block=False)
root.mainloop()
