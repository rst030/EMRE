'''example experiment. you speak to the machine with the communicator'''
import Plotter
import communication
from time import sleep
from PyQt5 import QtWidgets
import os # for checking if the magnettech files have appeared
import glob # location of files in folders

import cw_spectrum
import numpy as np

class experiment():
    name = 'test_experiment'
    data = []
    communicator = communication.communicator
    
    def __init__(self, communicator: communication.communicator, plotter:Plotter.Plotter):
        self.communicator = communicator
        self.communicator.list_devices()

        self.EPRplotter = plotter
        self.EPRplotter.preset_EPR()

        print('experiment initiated')


    def run(self):
        '''this method has to be here. one may call it in the constructor (__init__),
        but the experiment has to be pre-triggered! So running only after pre-triggering
        you can code here everything you want to happen.'''
        
        # just for convenience lets rename some of the objects
        comm = self.communicator
        right_hand = comm.right_hand 
        fc = comm.field_controller
        lia = comm.lockin

        tmpSpectrum = cw_spectrum.cw_spectrum('')

        tmpSpectrum.bstart = 3200
        tmpSpectrum.bstop = 3500
        tmpSpectrum.npoints = 512
        tmpSpectrum.bstep = float(tmpSpectrum.bstop - tmpSpectrum.bstart ) / tmpSpectrum.npoints

        self.EPRplotter.clear()
        self.EPRplotter.set_title('CWEPR')

        # ------------- set field sweep here ----------------------
        bvalues = np.linspace(tmpSpectrum.bstart, tmpSpectrum.bstop, tmpSpectrum.npoints) # these B values will be set
        fc.preset_field_scan(bvalues)
        fc.set_field(tmpSpectrum.bstart)
        sleep(3)

        for field_to_set in bvalues:
            sleep(0.01) #todo LIA's TC!
            measured_bfield = fc.set_field(field_to_set) # set the magnetic field, get the set magnetic field. #todo ER35M!!!
            tmpSpectrum.x_channel.append(lia.getX()) # get x channel of the LIA
            tmpSpectrum.y_channel.append(lia.getY()) # get y channel of the LIA
            tmpSpectrum.bvalues.append(measured_bfield) # pop
            self.EPRplotter.clear()
            self.EPRplotter.plotEprData(tmpSpectrum)

        fc.set_field(tmpSpectrum.bstart)
        sleep(3)

        tmpSpectrum.save('test_lyra_NC60_221004')



