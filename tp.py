'''rst@FU 221017
tune picture module for EMRE
rst030@protonmail.com'''
from datetime import datetime
from scipy.signal import savgol_filter #great invention
import numpy as np

timeToFrequencyConversionFactor = 6.94e4  # MHz/<tunepicunit>

class tp():
    '''Tunepicture object. creted by scope on lyra or by Emre.'''

    tunepicture = [] # make it a real float array
    tunepicFit = tunepicture*0 # tunepicture fit
    time = [] # make it a real float array
    frequency = 0 # millivolts per second
    datetime = datetime.now
    tpFile = 0 # a file where cv is stored



    def __init__(self,filename=''):

        # --- set parameters ---
        self.low_time_point = 0
        self.high_time_point = 0

        # --- measure parameters ---
        self.tunepicture = []
        self.time = []
        self.filename = ''

        # --- from here on - import from file ---
        # if filename was given, user wants to import that cv
        if filename == '':
            filename = './dummies/TP.csv'
            print('ever got here?')

        self.tpFile = open(filename)  # open the file
        # populate the fields of the cv object from that csv file
        self.tpFile = open(filename)  # open the file
        self.filename = str(filename.split('/')[-1])
        tpf = self.tpFile  # for short
        datafile = tpf.readlines()
        linecounter = 0
        lineWhereDataStarts = 0

        for line in datafile:
            relTime = float(line.split(',')[-3])
            tunePicValue = float(line.split(',')[-2])
            self.time.append(relTime)
            self.tunepicture.append(tunePicValue)

        self.frequency =  np.asarray(self.time,float)*timeToFrequencyConversionFactor
        self.tunepicture = np.asarray(self.tunepicture)


    def saveAs(self,filename: str):
        fout = open('%s.csv' % filename, 'w')
        i = 0
        for symb in self.tunepicture:
            if i == 0:
                fout.write('datetime,00.00.0000,00:00:00.000,%.12f, %.5f\n' % (float(self.time[i]), float(symb)))
                continue

            fout.write(',,,%.12f, %.5f\n' % (float(self.time[i]), float(symb)))
            i = i + 1
        fout.close()

    def fitDip(self):
        print('cutting the dip of the tunepicture')

        # subtract the constant offset
        lofst = np.mean(self.tunepicture[0:32])
        self.tunepicFit = self.tunepicture - lofst # to play around
        self.tunepicture_blcorr = self.tunepicFit # to use later

        # find maximum of tunepicture:
        maxTp = max(self.tunepicFit)
        # determine the noise level
        noiseLvl = maxTp * 0.1 # 10% of TP is noise. #np.mean(abs(self.tunepicFit[0:16])) * 7 # to be safe
        # determine when tunepicture exceeds the noise level
        tpLeft = 0 # limits of the tunepicture
        tpRight = -1
        leftFlag = False  # for scanning through tp, limits.
        for i in range (len(self.tunepicFit)):
            if self.tunepicFit[i] > noiseLvl*7.5: # sharp left edge! change to *1 when fix the klystron
                if not leftFlag: # if never detected left of TP
                    print(f'TUNEPICTURE LEFT DETECTED, index={i:10d}')
                    tpLeft = i+60
                    leftFlag = True
            else: # if below noise
                if leftFlag and (self.tunepicFit[i] < noiseLvl*2): # and after left of TP
                    print(f'TUNEPICTURE RIGHT DETECTED, index={i:10d}')
                    tpRight = i-128
                    break


        dipWide = self.tunepicFit[tpLeft:tpRight] # dip with parabolic bg
        frequencyWide = self.frequency[tpLeft:tpRight] # frequency for the wide dip

        # cut out the dip
        # smooth out the dip
        # get the derivative of the TP between tpLeft and tpRight
        self.tunepicFit = low_pass_filter(np.diff(savgol_filter(dipWide, 60,2)),1000, 44100) #savgol_filter(np.diff(savgol_filter(self.tunepicFit, 37,3)),37,3)
        # cut out oscillations on edges
        cutOscIdx = 100
        self.tunepicFit = self.tunepicFit[cutOscIdx:-round(cutOscIdx*1.5)]
        self.frequencyFit = self.frequency[tpLeft+1+cutOscIdx:tpRight-round(cutOscIdx*1.5)] # +1 from derivative

        dipLeft = self.tunepicFit.argmin()
        print('left dip ',dipLeft)
        dipRight = self.tunepicFit.argmax()
        print('right dip ',dipRight)
        self.tunepicFit = self.tunepicFit[dipLeft:dipRight]
        self.frequencyFit = self.frequencyFit[dipLeft:dipRight]
        print('left dip ',self.frequencyFit[0])
        print('right dip ',self.frequencyFit[-1])


        # extract the parabola
        dataToFitParanola = dipWide
        freqToFitParabola = frequencyWide

        # TMP
        self.tunepicFit = dataToFitParanola
        self.frequencyFit = freqToFitParabola

        #TODO: all bs, do smoothing, find 2nd extremum, there is your dip/


        # self.tunepicFit = polyval ...
        # self.dipfit = ...

def get_derivative(x, y):
    smooth_y = savgol_filter(y, 37, 3)  # sav-gol(data,window,order)
    return x[1:], savgol_filter(np.diff(smooth_y), 37, 3)

def low_pass_filter(adata: np.ndarray, bandlimit: int = 1000, sampling_rate: int = 44100) -> np.ndarray:
    # translate bandlimit from Hz to dataindex according to sampling rate and data size
    bandlimit_index = int(bandlimit * adata.size / sampling_rate)

    fsig = np.fft.fft(adata)

    for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index):
        fsig[i] = 0

    adata_filtered = np.fft.ifft(fsig)

    return np.real(adata_filtered)

