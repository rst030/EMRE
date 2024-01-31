""" 2017-2023 rst FUB rst030@protonmail.com"""
from PyQt5 import QtWidgets, uic
import sys # for finding the script path and importing scripts
import communication

import os
import importlib.util

#Queues for 'fast' devices
from multiprocessing import Process, Queue
from time import sleep

# utility windows:
import cvUtility
import chgUtility
import cweprUtility
import deviceManagerUtility


# logging for debug info and cmdline arg parsing
import logging
import argparse

# parse the log level
parser = argparse.ArgumentParser(description='This is the electron magnetic environment')
parser.add_argument('-d','--debug', dest='debug',help='switch to debug mode')
parser.add_argument('-q','--quiet', dest='quiet',help='run without gui')

my_args = parser.parse_args()
DEBUG=my_args.debug
QUIET=my_args.quiet # todo suppress gui and messages when called with -q

class Ui(QtWidgets.QMainWindow):
    """the main User Interface window."""
    def __init__(self):

        self.CWEPRgui = None
        self.CHGgui = None
        self.CVgui = None
        self.DevManGui = None

        self.communicator = None
        self.scriptPath = None # weirdly implemented user experiment class
        self.script = None
        self.experiment = None

        self.qGlob = Queue(maxsize = 100000)

        self.log = logging.getLogger("emre_logger")
        self.log.setLevel(logging.DEBUG if DEBUG == '1' else logging.INFO)
        logging.debug('Plain debug test') # for some reason necessary to initialise logging
        # get the script's directory
        # print('scripts working directory',os.path.dirname(sys.argv[0]))
        # os.chdir(os.path.dirname(sys.argv[0]))
        # get the root dir of the main exec script
        ROOT_PATH = os.path.dirname(sys.argv[0])
        if ROOT_PATH == '':
            # get current dir
            ROOT_PATH = os.getcwd()

        self.log.debug('Main working directory: %s'% ROOT_PATH)
        os.chdir(ROOT_PATH)

        super(Ui, self).__init__() # Call the inherited classes __init__ method
        try:
            uic.loadUi('gui/EMRE.ui', self) # Load the .ui file
        except:
            print('loading UI failed, cd to script folder')
            exit()
        self.show() # Show the GUI


        # binding methods to buttons:
        self.connect_button.clicked.connect(self.connect_to_spectrometer)  # Remember to pass the definition/method, not the return value!
        self.load_button.clicked.connect(self.load_script)  # Remember to pass the definition/method, not the return value!
        self.devman_button.clicked.connect(self.open_device_manager)  # Button to open the device manager
        self.CV_button.clicked.connect(self.open_CV_utility)  # cycling utility, use it for deposition and cleaning of your DIRTY FILMS
        self.CHG_button.clicked.connect(self.open_CHG_utility)  # charging utility, use it for testing your batteries (charge-discharge cycling)
        self.CWEPR_button.clicked.connect(self.open_CWEPR_utility)  # charging utility, use it for testing your batteries (charge-discharge cycling)

        # user-script-specific functions *when you load your script with "load script", emre uses these buttons to run it
        self.initialize_button.clicked.connect(self.initialize_experiment)  # Remember to pass the definition/method, not the return value!
        self.run_button.clicked.connect(self.run_experiment)
        self.abort_button.clicked.connect(self.abort_experiment)

    def connect_to_spectrometer(self):
        """connects to the spectrometer
        via the communication module.
        Initializes the available devices"""

        print('connecting to spectrometer.')
        self.communicator = communication.communicator(backend = '')

        self.infoLabel.setText('connected %d/%d'%(self.communicator.numRealDevices,self.communicator.numConnectedDevices))
        self.devman_button.setEnabled(True)
        self.CV_button.setEnabled(True)
        self.CHG_button.setEnabled(True)
        self.CWEPR_button.setEnabled(True)

    def load_script(self):
        """opens a file dialog to choose the file,
        loads the file as the "Experiment" class.
        The experiment class has to have methods "main" or "run\""""
        # choose the script file location
        self.scriptPath, _ = QtWidgets.QFileDialog.getOpenFileName(self,caption="Select script", directory="../scripts/",filter="All Files (*);;Python Files (*.py)")

        if self.scriptPath:
            print("loading script from %s"%os.path.dirname(self.scriptPath))
            print('script name:', os.path.basename(self.scriptPath))

        # script is a module, here we are loading it

            spec = importlib.util.spec_from_file_location(os.path.basename(self.scriptPath),self.scriptPath)

            self.script = importlib.util.module_from_spec(spec) # script is a field of EMRE. Just in case.
            spec.loader.exec_module(self.script)
            self.infoLabel.setText('user module loaded:\n%s' % os.path.basename(self.scriptPath))
            self.initialize_button.setEnabled(True)

        else:
            print('loading script cancelled')

    def open_device_manager(self):
        """creates and opens the device manager utility with self.communicator"""
        self.DevManGui = deviceManagerUtility.deviceManagerUI(self.communicator)

    def open_CV_utility(self):
        """ opens the CV GUI with CV the plotter in it."""
        self.qGlob = Queue(maxsize=10000)
        self.CVgui = cvUtility.CyclingUi(self.communicator.keithley_pstat, self.qGlob)

    def open_CHG_utility(self):
        """ opens the CHG GUI with the CHG plotter in it."""
        self.qGlob = Queue(maxsize=10)
        self.CHGgui = chgUtility.ChargingUi(self.communicator.keithley_pstat, self.qGlob)

    def open_CWEPR_utility(self):
        """ opens the CWEPR GUI with the CWEPR plotter in it."""
        self.qGlob = Queue(maxsize=128)
        self.CWEPRgui = cweprUtility.CweprUi(comm=self.communicator,q=self.qGlob)

    def initialize_experiment(self):
        '''sends the initial parameters to the spectrometer.
        parameters have to be defined in the loaded script.'''
        print('sending init param to the spectrometer.')
        self.experiment = self.script.experiment(communicator = self.communicator, plotter = None)  # experiment is a field of EMRE. It is globally visible.
        self.infoLabel.setText('experiment initialized')
        self.run_button.setEnabled(True)

    def run_experiment(self):
        '''executes the run() method from the experiment class.
         or rather: creates the experiment object by calling its constructor'''
        print('measurement sequence run')
        self.infoLabel.setText('running')
        self.experiment.run()
        self.infoLabel.setText('finished')

    def abort_experiment(self):
        print('stop machine!: todo')
        self.experiment.abort() #todo: add abort button to the experiment class



if __name__ == "__main__":
    q = Queue()

    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    window = Ui()  # Create an instance of our class
    app.exec_()  # Start the application

    # p_generator = Process(target=window.app.exec, args=(q,))
    # p_generator.start()
    #
    # p_generator.join()