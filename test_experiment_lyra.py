'''example experiment. you speak to the machine with the communicator'''
import Plotter
import communication
from time import sleep
from PyQt5 import QtWidgets
import os # for checking if the magnettech files have appeared
import glob # location of files in folders

import cw_spectrum


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
        fc.go_remote()

        tmpSpectrum = cw_spectrum.cw_spectrum('')

        tmpSpectrum.bstart = 3350
        tmpSpectrum.bstop = 3400
        tmpSpectrum.npoints = 1024
        tmpSpectrum.bstep = float(tmpSpectrum.bstop - tmpSpectrum.bstart ) / tmpSpectrum.npoints

        self.EPRplotter.clear()
        self.EPRplotter.set_title('CWEPR')

        fc.set_center_field(tmpSpectrum.bstart)
        sleep(3)

        for sweepIndex in range(tmpSpectrum.npoints):
            sleep(0.1)
            fieldToSet = tmpSpectrum.bstart + sweepIndex*tmpSpectrum.bstep
            fc.set_center_field(fieldToSet)
            tmpSpectrum.x_channel.append(lia.getX())
            tmpSpectrum.y_channel.append(lia.getY())
            tmpSpectrum.bvalues.append(fieldToSet)
            self.EPRplotter.clear()
            self.EPRplotter.plotEprData(tmpSpectrum)

        fc.set_center_field(tmpSpectrum.bstart)
        sleep(3)

        tmpSpectrum.save('test_lyra_NC60_221004')



