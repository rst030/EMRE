'''example experiment.
    you speak to the machine with the communicator'''

import communication
#import Plotter
from time import sleep
from PyQt5 import QtWidgets

class experiment():
    name = 'test_experiment'
    data = []
    communicator = communication.communicator
    
    def __init__(self, communicator: communication.communicator):
        self.communicator = communicator
        self.communicator.list_devices()
        print('experiment initiated')


    def run(self):
        '''this method has to be here. one may call it in the constructor (__init__),
        but the experiment has to be pre-triggered! So running only after pre-triggering
        you can code here everything you want to happen.'''

        # ------------------------------------------------ give parameters here ----------------------------------------
        numCvCyclesToGo = 5
        lowPotential = 0
        highPotential = 1
        rate = 1000
        filePathToSaveCVs = '../../dummies/test_CV' # without extension (.csv is added automatically)
        # --------------------------------------------------------------------------------------------------------------


        # just for convenience lets rename some of the objects
        comm = self.communicator
        pstat = comm.keithley_pstat
        right_hand = comm.right_hand
        # ---------------------- the main exmeriment sequence is happening here ----------------------------------------

        for step in range(1,numCvCyclesToGo):

            right_hand.start_magnettech_sequence(1000, 600)

            pstat.plotter.clear()
            pstat.plotter.title = 'CV [%d of %d]' % (step, numCvCyclesToGo)
            pstat.plotter.set_title(pstat.plotter.title)

            pstat.TakeCV(lowPotential=lowPotential,highPotential=highPotential,rate=rate,filePath=filePathToSaveCVs+'_%d' % step)