from PyQt5 import QtWidgets, uic
import sys # for finding the script path and importing scripts
import Plotter # for plotitng stuff online.
import communication

import os
import importlib.util
import tkinter as tk

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
my_args = parser.parse_args()
DEBUG=my_args.debug

class Ui(QtWidgets.QMainWindow):
    '''the main User Interface window.'''
    def __init__(self):
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
            uic.loadUi('EMRE.ui', self) # Load the .ui file
        except:
            print('loading UI failed, cd to script folder')
            exit()
        self.show() # Show the GUI

        # for the open dialog we have to create a blank Tk window and then withdraw it.
        self._window=tk.Tk()
        self._window.title("The window I initzialized")
        self._window.withdraw()

        # initialization of buttons and labels:
        self.connect_button.setText('Connect to spectrometer')
        self.infoLabel.setText('Welcome to EMRE')# = self.findChild(QtWidgets.QLabel, 'cvCountlabel') # Find the button - useful method

        # binding methods to buttons:
        self.connect_button.clicked.connect(self.connect_to_spectrometer)  # Remember to pass the definition/method, not the return value!

        self.load_button.clicked.connect(self.load_script)  # Remember to pass the definition/method, not the return value!

        self.devman_button.clicked.connect(self.open_device_manager)  # Button to open the device manager

        self.CV_button.clicked.connect(self.open_CV_utility)  # cycling utility, use it for deposition and cleaning of your DIRTY FILMS
        self.CHG_button.clicked.connect(self.open_CHG_utility)  # charging utility, use it for testing your batteries (charge-discharge cycling)
        self.CWEPR_button.clicked.connect(self.open_CWEPR_utility)  # charging utility, use it for testing your batteries (charge-discharge cycling)

        self.initialize_button.clicked.connect(self.initialize_experiment)  # Remember to pass the definition/method, not the return value!
        self.run_button.clicked.connect(self.run_experiment)
        self.abort_button.clicked.connect(self.abort_experiment)

        # --- adding the plotters: ---
        # EPR plotter:
        EPRplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'EPR_plotter_widget')
        #self.EPRplotter = Plotter.Plotter(parent = EPRplotterWidgetFound)
        self.EPRplotterWGT = Plotter.Plotter(parent=EPRplotterWidgetFound,type = 'EPR')
        self.verticalLayout_EPR_plotter.addWidget(self.EPRplotterWGT)
        #self.verticalLayout_EPR_plotter.addWidget(self.EPRplotterWGT.Plotter.toolbar)
        self.EPRplotter = self.EPRplotterWGT.PlotterCanvas

        # CV plotter:
        CVplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'CV_plotter_widget')
        self.CVplotterWGT = Plotter.Plotter(parent=CVplotterWidgetFound,type='CV')
        self.verticalLayout_CV_plotter.addWidget(self.CVplotterWGT)
       # self.verticalLayout_CV_plotter.addWidget(self.CVplotter.toolbar)
        self.CVplotter = self.CVplotterWGT.PlotterCanvas

        # CHG plotter:
        CHGplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'CHG_plotter_widget') # locate the widget
        self.CHGplotterWGT = Plotter.Plotter(parent=CHGplotterWidgetFound,type='CHG') # create the plotter with that widget
        self.verticalLayout_CHG_plotter.addWidget(self.CHGplotterWGT)
        #self.verticalLayout_CHG_plotter.addWidget(self.CHGplotter.toolbar)
        self.CHGplotter = self.CHGplotterWGT.PlotterCanvas

    def connect_to_spectrometer(self):
        '''connects to the spectrometer
        via the communication module.
        Initializes the available devices'''

        print('connecting to spectrometer.')
        self.communicator = communication.communicator(backend = '')
        self.communicator.keithley_pstat.plotter = self.CVplotter
        self.infoLabel.setText('connected')
        self.devman_button.setEnabled(True)
        self.CV_button.setEnabled(True)
        self.CHG_button.setEnabled(True)
        self.CWEPR_button.setEnabled(True)

    def load_script(self):
        '''opens a file dialog to choose the file,
        loads the file as the "Experiment" class.
        The experiment class has to have the main method or the run method.'''
        print('opening the open dialog to select the script file.')


        # choose the script file location (where rops the files)
        # self.scriptPath = filedialog.askopenfilename(parent=None, initialdir=r"../scripts/", title="Select script", filetypes = (("python files","*.py"),("all files","*.*")))
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
        self.DevManGui = deviceManagerUtility.deviceManagerUI(self.communicator)



    def open_CV_utility(self):
        ''' opens the CV GUI with CV the plotter in it.'''
        self.CVgui = cvUtility.CyclingUi(self.communicator.keithley_pstat)

    def open_CHG_utility(self):
        ''' opens the CHG GUI with the CHG plotter in it.'''
        self.CHGgui = chgUtility.ChargingUi(self.communicator.keithley_pstat)


    def open_CWEPR_utility(self):
        ''' opens the CWEPR GUI with the CWEPR plotter in it.'''
        self.CWEPRgui = cweprUtility.CweprUi(comm=self.communicator)

    def initialize_experiment(self):
        '''sends the initial parameters to the spectrometer.
        parameters have to be defined in the loaded script.'''
        print('sending init param to the spectrometer.')
        self.experiment = self.script.experiment(communicator = self.communicator, plotter = self.EPRplotter)  # ecxperiment is a field of EMRE. It is globally visible.
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


#todo: add abort button!
def threaded_function(arg):
    print("running")
    app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
    window = Ui() # Create an instance of our class
    app.exec_() # Start the applicatio


from threading import Thread

if __name__ == "__main__":
    thread = Thread(target = threaded_function, args = (10, ))
    thread.start()
    thread.join()
    print("thread finished...exiting")
