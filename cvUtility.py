''' CV utility module for EMRE.
    09 Aug 2022
    rst '''
from PyQt5 import QtWidgets, uic
import os

from tkinter import filedialog
import Plotter # an EMRE module for plotting
import keithley_pstat # an EMRE module for communicating to a keithley potentiostat
import cv # class of cv, makes an object of a cv. Can import from file. Attributes: voltage[], current[], etc

class CyclingUi(QtWidgets.QMainWindow):
    '''the cycling utility window.'''
    pstat = keithley_pstat.pstat # the keithley with which the CV or CHG is recorded.
    workingFolder = r"./dummies/"  # where the openfiledialog opens

    def __init__(self, pstat: keithley_pstat.pstat):
        super(CyclingUi, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('EMRE_cycling_module.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # initialization of buttons and labels:
        self.go_button.setText('Go!')
        self.abort_button.setText('Abort')
        self.save_button.setText('Save as')
        self.load_button.setText('Load')

        self.info_label.setText('')

        # binding methods to buttons:
        self.go_button.clicked.connect(self.do_cv_scan)  # Remember to pass the definition/method, not the return value!
        self.abort_button.clicked.connect(self.abort_cv_scan)  # Remember to code the method in the class.
        self.save_button.clicked.connect(self.save_cv)  # Remember to code the method in the class.
        self.load_button.clicked.connect(self.load_cv)  # Remember to code the method in the class.

        # --- adding the plotter: ---
        # CV plotter:
        CVplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'CV_plotter_widget')
        self.CVplotterWGT = Plotter.Plotter(parent=CVplotterWidgetFound)
        self.verticalLayout_CV_plotter.addWidget(self.CVplotterWGT)
        #self.verticalLayout_CV_plotter.addWidget(self.CVplotter.toolbar)
        self.CVplotter = self.CVplotterWGT.PlotterCanvas
        self.CVplotter.preset_CV()  # just add some labels

        # --- connect the pstat ---
        self.pstat = pstat


    def do_cv_scan(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # go from low point to high_point downto low_point for n_cycles cycles at scan_rate rate
        self.cv = cv.cv()
        self.cv.low_voltage_point = float(self.low_edit.text())/1000 # in Volts!
        self.cv.high_voltage_point  = float(self.high_edit.text())/1000 # in Volts!
        self.cv.scan_rate = float(self.rate_edit.text())/1000 # in Volts per second!
        self.cv.n_cycles = int(self.n_edit.text())
        self.cv.currentLimitInMicroamps = float(self.current_limit_edit.text())

        # get the cv with the potentiostat
        self.pstat.GlobalInterruptFlag = False
        self.pstat.TakeCV(self.cv, self.CVplotter)
        print('taking a cv')

    def abort_cv_scan(self):
        print('stop that crazy pstat, and turn the output off!')
        self.pstat.output_off()
        self.pstat.GlobalInterruptFlag = True
    def save_cv(self):
        print('save as file dialog etc, think of the format, Be compatible with the Keithley stuff!!!')
        # open open file dialog
        try:
            self.CVPath = filedialog.asksaveasfilename(parent=None, initialdir=self.workingFolder, title="Selekt foolder, insert name",
                                                 filetypes=(("comma separated values", "*.csv"), ("all files", "*.*")))
            self.workingFolder = os.path.split(os.path.abspath(self.CVPath))[0]
        except:
            print('no filename given, do it again.')
            return 0

        if self.cv != 0:
            print('')
            self.cv.saveAs(self.CVPath)


    def load_cv(self):
        print('load the cv file, plot the curve in the plotter and populate the fields.')
        # open open file dialog
        try:
            self.CVPath = filedialog.askopenfilename(parent=None, initialdir=self.workingFolder, title="Select shkript", filetypes = (("comma separated values","*.csv"),("all files","*.*")))
            self.workingFolder = os.path.split(os.path.abspath(self.CVPath))[0]
        except:
            print('no filename given, do it again.')
            return 0

        # import the cv curve as an object
        self.cv = cv.cv(filename = self.CVPath)
        # and print it on the plotter.
        self.CVplotter.plotCv(self.cv)