
import datetime
import numpy as np

class cw_spectrum:
    '''cw EPR spectrum recorded on lyra
    and some methods for processing it'''

    file_path = ""     # file path with data
    spectrum_file = 0  # spectrum file
    index = 0          # index in the tree view

    twochannels = False # recorded two channels?
    gaussmeter = False  # gaussmeter used?
    date = 0          # date of experiment
    time = 0          # time of experiment
    bstart = 0        # start value of magnetic field
    bstop = 0         # upper limit of magnetic field
    bstep = 0         # step of magnetic field
    modamp = 0        # modulation amplitude
    modfreq = 0       # modulation frequency
    li_tc = 0         # LIA TC
    li_level = 0      # LIA level
    li_phase = 0      # LIA phase
    li_sens = 0       # LIA sensitivity
    conv_time = 0     # conversion time, TCs
    mwfreq = 0        # MW frequency, GHz
    attn = 0          # Attenuation, dB
    temp = 0          # Temperature, K
    sample = ""
    comment = ""
    file_name = ""     # file name, not the full path

    modamp_dim = ''   # for the time being. Heritage of fsc2

    bstart_meas = 0
    bstop_meas = 0     # magnetic fields measured with gaussmeter
    nruns = 0          # number of scans
    npoints = 0        # number of magnetic field points

    # === these are for plotting ===
    bvalues = []    # magnetic field axis
    x_channel = []  # spectral x channel component
    y_channel = []  # spectral y channel component

    frequency_corrected = False

    # === these are for saving spectrum to a file ===
    savefile = 0 # file to save data

    # === these are for electrochemistry ===
    potential = 0  # to be populated in the electrochemistry scan.

    def __init__(self,filepath):
        ''''create instance of cwepr spectrum with parameters and data.
        Magnetic field axis is created.
        Call normalize to normalize.
        Call baseline_correct to base line correct
        Write autophase method to put signal to X channel'''

        # by now this works by loading a fsc2 akku2 spectrum from file.
        # replace it by self.fsc2load to get cwe_spectrum from akku2 file (look at file format)
        # or use self.eprload to get cw_spectrum from xEpr files.

        if filepath == '':  # if no file path given, just create a container. Used for creating spectra,
            return


        self.file_path = filepath # we will work with the file from here
        print("filepath: %s" %self.file_path)

        self.spectrum_file = open(self.file_path) # open the file
        sf = self.spectrum_file # for short
        #------- just quickly getting the name of the file: -------
        import os
        self.file_name = os.path.basename(self.file_path)

        #------- now we work with the file. Reading it line by line: ------

        channel_config = sf.readline().split(" ")  # here are channel parameters
        if channel_config[2] == "2ch":
            self.twochannels = True
            print("data in both channels")

        #------ reading date and time of experiment: ------#

        date_time_list = sf.readline()#.split(" ")
        self.time = date_time_list # just a string
        #date_list = date_time_list[1].split("-")
        #time_list = date_time_list[2].split(":")
        #self.date = datetime.date(int(date_list[0]), int(date_list[1]), int(date_list[2]))  # set date
        #self.time = datetime.time(int(time_list[0]), int(time_list[1]), int(time_list[2]))  # set time

        # ------ reading magnetic field: ------#

        gaussmeter_config = sf.readline().split(" ")
        if "bstart_meas" in gaussmeter_config:
            self.gaussmeter = True
            print("gaussmeter was used")
        else:
            print("no gaussmeter used")

        print(sf.readline()) # I have no idea what should be in this line. Looks like the comment, I can check it later.
        print("------------------ parameters --------------------")

        # ------ reading other parameters: ------#

        def suffix_to_factor(suffix):
            '''# stupid but necessary: switches uV to 1e-6 and so on'''
            print(suffix)
            return {
                'nV'  : 1e-9,  # 1 nV
                'nV\n': 1e-9,  # 1 nV
                'uV'  : 1e-6,  # 1 uV
                'uV\n': 1e-6,
                'mV'  : 1e-3,  # 1 mV
                'mV\n': 1e-3,
                'us\n': 1e-6,  # 1 us
                'us'  : 1e-6,
                'ms\n': 1e-3,
                'ms'  : 1e-3,
                'ns\n': 1e-9,
                'ns'  : 1e-9,

            }.get(suffix, -1)  # default value to return is -1 that means smth went wrong and threw an error


        lst = sf.readline().split(" ")
        self.nruns = int(lst[2]) # number of scans
        print("nruns: %.3f" % (self.nruns))

        lst = sf.readline().split(" ")
        self.npoints = int(lst[2]) # number of points for magnetic field
        print("npoints: %d" % (self.npoints))

        lst = sf.readline().split(" ")
        self.bstart = float(lst[2])  # start magnetic field, reading line 7
        print("B start: %.3f %s" % (self.bstart,lst[3]))


        lst = sf.readline().split(" ")
        self.bstop = float(lst[2])  # stop magnetic field, reading line 8
        print("B stop : %.3f %s" % (self.bstop, lst[3]))

        lst = sf.readline().split(" ")
        self.bstep = float(lst[2])  # step of magnetic field, reading line 9
        print("B step: %.3f %s" % (self.bstep, lst[3]))

        lst = sf.readline().split(" ")
        self.modamp = float(lst[2])  # modulation in G, reading line 10
        print("modamp: %.3f %s" % (self.modamp,lst[3]))
        self.modamp_dim = (lst[3]) # dimensionality matters
        # that will be saved for a while as a field of the class

        lst = sf.readline().split(" ")
        self.modfreq = float(lst[2])  # modulation frequency
        print("modfreq: %.3f %s" % (self.modfreq,lst[3]))

        lst = sf.readline().split(" ")
        li_tc_raw = float(lst[2])  # LIA Time Constant
        li_tc_dim = (lst[3]) # ms, us, etc
        # taking care of dimensions
        self.li_tc = li_tc_raw*suffix_to_factor(li_tc_dim)
        print("LIA TC : %.3f %s -> %.3f s" % (li_tc_raw, lst[3], self.li_tc))


        lst = sf.readline().split(" ")
        self.li_level = float(lst[2])  # LIA level
        print("LIA level : %.3f %s" % (self.li_level,lst[3]))

        lst = sf.readline().split(" ")
        self.li_phase = float(lst[2])  # LIA phase
        print("LIA phase : %.3f %s" % (self.li_phase,lst[3]))
        lst = sf.readline().split(" ")
        li_sens_raw = float(lst[2])  # LIA sensitivity
        # here dimension matters. uV gets factor of 1e-6
        li_sens_suffix = str((lst[3]))
        self.li_sens = li_sens_raw*suffix_to_factor(li_sens_suffix)

        print("LIA sens : %.3f %s -> %.3f V" % (li_sens_raw, li_sens_suffix, self.li_sens))



        lst = sf.readline().split(" ")
        self.conv_time = float(lst[2])  # LIA conversion time, in TCs
        print("LIA conv time : %.3f" % (self.conv_time))

        lst = sf.readline().split(" ")
        self.mwfreq = float(lst[2])  # MW freq, GHz
        print("MW freq : %.6f GHz %s" % (self.mwfreq/1e9,lst[3]))

        lst = sf.readline().split(" ")
        self.attn = float(lst[2])  # Attenuation, dB
        print("Attenuation : %d %s" % (self.attn,lst[3]))

        lst = sf.readline().split(" ")
        self.temp = float(lst[2])  # Temperature, K
        print("Temperature : %d %s" % (self.temp,lst[3]))

        lst = sf.readline().split(" ")
        strange_parameter = float(lst[2])  # something in V but I dont beleive that
        print("strange parameter: %d %s" % (strange_parameter,lst[3]))

        print("--------------------------------------------------")

        print("reading data")
        # now reading data. Depending on whether gaussmeter was used and both channels recorded, choose the way.
        # c гаусметром аккуратнее тут, последние три числа в этом списке будут частота и два магнитных поля.
        # если два канала записали, надо два канала считать.

        string_x_channel = sf.readline().split(" ")
        if self.gaussmeter:  # if gaussmeter was used:
            x_channel = string_x_channel[0:-4]  # spectrum in the x channel
            self.mwfreq = float(string_x_channel[-3])       # mw frequency measured with the MW counter
            self.bstart_meas = float(string_x_channel[-2])  # start field measured with gaussmeter
            self.bstop_meas = float(string_x_channel[-1])   # stop field measured with gaussmeter
        else:
            x_channel = string_x_channel[0:-2]

        if self.twochannels:  # if both channels were recorded, read second channel
            string_y_channel = sf.readline().split(" ")
            if self.gaussmeter:
                y_channel = string_y_channel[0:-4]
            else:
                y_channel = string_y_channel[0:-2]

        # making the spectral components arrays:
        self.x_channel = np.asarray(x_channel, dtype=float)  # the x channel signal array
        if self.twochannels:
            self.y_channel = np.asarray(y_channel, dtype=float)  # the y channel signal array
        else:
            self.y_channel = self.bvalues*0  # there is nothing in the y channel, let us put permanently zero there

        # now that we have the spectral components, let us make the magnetic field axis:
        self.make_magnetic_field()  # calling the method of the cw_spectrum class that creates magnetic field
        self.sample = "not specified"
        self.comment = "no comments"

        # end of reading, close the spectrum file:
        self.spectrum_file.close()

    def __str__(self):
        return("cw_epr spectrum at %s"%self.file_path)

    def make_magnetic_field(self):
        '''making magnetic field axis from parameters of the class. Parameters should be loaded before.'''
        if self.gaussmeter:
            self.bvalues = np.linspace(self.bstart_meas, self.bstop_meas, self.npoints-1)
            # create the magnetic field array from the measured B values (start and end)
            print("making B axis from measured magnetic fields")
        else:
            self.bvalues = np.linspace(self.bstart, self.bstop+self.bstep, self.npoints-1)  # create the magnetic field array
            # create the magnetic field array from the set B values (start and end)
            print("making B axis from set magnetic fields")

    def autophase(self):
        '''maximizes the x channel by correcting the phase between the signals.
        Ask Dasha, she did it in Matlab'''
        pass

    def baseline_correct(self):
        '''subtracts baseline from both channels'''
        # X channel:
        baseline_parameters_x_channel = np.polyfit(self.bvalues, self.x_channel, 0)  # linear baseline for the X channel
        print("X channel baseline at %.7f " %baseline_parameters_x_channel) #just to be sure we fit the baseline correctly
        baseline_x_channel = baseline_parameters_x_channel[0] + (self.bvalues * 0)  #linear function
        self.x_channel = (self.x_channel - baseline_x_channel) # BG corrected X channel

        if self.twochannels:
            baseline_parameters_y_channel = np.polyfit(self.bvalues, self.y_channel, 0)  # linear baseline for the Y channel
            print("Y channel baseline at %.7f " %baseline_parameters_y_channel)  # just to be sure we fit the baseline correctly
            baseline_y_channel = baseline_parameters_y_channel[0] + (self.bvalues * 0)  # linear function
            self.y_channel = (self.y_channel - baseline_y_channel)  # BG corrected X channel
        else:
            self.y_channel = self.bvalues*0

    def normalize(self):
        '''normalize intensities of both channels to 1'''
        self.baseline_correct() # baseline correct first
        self.x_channel = self.x_channel * 2 / abs((max(self.x_channel) - min(self.x_channel)))
        if self.twochannels:
            self.y_channel = self.y_channel * 2 / abs((max(self.y_channel) - min(self.y_channel)))

    def correct_for_frequency(self):
        '''correct for the frequency deviation from 9.6 GHz'''
        x_band_frequency = 9.6e9  # GHz
        if not self.frequency_corrected: # otherwise you can correct until infinity
            self.bvalues = self.bvalues * x_band_frequency / self.mwfreq # g factor is the same, field stretchesa little bit
            self.frequency_corrected = True


    def save(self, file_path): # saves data in akku2 format, compatible with fscII
        self.savefile = open(file_path,'w')  # open the file
        f2w = self.savefile
        # ____________________________ saving spectrum to akku2 file _____________________________________________________________
        # following the structure of akku2. Fields of class must be populated before writing in file
        # the first line has to be adapted for different machines. Take care in the future.
        if self.twochannels:
            f2w.write('%%? 1d 2ch akku\n')
        else:
            f2w.write('%%? 1d 2ch akku\n')

        # time was created when experiment started

        f2w.write('%%? %s\n' % (str(self.time)))
        f2w.write('%%. %.2f mV %s' % (self.potential, self.comment))
        f2w.write('%%! nruns %d\n' % self.nruns)
        f2w.write('%%! npoints %d\n' % int(len(self.bvalues)+1))
        f2w.write('%%! bstart %.5f G\n' % self.bstart)
        f2w.write('%%! bstop %.5f G\n' % self.bstop)
        f2w.write('%%! bstep %.5f G\n' % self.bstep)
        f2w.write('%%! modamp %.8e %s\n' % (self.modamp, self.modamp_dim))
        f2w.write('%%! modfreq %.8e Hz\n' % self.modfreq)
        f2w.write('%%! li_tc %.8e s\n' % self.li_tc)
        f2w.write('%%! li_level %.8e V\n' % self.li_level)
        f2w.write('%%! li_phase %.2f deg\n' % self.li_phase)
        f2w.write('%%! li_sens %.8e V\n' % self.li_sens)
        f2w.write('%%! conv_time %d TC\n' % self.conv_time)
        f2w.write('%%! mwfreq %.8e Hz\n' % self.mwfreq)
        f2w.write('%%! attn %d dB\n' % self.attn)
        f2w.write('%%! temp %.2f K\n' % self.temp)
        f2w.write('%%! li_level %.2f V\n' % self.li_level)

        # now populating the values
        for value in self.x_channel:
            f2w.write("%.8e "%value)

        f2w.write('\n')

        for value in self.y_channel:
            f2w.write("%.8e "%value)

        # writing mw frequency
        # f2w.write(str(self.mwfreq)) # not now

        # writing measured B0 values if gaussmeter was used
        if self.gaussmeter:
            f2w.write(str(self.bstart_meas))
            f2w.write(str(self.bstop_meas))

        f2w.close()




    #TODO: make this happen and you dont need Matlab anymore ;-)
    def fsc2load(self,fsc2_spectrum_file_path):
        print("loading fsc2 spectrum from file. To be continued")
        print("read fsc2 file, determine all fields")
        print("initialize the cw_spectrum instance with the fields from this file")

    def eprload(self, bruler_spectrum_file_path):
        print("loading bruker xEpr spectrum from file. To be continued")
        print("read bruker xEpr file, lookup Stoll's code!")
        print("initialize the cw_spectrum instance with the fields from this file")

import setup_scan
def make_spectrum_from_scans(scans: [cw_spectrum], scan_setting: setup_scan.Scan_setup):
    # majes an averaged spectrum from the list of spectra in the input.
    container = cw_spectrum('')  # this is to be returned

    if len(scans) > 0:

        # If something is in the list:
        container = scans[0]
        averaged_signal_x = np.array(container.x_channel) * 0
        averaged_signal_y = np.array(container.y_channel) * 0
        # lets average now

        for sctrm in scans:  # going through the list of cw_spectra
            averaged_signal_x = averaged_signal_x + np.array(sctrm.x_channel)
            averaged_signal_y = averaged_signal_y + np.array(sctrm.y_channel)

        averaged_signal_x = averaged_signal_x / len(scans)  # normalization
        averaged_signal_y = averaged_signal_y / len(scans)  # normalization

        container.x_channel = averaged_signal_x
        container.y_channel = averaged_signal_y

    # now populating the fields of the spectrum from the scan setting.
    container.nruns = len(scans)
    container.npoints = len(container.bvalues)
    container.bstart = scan_setting.bstart
    container.bstop = scan_setting.bstop
    container.bstep = scan_setting.bstep
    container.modamp = scan_setting.modamp
    container.modamp_dim = scan_setting.modamp_dim
    container.modfreq = scan_setting.modfreq
    container.li_tc = scan_setting.li_tc
    container.li_level = scan_setting.li_level
    container.li_phase = scan_setting.li_phase
    container.li_sens = scan_setting.li_sens
    container.conv_time = scan_setting.conv_time
    container.mwfreq = scan_setting.mwfreq  # todo: get the mw frequency.
    container.attn = scan_setting.attn
    container.temp = scan_setting.temp
    container.li_level = scan_setting.li_level
    container.comment = scan_setting.comment

    return container
    # return scan 0 with its parameters, and with the averaged channels.





# file_path = filedialog.askopenfilename()
# print("opening spectrum at %s"%file_path)
# my_spectrum = cw_spectrum(file_path)  # create an instance of cw spectrum from file in file_path
# my_spectrum.correct_for_frequency()
# my_spectrum.normalize()
#
# ###########################
# #         plotting        #
# ###########################
#
# from matplotlib import pyplot as plt
# import math
#
# fig = plt.figure()
# ax = fig.add_axes([0.15,0.15,0.75,0.75])
# ax.plot(my_spectrum.bvalues, my_spectrum.x_channel, linewidth = 1.0)
# ax.plot(my_spectrum.bvalues, my_spectrum.x_channel-0.2, linewidth = 1.0)
# ax.plot(my_spectrum.bvalues, my_spectrum.x_channel-0.4, linewidth = 1.0)
# ax.plot(my_spectrum.bvalues, my_spectrum.x_channel-0.6, linewidth = 1.0)
# #ax.plot(magnetic_field,baseline)
# ax.set_title("cwEPR spectrum at 9.4 GHz")
# ax.set_xlabel("Magnetic field, G")
# ax.set_ylabel("amplitude, a.u.")
# plt.show()
#
