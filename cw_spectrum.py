
from datetime import datetime

import numpy
import numpy as np
import os
# copy it from the plotting module, disgraceful!

class cw_spectrum:
    '''cw EPR spectrum recorded on lyra
    and some methods for processing it'''

    file_path = ""     # file path with data
    file_name = ""  # file name, not the full path
    spectrum_file = 0  # spectrum file
    index = 0          # index in the tree view

# to be in file
    twochannels = False # recorded two channels?
    mwfreqFlag = False # mwfreq recorded?
    gaussmeterFlag = False  # gaussmeter used?
    datetime = datetime.now() # date/time of experiment

    bstart = 0        # start value of magnetic field
    bstop = 0         # upper limit of magnetic field
    modamp = 0        # modulation amplitude
    modamp_dim = 'V'  # V or G
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

    bstart_meas = 0
    bstop_meas = 0     # magnetic fields measured with gaussmeter
    nruns = 0          # number of scans
    npoints = 0        # number of magnetic field points

    # for lia
    li_sens_SCPI_code = 0
    li_tc_SCPI_code = 0

# === these are for plotting ===
    bvalues = []    # magnetic field axis
    x_channel = []  # spectral x channel component
    y_channel = []  # spectral y channel component

    frequency_corrected = False

    # === these are for saving spectrum to a file ===
    savefile = 0 # file to save data

    # === these are for electrochemistry ===
    potential = 0  # to be populated in the amperometry scan.
    current = 0 # to be populated in the potentiometry scan

    def __init__(self,filepath):
        ''''create instance of cwepr spectrum with parameters and data.
        Magnetic field axis is created.
        Call normalize to normalize.
        Call baseline_correct to base line correct
        Write autophase method to put signal to X channel'''

        # by now this works by loading a fsc2 akku2 spectrum from file.
        # replace it by self.fsc2load to get cw_spectrum from akku2 file (look at file format)
        # or use self.eprload to get cw_spectrum from xEpr files.

        if filepath == '':  # if no file path given, just create a container. Used for getting spectra irl.
            self.bvalues = []
            self.x_channel = []
            self.y_channel = []
            print('empty cwEPR spectrum created')
            return

        self.file_path = filepath # we will work with the file from here
        print("importing cwEPR spectrum from: %s" %self.file_path)

        self.spectrum_file = open(self.file_path,'r') # open the file
        self.file_name = os.path.basename(self.file_path)  # name of the file
        self.fsc2load(self.spectrum_file)


    def fsc2load(self,cwf):
        # read all lines of the spectrum
        # get tokens, populate fields in the cw_spectrum object
        dataLines = cwf.readlines()

        for line in dataLines:

            if '%' in line: # % = if not data
                if '?' in line: # %? = if info lines
                    if '2ch' in line: # both channels?
                        self.twochannels = True
                    if ':' in line:   # time?
                        dt_string = line[3:-2]
                        _format = "%Y-%m-%d %H:%M:%S"
                        try:
                            #self.datetime = datetime.strptime("2019-07-02 16:20:00", _format)
                            self.datetime = datetime.strptime(str(dt_string), _format)
                        except:
                            self.datetime = datetime(year=1970,month=1,day=1,hour=0,minute=0,second=0)

                    if 'addcols' in line:
                        if 'mwfreq' in line: # mwfreq recorded?
                            self.mwfreqFlag = True
                        if '_meas' in line:  # gaussmeter field recorded?
                            self.gaussmeterFlag = True
                if '%.' in line:  # %. = comment line
                    self.comment = str(line[3:-1])
                if '%!' in line:  # %! = data fields, populate from here by tokens!
                    splitvals = line.split(' ')
                    token = splitvals[1]
                    if token == 'nruns':
                        self.nruns = int(splitvals[2])
                    if token == 'npoints':
                        self.npoints = int(splitvals[2])
                    if token == 'bstart':
                        self.bstart = float(splitvals[2])
                    if token == 'bstop':
                        self.bstop = float(splitvals[2])
                    if token == 'modamp':
                        self.modamp = float(splitvals[2])
                        self.modamp_dim = str(splitvals[3])
                    if token == 'modfreq':
                        self.modfreq = float(splitvals[2])
                    if token == 'li_tc':
                        self.li_tc = float(splitvals[2])*self._suffix_to_factor(str(splitvals[-1]))
                    if token == 'li_level':
                        self.li_level = float(splitvals[2])
                    if token == 'li_phase':
                        self.li_phase = float(splitvals[2])
                    if token == 'li_sens':
                        self.li_sens = float(splitvals[2])*self._suffix_to_factor(str(splitvals[-1]))
                        print('SUFFIX: ',str(splitvals[-1]))
                    if token == 'conv_time':
                        self.conv_time = int(splitvals[2])
                    if token == 'mwfreq':
                        self.mwfreq = float(splitvals[2])
                    if token == 'attn':
                        self.attn = float(splitvals[2])
                    if token == 'temp':
                        self.temp = float(splitvals[2])
            else: # if data
                string_x_channel = dataLines[-2].split(" ") # 2nd last line is always the x channel

                if self.mwfreqFlag: # if mw frequency was recorded
                    self.mwfreq = float(string_x_channel[-3])

                if self.gaussmeterFlag: # if gaussmeter was used
                    self.bstart_meas = float(string_x_channel[-2])
                    self.bstop_meas = float(string_x_channel[-1])

                self.x_channel = np.asarray(string_x_channel[1:-3],float)

                if self.twochannels: # if two channels were recorded
                    string_y_channel = dataLines[-1].split(" ")
                    self.y_channel = np.asarray(string_y_channel[1:-3],float)
                break
        self.bvalues = np.linspace(start = self.bstart, stop = self.bstop,num = len(self.x_channel))





    def _suffix_to_factor(self,suffix):
        '''# stupid but necessary: switches uV to 1e-6 and so on'''
        print(suffix)
        if 'n' in suffix:
            return 1e-9
        if 'u' in suffix:
            return 1e-6
        if 'm' in suffix:
            return 1e-3
        if 'V' in suffix:
            return 1e-0
        if 's' in suffix:
            return 1e-0
        if 'k' in suffix:
            return 1e3
        else:
            return 0



    def __str__(self):
        return("cw_epr spectrum at %s"%self.file_path)

    def make_magnetic_field(self):
        '''making magnetic field axis from parameters of the class. Parameters should be loaded before.'''
        if self.gaussmeterFlag:
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
        print("X channel baseline at %.7f " %baseline_parameters_x_channel[0]) #just to be sure we fit the baseline correctly
        baseline_x_channel = baseline_parameters_x_channel[0] + (self.bvalues * 0)  #linear function
        self.x_channel = (self.x_channel - baseline_x_channel) # BG corrected X channel

        if self.twochannels:
            baseline_parameters_y_channel = np.polyfit(self.bvalues, self.y_channel, 0)  # linear baseline for the Y channel
            print("Y channel baseline at %.7f " %baseline_parameters_y_channel[0])  # just to be sure we fit the baseline correctly
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
            f2w.write('%? 1d 2ch akku\n')
        else:
            f2w.write('%? 1d 2ch akku\n') # Oi!

        # time was created when experiment started

        f2w.write('%%? %s\n' % (str(self.datetime)))
        f2w.write('%%? addcols EMRE\n')
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
        if self.mwfreqFlag:
            f2w.write(str(self.mwfreq))

        # writing measured B0 values if gaussmeter was used
        if self.gaussmeterFlag:
            f2w.write(str(self.bstart_meas))
            f2w.write(str(self.bstop_meas))

        f2w.close()



    #TODO: make this happen and you dont need Matlab anymore ;-)
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