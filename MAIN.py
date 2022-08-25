from PyQt5 import QtWidgets, uic
import sys # for finding the script path and importing scripts
import Plotter # for plotitng stuff online.
import communication

from tkinter import filedialog
import os.path
import importlib.util
import tkinter as tk
import cvUtility
import chgUtility

class Ui(QtWidgets.QMainWindow):
    '''the main User Interface window.'''
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('EMRE.ui', self) # Load the .ui file
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

        self.CV_button.clicked.connect(self.open_CV_utility)  # cycling utility, use it for deposition and cleaning of your DIRTY FILMS
        self.CHG_button.clicked.connect(self.open_CHG_utility)  # charging utility, use it for testing your batteries (charge-discharge cycling)


        self.initialize_button.clicked.connect(self.initialize_experiment)  # Remember to pass the definition/method, not the return value!
        self.run_button.clicked.connect(self.run_experiment)

        # --- adding the plotters: ---
        # EPR plotter:
        EPRplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'EPR_plotter_widget')
        self.EPRplotter = Plotter.Plotter(parent = EPRplotterWidgetFound)
        self.verticalLayout_EPR_plotter.addWidget(self.EPRplotter)
        self.verticalLayout_EPR_plotter.addWidget(self.EPRplotter.toolbar)
        self.EPRplotter.preset_EPR() # just add some labels

        # CV plotter:
        CVplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'CV_plotter_widget')
        self.CVplotter = Plotter.Plotter(parent=CVplotterWidgetFound)
        self.verticalLayout_CV_plotter.addWidget(self.CVplotter)
        self.verticalLayout_CV_plotter.addWidget(self.CVplotter.toolbar)
        self.CVplotter.preset_CV() # just add some labels

        # CHG plotter:
        CHGplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'CHG_plotter_widget') # locate the widget
        self.CHGplotter = Plotter.Plotter(parent=CHGplotterWidgetFound) # create the plotter with that widget
        self.verticalLayout_CHG_plotter.addWidget(self.CHGplotter)
        self.verticalLayout_CHG_plotter.addWidget(self.CHGplotter.toolbar)
        self.CHGplotter.preset_CHG() # just add some labels


    def connect_to_spectrometer(self):
        '''connects to the spectrometer
        via the communication module.
        Initializes the available devices'''

        print('connecting to spectrometer.')
        self.communicator = communication.communicator(backend = '', cvPlotter = self.CVplotter)
        self.infoLabel.setText('connected')

    def load_script(self):
        '''opens a file dialog to choose the file,
        loads the file as the "Experiment" class.
        The experiment class has to have the main method or the run method.'''
        print('opening the open dialog to select the script file.')


        # choose the script file location (where rops the files)
        self.scriptPath = filedialog.askopenfilename(parent=None, initialdir=r"../scripts/", title="Select shkript", filetypes = (("python files","*.py"),("all files","*.*")))


        print("loading script from %s"%os.path.dirname(self.scriptPath))
        print('script name:', os.path.basename(self.scriptPath))

        # script is a module, here we are loading it

        spec = importlib.util.spec_from_file_location(os.path.basename(self.scriptPath),self.scriptPath)

        self.script = importlib.util.module_from_spec(spec) # script is a field of EMRE. Just in case.
        spec.loader.exec_module(self.script)
        self.infoLabel.setText('user module loaded:\n%s' % os.path.basename(self.scriptPath))

    def open_CV_utility(self):
        ''' opens the CV GUI with CV the plotter in it.'''
        self.CVgui = cvUtility.CyclingUi(self.communicator.keithley_pstat)

    def open_CHG_utility(self):
        ''' opens the CHG GUI with the CHG plotter in it.'''
        self.CHGgui = chgUtility.ChargingUi(self.communicator.keithley_pstat)

    def initialize_experiment(self):
        '''sends the initial parameters to the spectrometer.
        parameters have to be defined in the loaded script.'''
        print('sending init param to the spectrometer.')
        self.experiment = self.script.experiment(communicator = self.communicator)  # ecxperiment is a field of EMRE. It is globally visible.
        self.infoLabel.setText('experiment initialized')

    def run_experiment(self):
        '''executes the run() method from the experiment class.
         or rather: creates the experiment object by calling its constructor'''
        print('measurement sequence run')
        self.infoLabel.setText('running')
        self.experiment.run()
        self.infoLabel.setText('finished')


#todo: add abort button!
app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
app.exec_() # Start the applicatio
