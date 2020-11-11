"""this is the main gui for the epr script.
it has plotter and buttons. buttons control the experiment."""

#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 4.26
#  in conjunction with Tcl version 8.6
#    Oct 22, 2020 06:02:38 PM CEST  platform: Windows NT
#        Ilia Kulikov ilia.kulikov@fu-berlin.de

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

# importing modules that we will soon need. Including the cw_spectrum! It is a class now.
import Plotter # this is a matplotlib plot that is used heavily for plotting
import setup_scan # a thing for setting up scans
import communication
import threading
from time import sleep


class main_gui:
    plotter = Plotter.Plotter # the plotter is a global field of the main gui class. it is accessible easily.
    scan_setting = setup_scan.Scan_setup() # an instance of the Scan_setup with all its fields and methods. Useful.
    window = tk.Tk
    spectrometer_communicator = communication.new_communicator # there we have all hardware resources.
    # spectrometer_communicator is constructed when the connect to spectrometer button is clicked.

    def __init__(self):

        top = tk.Tk()
        self.window = top
        # -------- code generated by Page gui ide from here -----------------------------------------------------------
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        font10 = "-family {Segoe UI} -size 12 -weight bold -slant "  \
            "roman -underline 0 -overstrike 0"
        font9 = "-family {Segoe UI} -size 12 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("1466x912+272+144")
        top.minsize(116, 1)
        top.maxsize(3282, 1174)
        top.resizable(1, 1)
        top.title("Electron Magnetic Resonance Environment")
        top.configure(background="#d9d9d9")

        self.run_btn = tk.Button(top)
        self.run_btn.place(relx=0.061, rely=0.93, height=55, width=53)
        self.run_btn.configure(activebackground="#ececec")
        self.run_btn.configure(activeforeground="#000000")
        self.run_btn.configure(background="#d9d9d9")
        self.run_btn.configure(disabledforeground="#a3a3a3")
        self.run_btn.configure(font="-family {Segoe UI} -size 12")
        self.run_btn.configure(foreground="#000000")
        self.run_btn.configure(highlightbackground="#d9d9d9")
        self.run_btn.configure(highlightcolor="black")
        self.run_btn.configure(pady="0")
        self.run_btn.configure(text='''Run''')

        self.run_btn_2 = tk.Button(top)
        self.run_btn_2.place(relx=0.102, rely=0.93, height=55, width=53)
        self.run_btn_2.configure(activebackground="#ececec")
        self.run_btn_2.configure(activeforeground="#000000")
        self.run_btn_2.configure(background="#d9d9d9")
        self.run_btn_2.configure(disabledforeground="#a3a3a3")
        self.run_btn_2.configure(font="-family {Segoe UI} -size 12")
        self.run_btn_2.configure(foreground="#000000")
        self.run_btn_2.configure(highlightbackground="#d9d9d9")
        self.run_btn_2.configure(highlightcolor="black")
        self.run_btn_2.configure(pady="0")
        self.run_btn_2.configure(text='''Stop''')

        self.plotter_frame = tk.Frame(top)
        self.plotter_frame.place(relx=0.143, rely=0.088, relheight=0.795
                , relwidth=0.842)
        self.plotter_frame.configure(relief='groove')
        self.plotter_frame.configure(borderwidth="2")
        self.plotter_frame.configure(relief="groove")
        self.plotter_frame.configure(background="#d9d9d9")

        self.Frame1 = tk.Frame(top)
        self.Frame1.place(relx=0.143, rely=0.888, relheight=0.104
                , relwidth=0.842)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(background="#d9d9d9")

        self.TLabel1 = ttk.Label(self.Frame1)
        self.TLabel1.place(relx=0.008, rely=0.105, height=25, width=37)
        self.TLabel1.configure(background="#d9d9d9")
        self.TLabel1.configure(foreground="#000000")
        self.TLabel1.configure(font=font9)
        self.TLabel1.configure(relief="flat")
        self.TLabel1.configure(text='''B set''')

        self.TLabel1_3 = ttk.Label(self.Frame1)
        self.TLabel1_3.place(relx=0.008, rely=0.358, height=25, width=57)
        self.TLabel1_3.configure(background="#d9d9d9")
        self.TLabel1_3.configure(foreground="#000000")
        self.TLabel1_3.configure(font="-family {Segoe UI} -size 12")
        self.TLabel1_3.configure(relief="flat")
        self.TLabel1_3.configure(text='''B meas''')

        self.B_set_label = ttk.Label(self.Frame1)
        self.B_set_label.place(relx=0.065, rely=0.105, height=25, width=87)
        self.B_set_label.configure(background="#d9d9d9")
        self.B_set_label.configure(foreground="#000000")
        self.B_set_label.configure(font=font10)
        self.B_set_label.configure(relief="flat")
        self.B_set_label.configure(text='''XXXXXX''')

        self.B_meas_label = ttk.Label(self.Frame1)
        self.B_meas_label.place(relx=0.065, rely=0.358, height=25, width=87)
        self.B_meas_label.configure(background="#d9d9d9")
        self.B_meas_label.configure(foreground="#000000")
        self.B_meas_label.configure(font=font10)
        self.B_meas_label.configure(relief="flat")
        self.B_meas_label.configure(text='''XXXXXX''')

        self.TLabel1_4 = ttk.Label(self.Frame1)
        self.TLabel1_4.place(relx=0.761, rely=0.105, height=25, width=187)
        self.TLabel1_4.configure(background="#d9d9d9")
        self.TLabel1_4.configure(foreground="#000000")
        self.TLabel1_4.configure(font="-family {Segoe UI} -size 12")
        self.TLabel1_4.configure(relief="flat")
        self.TLabel1_4.configure(text='''Electrochemical potential''')

        self.echem_pot_label = ttk.Label(self.Frame1)
        self.echem_pot_label.place(relx=0.915, rely=0.105, height=25, width=87)
        self.echem_pot_label.configure(background="#d9d9d9")
        self.echem_pot_label.configure(foreground="#000000")
        self.echem_pot_label.configure(font="-family {Segoe UI} -size 12")
        self.echem_pot_label.configure(relief="flat")
        self.echem_pot_label.configure(text='''XXXXXX mV''')

        self.TLabel1_4 = ttk.Label(self.Frame1)
        self.TLabel1_4.place(relx=0.178, rely=0.105, height=25, width=57)
        self.TLabel1_4.configure(background="#d9d9d9")
        self.TLabel1_4.configure(foreground="#000000")
        self.TLabel1_4.configure(font="-family {Segoe UI} -size 12")
        self.TLabel1_4.configure(relief="flat")
        self.TLabel1_4.configure(text='''scan #''')
#!!! changed here nscan label name
        self.nscan_label = ttk.Label(self.Frame1)
        self.nscan_label.place(relx=0.219, rely=0.105, height=25, width=47)
        self.nscan_label.configure(background="#d9d9d9")
        self.nscan_label.configure(foreground="#000000")
        self.nscan_label.configure(font="-family {Segoe UI} -size 12")
        self.nscan_label.configure(relief="flat")
        self.nscan_label.configure(text='''XXXX''')

        self.TLabel1_5 = ttk.Label(self.Frame1)
        self.TLabel1_5.place(relx=0.257, rely=0.095, height=25, width=27)
        self.TLabel1_5.configure(background="#d9d9d9")
        self.TLabel1_5.configure(foreground="#000000")
        self.TLabel1_5.configure(font="-family {Segoe UI} -size 12")
        self.TLabel1_5.configure(relief="flat")
        self.TLabel1_5.configure(text='''of''')

        self.TEntry1 = ttk.Entry(self.Frame1)
        self.TEntry1.place(relx=0.279, rely=0.126, relheight=0.221
                , relwidth=0.045)
        self.TEntry1.configure(font="Font9")
        self.TEntry1.configure(takefocus="")
     #   self.TEntry1.configure(cursor="ibeam")

        self.TLabel1_9 = ttk.Label(self.Frame1)
        self.TLabel1_9.place(relx=0.117, rely=0.105, height=25, width=37)
        self.TLabel1_9.configure(background="#d9d9d9")
        self.TLabel1_9.configure(foreground="#000000")
        self.TLabel1_9.configure(font="-family {Segoe UI} -size 12")
        self.TLabel1_9.configure(relief="flat")
        self.TLabel1_9.configure(text='''G''')

        self.TLabel1_10 = ttk.Label(self.Frame1)
        self.TLabel1_10.place(relx=0.117, rely=0.358, height=25, width=37)
        self.TLabel1_10.configure(background="#d9d9d9")
        self.TLabel1_10.configure(foreground="#000000")
        self.TLabel1_10.configure(font="-family {Segoe UI} -size 12")
        self.TLabel1_10.configure(relief="flat")
        self.TLabel1_10.configure(text='''G''')

        self.Frame2 = tk.Frame(top)
        self.Frame2.place(relx=0.143, rely=0.011, relheight=0.071
                , relwidth=0.842)
        self.Frame2.configure(relief='groove')
        self.Frame2.configure(borderwidth="2")
        self.Frame2.configure(relief="groove")
        self.Frame2.configure(background="#d9d9d9")

        self.connect_btn = tk.Button(top)
        self.connect_btn.place(relx=0.007, rely=0.011, height=65, width=193)
        self.connect_btn.configure(activebackground="#ececec")
        self.connect_btn.configure(activeforeground="#000000")
        self.connect_btn.configure(background="#d9d9d9")
        self.connect_btn.configure(disabledforeground="#a3a3a3")
        self.connect_btn.configure(font="-family {Segoe UI} -size 12")
        self.connect_btn.configure(foreground="#000000")
        self.connect_btn.configure(highlightbackground="#d9d9d9")
        self.connect_btn.configure(highlightcolor="black")
        self.connect_btn.configure(pady="0")
        self.connect_btn.configure(text='''Connect to spectrometer''')

        self.setup_scan_btn = tk.Button(top)
        self.setup_scan_btn.place(relx=0.007, rely=0.088, height=65, width=193)
        self.setup_scan_btn.configure(activebackground="#ececec")
        self.setup_scan_btn.configure(activeforeground="#000000")
        self.setup_scan_btn.configure(background="#d9d9d9")
        self.setup_scan_btn.configure(disabledforeground="#a3a3a3")
        self.setup_scan_btn.configure(font="-family {Segoe UI} -size 12")
        self.setup_scan_btn.configure(foreground="#000000")
        self.setup_scan_btn.configure(highlightbackground="#d9d9d9")
        self.setup_scan_btn.configure(highlightcolor="black")
        self.setup_scan_btn.configure(pady="0")
        self.setup_scan_btn.configure(text='''Set up scan''')

        self.params_to_hw_btn = tk.Button(top)
        self.params_to_hw_btn.place(relx=0.007, rely=0.93, height=55, width=75)
        self.params_to_hw_btn.configure(activebackground="#ececec")
        self.params_to_hw_btn.configure(activeforeground="#000000")
        self.params_to_hw_btn.configure(background="#d9d9d9")
        self.params_to_hw_btn.configure(disabledforeground="#a3a3a3")
        self.params_to_hw_btn.configure(font="-family {Segoe UI} -size 12")
        self.params_to_hw_btn.configure(foreground="#000000")
        self.params_to_hw_btn.configure(highlightbackground="#d9d9d9")
        self.params_to_hw_btn.configure(highlightcolor="black")
        self.params_to_hw_btn.configure(pady="0")
        self.params_to_hw_btn.configure(text='''par to hw''')


        # ---------- upto here the code was generated by Page tkinter drag and drop manager -----------

        # first of all lets insert the plotter to the plotting frame.
        self.plotter = Plotter.Plotter(rootframe=self.plotter_frame)

        # now let us configure buttons. set up scan button should create an instance of setup scan.
        self.connect_btn.configure(command = self.connect_to_spectrometer)
        self.setup_scan_btn.configure(command = self.make_scan_setting)
        self.params_to_hw_btn.configure(command = self.parameters_to_hardware)
        self.run_btn.configure(command = self.run_experiment)
        self.run_btn.configure(state='disabled') # by default you cant run experiment. You need to setup params first

        top.protocol("WM_DELETE_WINDOW", self.close_main_window)
        top.mainloop()


    def make_scan_setting(self):

        if self.scan_setting.set_scan: # if scan was already set, just open its gui
            self.scan_setting.unhide()
        else:
            self.scan_setting = setup_scan.Scan_setup() # create an instance of the class. Scan set if scanset var True
            self.scan_setting.show_gui()


    def run_experiment(self): # run experiment here
        # just run the experiment with the parameters obtained from self.scan_setting.
        if self.scan_setting.scan_set:
            # self.run_cw_experiment() that would work, for now we just test
            self.run_echem_experiment()

        else:
            print('first set up a scan')
            self.scan_setting = setup_scan.Scan_setup()  # create an instance of the class. Scan set if scanset var True
            self.scan_setting.show_gui()



    def run_cw_experiment(self):
        print('just running the cw_scan method')
        #experiment_thread = threading.Thread(target=cw_scan, args= (self.spectrometer_communicator,self.scan_setting,self.plotter))# here starts the cw scan in a separate process! Dont forget to finish it.
        #experiment_thread.start()
        cw_scan(self.spectrometer_communicator,self.scan_setting,self.plotter)


    def run_echem_experiment(self):
        print('just running the echem_scan method')
        #experiment_thread = threading.Thread(target=cw_scan, args= (self.spectrometer_communicator,self.scan_setting,self.plotter))# here starts the cw scan in a separate process! Dont forget to finish it.
        #experiment_thread.start()
        self.sink_run_button()
        echem_scan(self.spectrometer_communicator,self.scan_setting,self.plotter, self)
        self.raise_run_button()
        print('creating another process for plotting')

    def sink_run_button(self):
        self.run_btn.configure(relief=tk.SUNKEN)

    def raise_run_button(self):
        self.run_btn.configure(relief=tk.RAISED)

    def close_main_window(self): # hell yeah
        self.window.destroy()
        self.scan_setting.gui.destroy()

    def connect_to_spectrometer(self):
        '''connect to spectrometer, that is create a communicator and try creating all devices in it'''
        print('connecting to spectrometer...')

        self.spectrometer_communicator = communication.new_communicator('')  # create a communicator with pyvisa-py
        #TODO: UNCOMMENT THIS ON LYRA:
#        self.spectrometer_communicator = communication.new_communicator('@py')  # create a communicator with pyvisa-py
        # backend. This is a global field of the main_gui class.
        # now I dont want to always write self.spectrometer_communicator, I will just write sp_comm
        sp_comm = self.spectrometer_communicator

        # lets handshake with the field controller:
        fieldcontroller = sp_comm.field_controller # as easy as it sounds
        lockin = sp_comm.lockin # our lovely SR810 LIA at lyra. Yeas we will nead the machine files but later.


    def send_initial_parameters_to_hardware(self):

        # ############################ sending initial parameters to spectrometer here #################################

        # 0. send settings to the lock-in amplifdier
        # 1. send magnetic field to field controller
        # 2. WE DO NOT USE GAUSSMETER NOW. SOMEONE IMPLEMENT IT LATER
        # copy that from an edl script on lyra, your life will be so much easier!

        # ________________________________________________   LIA setup _________________________________________________
        # Felix wrote calibration
        # fir Lock-in we have 5 lockin variables.
        # li_freq   v
        # li_level  v
        # li_phase  v
        # li_tc     v
        # li_sens   v

        # li_level is the value that is to be sent to lia for the certain amplitude in Gauss.

        print('sending parameters to hardware')

        # -------------------------------------------   setting li_freq:   ---------------------------------------------

        li_freq = self.scan_setting.modfreq
        print("Lock-in modulation frequency setting to %.1f Hz" % li_freq)
        sp_com = self.spectrometer_communicator # this is just shorter, better for reading.
        print(li_freq)

        sp_com.lockin.set_frequency(frequency_in_hz = li_freq)

        # --------------------------------------------  setting li_level:  ---------------------------------------------

        # if mod amp was given in gauss we need to calculate it to volts. That is a method of Scan_setup class
        li_level = self.scan_setting.li_level

        print('%.3f V'%li_level)
        sp_com.lockin.set_voltage(voltage_in_volts = li_level)

        # --------------------------------------------  setting li_phase:  ---------------------------------------------
        # for 10 kHz it is 291 deg
        # for 100 kHz it is 338 deg
        # that was done in the setup_scan. the modulation amplitude should in principle be there too, not here.
        # but no one cares.

        li_phase = self.scan_setting.li_phase
        print("Lock-in phase setting to %.3f deg" % (li_phase))

        sp_com.lockin.set_phase(li_phase)

        # --------------------------------------------  setting li_tc:  ------------------------------------------------
        li_tc = self.scan_setting.li_tc

        # a trick. find the time constant in the list and take its position, that would be the code
        time_constants = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 1e+1, 3e+1, 1e+2, 3e+2,
                          1e+3, 3e+3, 1e+4, 3e+4]  # order of value is its SCPI code

        CODE = time_constants.index(li_tc)
        print("Lock-in time constant setting to %.1e s with CODE = %d" % (li_tc, CODE))

        sp_com.lockin.set_time_constant(CODE)

        # --------------------------------------------     li_sens      ------------------------------------------------
        print('Lock-in auto sensitivity is not available')

        li_sens = self.scan_setting.li_sens
        sens_values = [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4,
                       5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1]  # order of value is its SCPI code
        CODE = sens_values.index(li_sens)
        print('Lock-in sensitivity setting to %.1e V with CODE = %d' % (li_sens, CODE))

        sp_com.lockin.set_sensitivity(CODE)

        # _____________________________________   Field Controller Set-up   ____________________________________________

        from time import sleep  # this guy is slow

        sp_com.field_controller.go_remote()  # doing it as it was written in its manual
        sleep(0.5)
        sp_com.field_controller.set_operating_mod(mode_ = 0) # moving BH15 to operating mode 0
        sp_com.field_controller.set_center_field(self.scan_setting.bstart) # setting b_start to field controller
        print('#### set initial field ### %.2f G'%self.scan_setting.bstart)
        sleep(0.5)  # it likes to sleep. Check it with LE though, that is more sensible

        return 1  # default return value is 1. anything goes wrong and changes it to -1, that will be seen.

    def unload_parameters_from_hardware(self): # make it solve most of the problems.
        print("unload parameters from hardware. You can't run experiment now.")
        print("just stop modulation coils by now")
        sp_com = self.spectrometer_communicator
        sp_com.lockin.set_voltage(voltage_in_volts=0) # set modulation amp to 0 V

    def parameters_to_hardware(self):
        # if scan was set, send initial parameters to hardware and preset scan
        if self.scan_setting.scan_set: # if somebody has modified the scan

            # stupidly monkeying after xEpr:
            state = str(self.params_to_hw_btn['relief'])

            if state == tk.RAISED:  # if parameters to hardware button not pressed

                self.send_initial_parameters_to_hardware() # send initial params to hardwaew
                self.run_btn.configure(state=tk.NORMAL)  # let user run th eprogram
                self.params_to_hw_btn.configure(relief=tk.SUNKEN)  # keep it pressed
            else:

                self.unload_parameters_from_hardware()
                self.params_to_hw_btn.configure(relief=tk.RAISED)  # keep it unpressed
                self.run_btn.configure(state=tk.DISABLED)

    # decorative fancy useless things that absolutely noone needs

    def show_potential_in_gui(self, pot: float):  # this modifies the label in the gui that shows the applied potential.
        self.echem_pot_label.configure(text='%.3f' % pot)
        self.echem_pot_label.update()

    def show_field_in_gui(self, field: float):  # this modifies the label in the gui that shows the applied potential.
        self.B_set_label.configure(text='%.3f' % field)
        self.B_set_label.update()

    def show_nscan_in_gui(self,nscan: int):
        self.nscan_label.configure(text = '%d'%nscan)



END = tk.END  # convenient variable for configuring entries

def cw_scan(sp_com: communication.new_communicator, scan_setting: setup_scan, plotter: Plotter.Plotter):
    #---------------------------------------------------- the cw scan happens here -------------------------------------
    """CW SCAN. the scan settings are passed by scan setting instance. That has to be already populated in the set scan procedure."""
    import cw_spectrum

    bstart = scan_setting.bstart
    bstop = scan_setting.bstop
    bstep = scan_setting.bstep

    number_of_cw_scans = scan_setting.nruns

    import numpy as np
    from time import sleep

    B0s = np.arange(bstart, bstop, bstep)

    bvalues = []
    signal = []
    scans_stack = [] # here we stack individual scans
    averaged_signal_R = [] # this list to be dynamically changed
    bvalues_for_averaged = []  # for plotting averaged data. Once populated in 1st scan, stays the same for all scans


    plotter.add_live_plot(bstart,bstop) #adding axes for plotting live data. data manipulation in these axes is separate from other.
    plotter.add_average_plot(bstart,bstop) # adding axes for plotting averaged plot


    # _______ Спаси и сорхрани ______ saving spectrum as cw_spectrum.cw_spectrum.  _______________________________________

    spectrum = cw_spectrum.cw_spectrum('')  # temp file. we save only R and only akku
    from datetime import datetime           # this thing gets current time
    spectrum.time = str(datetime.now())     # get current time, microseconds lol
    spectrum.comment = scan_setting.comment # from here you see, we just populate the lines as it was done in akku2
    spectrum.nruns = scan_setting.nruns
    spectrum.bstart = scan_setting.bstart
    spectrum.bstop = scan_setting.bstop
    spectrum.bstep = scan_setting.bstep
    spectrum.modamp = scan_setting.modamp
    spectrum.modamp_dim = scan_setting.modamp_dim
    spectrum.modfreq = scan_setting.modfreq
    spectrum.li_tc = scan_setting.li_tc
    spectrum.li_level = scan_setting.li_level
    spectrum.li_phase = scan_setting.li_phase
    spectrum.li_sens = scan_setting.li_sens
    spectrum.conv_time = scan_setting.conv_time
    spectrum.mwfreq = scan_setting.mwfreq
    spectrum.attn = scan_setting.attn
    spectrum.temp = scan_setting.temp
    spectrum.bvalues = B0s # just in case you will want to plot it later.

    # __________________________________________________________



    # -------------------------------------------- cycle on nruns ------------------------------------------------------
    for scan_cntr in range(number_of_cw_scans):

        signal = [] # current signal is nothing when B0 scan begins
        bvalues = [] # magnetic field values are nothing too


        # ----------------------------------- cycle on magnetic fields -------------------------------------------------
        for B0 in B0s:
            '''move to basic field control mode that is mode 0'''
            sp_com.field_controller.curse_BH15('MO0')
            '''set field to current B0'''
            sp_com.field_controller.set_center_field(B0)
            '''move to field measure mode that is mode 5'''
            sp_com.field_controller.curse_BH15('MO5')
            '''get the led status'''
            ledstatus = sp_com.field_controller.talk_to_BH15('LE')
            '''measure field'''
            B0_measured_str = sp_com.field_controller.talk_to_BH15('FC')
            B0_measured = float(B0_measured_str[3:11])
            '''God save the magnet.'''

            '''lets now talk about the microwave absorption. This is measured with the LIA. Lets talk to the LIA.'''
            voltage_in_the_r_channel = sp_com.lockin.getR()

            '''careful there with sleep'''
            sleep(0.01)
            '''our spectrum'''

            # -------------------------------------- data collection for real devices ----------------------------------
            bvalues.append(B0_measured)                   # B0s for the current scan
            signal.append(voltage_in_the_r_channel)       # sognal of the current scan

            if scan_cntr == 0:
                averaged_signal_R.append(voltage_in_the_r_channel)    # averaged signal = signal for scan #0
                bvalues_for_averaged.append(B0_measured)            # B0 vector is just being created
            else:
                averaged_signal_R[len(signal)-1] = (averaged_signal_R[len(signal)-1]*scan_cntr + signal[len(signal)-1]) / (scan_cntr+1) # here we are different from xEpr
                                                                    # then you average points in the scan with weights
            # --------------------------------- end of data collection -------------------------------------



            # --------------------------------------live plotting ------------------------------------------


            plotter.plot_live_data(bvalues, signal,'-b')
            plotter.plot_averaged_data(bvalues_for_averaged, averaged_signal_R, '-r')

            # ---------------------------------- end of liveplotting ---------------------------------------

        # ----------------------------------- end of cycle on magnetic fields ------------------------------------------

        scans_stack.append(signal)  # save current scan in memory

        # plot averaged... wait. I want plot average while it is recording

    # -----------------------------------------    end of cycle on nruns   ---------------------------------------------
    # TODO: SAVE BOTH CHANNELS! WHAT YOU DO NOW IS WRONG!
    spectrum.x_channel = averaged_signal_R
    spectrum.y_channel = averaged_signal_R


    spectrum.save('temp_spectrum.akku2') # сохранили временный спектр. Потом можно спросить там как его называть

import cw_spectrum


def echem_scan(sp_com: communication.new_communicator, scan_setting: setup_scan, plotter: Plotter.Plotter, gui:main_gui):
    import numpy as np
    from datetime import datetime as dt
    echem_potentials = np.linspace(start = scan_setting.echem_low, stop = scan_setting.echem_high, num=scan_setting.echem_nsteps)

    print('we will go through following potentials:')
    for pot in echem_potentials:
        print(str(pot)+'mV')

    stay_low_ncycles = scan_setting.echem_go_low
    go_high_ncycles = scan_setting.echem_stay_high

    high_scans = []  # list of electrochemical scans with nonzero potential
    low_scans = []   # list of echem scans with zero potential


    #  plotting: averaged plot at the averaged axes.
    plotter.add_average_plot(bstart=scan_setting.bstart, bstop = scan_setting.bstop)

    print('echem experiment:')
    for pot in echem_potentials:
        #sp_com.pstat.play_tune() # scare your colleagues by uncommenting this line
        sp_com.pstat.play_short_beep()
        sp_com.pstat.set_voltage(voltage_in_volts=pot/1000)
        sp_com.pstat.output_on() # включили выход потенциостата, он - ебашит.
        print(' ________________________________________this will set new potential' + str(pot) + 'mV. I also beep.  P')
        gui.show_potential_in_gui(pot)

        for scan_cntr in range(go_high_ncycles):
            print('   CW running cw scan')
            gui.show_nscan_in_gui(scan_cntr)  # absolutely excessive useless function, yeah. Of course.

            high_scan = SingleCwScan(sp_com,scan_setting,plotter,pot,gui) # record one cw scan
            high_scans.append(high_scan)
            plotter.plot_averaged_data(high_scans)
            #plotter.set_y_limits_of_x_averaged_axis(min(),scan_setting.li_sens) # wit and easy
            #plotter.set_y_limits_of_y_averaged_axis(-scan_setting.li_sens, scan_setting.li_sens)  # wit and easy
            # by setting limits you can manipulate the displayed data.


            #this averaged plot is plotted once per scan

        # at this point we have done go_high_cycles cw scans at potential pot.
        # let us save it as TMP_n%d_%.2fmV.akku2
        # first make a cw_spectrum from these scans.

        averaged_spectrum_high = cw_spectrum.make_spectrum_from_scans(high_scans,scan_setting)
        averaged_spectrum_high.time = dt.now() # recorded the time.
        # getting the MW frequency from agilent counter:
        mwfrq = sp_com.frequency_counter.get_MW_frequency()
        averaged_spectrum_high.mwfreq = mwfrq
        averaged_spectrum_high.save('HIGH_n%d_%.2fmV'%(go_high_ncycles,pot))


        print(' ______________________________________________________________ this will set zero potential {0} mV 0')
        sp_com.pstat.set_voltage(voltage_in_volts = 0)  # Двойная зашита от пыли и грязи.
        sp_com.pstat.output_off()  # выключили выход потенциостата, он - не ебашит.
        for _ in range(stay_low_ncycles):
            print('   CW running cw scan')

            low_scan = SingleCwScan(sp_com, scan_setting, plotter, 0, gui)  # record one cw scan for zero potential
            low_scans.append(low_scan)

    averaged_spectrum_low = cw_spectrum.make_spectrum_from_scans(high_scans, scan_setting)
    averaged_spectrum_low.time = dt.now()  # recorded the time.
    # getting the MW frequency from agilent counter:
    mwfrq = sp_com.frequency_counter.get_MW_frequency()
    averaged_spectrum_low.mwfreq = mwfrq
    averaged_spectrum_low.save('LOW_n%d' % (stay_low_ncycles*scan_setting.echem_nsteps))


import numpy as np
import datetime as dt

def SingleCwScan(sp_com: communication.new_communicator, scan_setting: setup_scan.Scan_setup, plotter: Plotter.Plotter, potential, gui:main_gui):
    '''populate bvalues and signal by measuring the spectrum'''

    spectrum = cw_spectrum.cw_spectrum('')  # container. empty filepath === just an empty cw_spectrum
    spectrum.bvalues = [] # values of B0, measured. Populated as scan progresses.
    spectrum.signal = []  # values of signal. Measured. populated in the constructor
    spectrum.potential = 0 # electrochemical potential for this scan

    def runscan():
        # this runs a scan. it runs the cw EPR experiment. And returns an instance of cw_spectrum

        bstart = scan_setting.bstart # read scan parameters from the scan setting obj that has been constructed before
        bstop = scan_setting.bstop
        bstep = scan_setting.bstep
        bvalues_to_send = np.arange(bstart, bstop, bstep) # these will be sent to the field controller.
        delay = scan_setting.delay

        spectrum.x_channel = []  # these are the most important fields of this class.
        spectrum.y_channel = []  # these are the most important fields of this class.
        spectrum.bvalues = []

        spectrum.potential = potential
        print('doing cw scan at %.2f mV'%spectrum.potential)

        plotter.add_live_plot(bstart,bstop) # rescaling B axis for live plotting and adding live axes if needed

        # when scan starts, set B0 so that it is set. Wait f needed
        B0_start = bvalues_to_send[0]
        sp_com.field_controller.set_center_field(B0_start)
        # sleep widely but for now sleep dumb
        sleep(3) # to return back to initial B0

        # go through B0s in bvalues_to_send:
        for B0 in bvalues_to_send:
            gui.show_field_in_gui(B0)  # absolutely excessive useless function, yeah. Of course.
            B0_measured_by_FC = sp_com.field_controller.set_field(B0)  # set and measure magnetic field
            spectrum.bvalues.append(B0_measured_by_FC)  # real data from lyra.
            #print('_______________ measured B0 ____________________ %.2f G ______________________________'%B0_measured_by_FC)
            sleep(delay) # is sleep in seconds? Is delay in seconds?
            #sleep(0.001)


            #print('MEASURING SIGNAL')

            # uncomment the fake line for debugging.
            # fake epr line:
                #fc = 3275
                #intens = 50
                #lw = 20
                #self.signal.append(-intens*np.exp(-(B0-fc)*(B0-fc)/(2*lw*lw))*(B0-fc)+np.random.randint(0,50))  # temp!

            lia_voltage_in_X_channel = sp_com.lockin.getX()
            lia_voltage_in_Y_channel = sp_com.lockin.getY()

            #print('________ %.2f V / %.2f V _____________________' % (lia_voltage_in_X_channel, lia_voltage_in_Y_channel))

            spectrum.x_channel.append(lia_voltage_in_X_channel)
            spectrum.y_channel.append(lia_voltage_in_Y_channel)
            ################################################### !!! live  plotting is happening here !!! ##################
            plotter.plot_live_data_x(
                spectrum.bvalues,spectrum.x_channel,min(spectrum.x_channel),max(spectrum.x_channel))
            plotter.plot_live_data_y(
                spectrum.bvalues, spectrum.y_channel,min(spectrum.y_channel),max(spectrum.y_channel))
            plotter.update()

        # TODO: also make a file. CW_scan outputs a file(!) call it temp. Rename it later whan the user demands. Or rather call it temp_date
        # lol easy. Just run spectrum.save!



    dtm = dt.datetime.now() # time stamp after scan ended.
    runscan()
    return spectrum


def startgui():
    maingui = main_gui()

if __name__ == "__main__":
    #gui_thread = threading.Thread(target = startgui())
    #gui_thread.start()
    gui = main_gui()
