'''rst@FU 221017
tune picture module for EMRE
rst030@protonmail.com'''
from datetime import datetime
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
        # find maximum of tunepicture:

        dipLeft = 10
        dipRight = 20
        dip = np.asarray(self.tunepicture[dipLeft:dipRight])
        self.tunepicFit = [np.asarray(self.tunepicture[0:dipLeft]), dip, np.asarray(self.tunepicture[dipRight:-1])] # TEMP!!!





