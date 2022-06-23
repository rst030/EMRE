'''example experiment. you speak to the machine with the communicator'''

import communication
from time import sleep
from PyQt5 import QtWidgets
import os # for checking if the magnettech files have appeared
import glob # location of files in folders

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
        
        # just for convenience lets rename some of the objects
        comm = self.communicator
        pstat = comm.keithley_pstat
        right_hand = comm.right_hand 
        
        # ------------------------------------------------ give parameters here ----------------------------------------
        
        self.numCvCyclesToGo = 2 #how many degradtion cycles
        lowPotential = 0.2
        highPotential = 1.2
        rate = 100
        filePathToSaveCVs = './DATA/CV/220623/' # without extension (.csv is added automatically)
        filePathToSaveEPRs = './DATA/EPR/220623/' # where to search for the ESR studio files (specify it in ESRstudio!)
        
        # --------------------------------------------------------------------------------------------------------------
        # ---------------------- the main exmeriment sequence is happening here ----------------------------------------

        for step in range(1,self.numCvCyclesToGo+1):

            self.take_cwEPR(right_hand)
            self.take_CV(pstat=pstat,lowPotential=lowPotential,highPotential=highPotential,rate=rate,CVfilePath=filePathToSaveCVs,EPRfilepath=filePathToSaveEPRs,targetNumberOfScans = step)
            
    



    
    def take_CV(self,pstat,lowPotential,highPotential,rate,CVfilePath,EPRfilepath,targetNumberOfScans):
        
        # before running the CV, list files in the EPRfilepath directory (= how many files were generated by esrstudio?)
        # there is a folder with this timestamp
    
        # check with glob.glob how many files are there. if files as nscans: 
        numberoftrials = 0 # trials to find all spectra in the current folder
        maxnumberoftrials = 1200 # you got 20 minutes to get the first scan in the folder
        while numberoftrials <= maxnumberoftrials:
            numberoftrials = numberoftrials + 1
            sleep(1) # check floder each 1 second
            print('awaiting EPR spectra, attempt %d / %d \n path: \n'%(numberoftrials,maxnumberoftrials))
            patternString = '%s/*.xml'%(EPRfilepath)
            print(patternString)
            genFiles = glob.glob(patternString)
            print(genFiles)
            print(len(genFiles),' of ',targetNumberOfScans,' spectra were recorded')
            if (len(genFiles) == targetNumberOfScans): # if nscans .csv files then break, do next round.
                print('%d cw scan finished.\n recording CV now. '%targetNumberOfScans)    
                pstat.plotter.clear()
                pstat.plotter.title = 'CV [%d of %d]' % (targetNumberOfScans, self.numCvCyclesToGo)
                pstat.plotter.set_title(pstat.plotter.title)
                pstat.TakeCV(lowPotential=lowPotential,highPotential=highPotential,rate=rate,filePath=CVfilePath+'_%d' % targetNumberOfScans)
                return
        
        
    def take_cwEPR(self,right_hand):
        # click the start button in the ESRstudio
        right_hand.start_magnettech_sequence(1665, 70)