''' CV utility module for EMRE.
    09 Aug 2022
    rst '''
from PyQt5 import QtWidgets, uic
import os
from time import sleep # for dev only

import Plotter  # an EMRE module for plotting
import keithley_pstat  # an EMRE module for communicating to a keithley potentiostat
import cv  # class of cv, makes an object of a cv. Can import from file. Attributes: voltage[], current[], etc

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import time

from multiprocessing import Queue


class data_visualisation_thread(QThread): # this is the data vis thread. Reads data from q and plots to Plotter
    def __init__(self,plotter:Plotter.Plotter, q:Queue):
        super(data_visualisation_thread, self).__init__()
        self.plotter = plotter
        self.q = q

    def run(self):
        print('CV plotter: queue empty?', self.q.empty())
        slp = 0.5
        sleep(slp)
        cvY = cv.cv()
        while True:
            if not self.q.empty():
                while not self.q.empty():
                    cvY = self.q.get()
                self.plotter.plotCv(cvY)
                slp = cvY.delayBetweenPointsInSeconds
                sleep(slp)
            else:
                sleep(2*slp)
                if self.q.empty():
                    break
        self.quit()
        self.wait()

class data_generating_thread(QThread): # oт это у нас кусрэд, но наш, русскaй, родной, ТТТ.
    def __init__(self, pstat:keithley_pstat, q:Queue, cv_init:cv.cv):  # and here is its constructor
        super(data_generating_thread, self).__init__() # from a parent to be born
        self.quit_flag = False # and no flag was given to ever quit anything
        self.pstat = pstat
        self.q = q # there put what you have done in your miserable life
        self.cv = cv_init # whsat kind of function to be called in this thread

    def run(self): # it waits, like a cat in a bush, when you call it. Run! - you shout.

        print('cvUTility QThread running, type CV')

        self.do_cv()

        self.quit()
        self.wait()

    def do_cv(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        cvTmp = self.cv
        print(cvTmp.filename)
        cvTmp.filename = 'temp_cv'
        print(cvTmp.filename)

        # get the cv with the potentiostat
        self.pstat.GlobalInterruptFlag = False
        print('taking a cv')
        self.pstat.TakeCV(cvTmp, self.q)




class CyclingUi(QtWidgets.QMainWindow):
    '''the cycling utility window.'''
    pstat = keithley_pstat.pstat # the keithley with which the CV or CHG is recorded.

    cvGlob = cv.cv  # instance of cv, global variable, careful.
    q = Queue  # queue for pstat to put things into

    workingFolder = r"./dummies/"  # where the openfiledialog opens

    def __init__(self, pstat: keithley_pstat.pstat, q:Queue):
        super(CyclingUi, self).__init__()  # Call the inherited classes __init__ method

        uic.loadUi('gui/EMRE_cycling_module.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # working folder
        self.CVPath = None

        # binding methods to buttons:
        self.go_button.clicked.connect(self.do_cv_scan)  # Remember to pass the definition/method, not the return value!
        self.abort_button.clicked.connect(self.abort_cv_scan)  # Remember to code the method in the class.
        self.save_button.clicked.connect(self.save_cv)  # Remember to code the method in the class.
        self.load_button.clicked.connect(self.load_cv)  # Remember to code the method in the class.

        # --- adding the plotter: ---
        # CV plotter:
        CVplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'CV_plotter_widget')
        self.CVplotterWGT = Plotter.Plotter(parent=CVplotterWidgetFound, plotType = 'CV')
        self.verticalLayout_CV_plotter.addWidget(self.CVplotterWGT)
        #self.verticalLayout_CV_plotter.addWidget(self.CVplotter.toolbar)
        self.CVplotter = self.CVplotterWGT.PlotterCanvas
        self.CVplotter.preset_CV()  # just add some labels

        # --- connect the pstat ---
        self.pstat = pstat
        self.q=q

        # todo create two processes. One speaks with pstat, other plots stuff



    def do_cv_scan(self):
        # create initial cv and populate its fields
        self.cvGlob = cv.cv()
        self.cvGlob.low_voltage_point = float(self.low_edit.text()) / 1000  # in Volts!
        self.cvGlob.high_voltage_point = float(self.high_edit.text()) / 1000  # in Volts!
        self.cvGlob.scan_rate = float(self.rate_edit.text()) / 1000  # in Volts per second!
        self.cvGlob.n_cycles = int(self.n_edit.text())
        self.cvGlob.currentLimitInMicroamps = float(self.current_limit_edit.text())

        # parallel computing
        self.gen_trd = data_generating_thread(pstat=self.pstat, q=self.q, cv_init=self.cvGlob)
        # because it hangs on a laptop
        self.vis_trd = data_visualisation_thread(plotter=self.CVplotter, q=self.q)

        self.gen_trd.start()
        self.vis_trd.start()

    def do_cv_scan_old(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # go from low point to high_point downto low_point for n_cycles cycles at scan_rate rate

        # start process with data generation, update cv in the q
        # start process with data collection, read cv from the q

        self.cvGlob = cv.cv()
        self.cvGlob.low_voltage_point = float(self.low_edit.text())/1000 # in Volts!
        self.cvGlob.high_voltage_point  = float(self.high_edit.text())/1000 # in Volts!
        self.cvGlob.scan_rate = float(self.rate_edit.text())/1000 # in Volts per second!
        self.cvGlob.n_cycles = int(self.n_edit.text())
        self.cvGlob.currentLimitInMicroamps = float(self.current_limit_edit.text())

        # get the cv with the potentiostat
        self.pstat.GlobalInterruptFlag = False

        #self.q = Queue(maxsize=100000)
        print('here?')

        TESTCCLS = 100
        for i in range(TESTCCLS):
            # spit that to the queue every x seconds
            sleep(0.1)
            print('new cv. q deep?',self.q.qsize())
            self.q.put(self.cvGlob)


    def abort_cv_scan(self):
        print('stop that crazy pstat, and turn the output off!')
        self.pstat.output_off()
        self.pstat.GlobalInterruptFlag = True
        self.gen_trd.quit()
        self.vis_trd.quit()


    def save_cv(self):
        print('save as file dialog etc, think of the format, Be compatible with the Keithley stuff!!!')
        # open file dialog
        try:

            self.CVPath, _ = QtWidgets.QFileDialog.getSaveFileName(self,caption="Select folder, insert name",
                                                                   directory=self.workingFolder, filter="comma "
                                                                                                        "separated "
                                                                                                        "values ("
                                                                                                        "*.csv);all "
                                                                                                        "files (*)")
            self.workingFolder = os.path.split(os.path.abspath(self.CVPath))[0]
        except:
            print('no filename given, do it again.')
            return 0

        if self.cvGlob != 0:
            print('')
            self.cvGlob.saveAs(self.CVPath)

    def load_cv(self):
        print('load the cv file, plot the curve in the plotter and populate the fields.')
        # open file dialog
        try:
            self.CVPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Select CV data",
                                                                   directory=self.workingFolder,
                                                                   filter="All Files (*);;CSV Files (*.csv)")
            self.workingFolder = os.path.split(os.path.abspath(self.CVPath))[0]

        except:
            print('no filename given, do it again.')
            return 0

        # import the cv curve as an object
        self.cvGlob = cv.cv(filename = self.CVPath)
        # and print it on the plotter.
        self.CVplotter.plotCv(self.cvGlob)