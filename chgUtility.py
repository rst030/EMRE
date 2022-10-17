''' CHG utility module for EMRE.
    25 Aug 2022
    rst '''
from PyQt5 import QtWidgets, uic
import os
from tkinter import filedialog
import Plotter # an EMRE module for plotting
import keithley_pstat # an EMRE module for communicating to a keithley potentiostat
import chg # class of cv, makes an object of a cv. Can import from file. Attributes: voltage[], current[], etc

class ChargingUi(QtWidgets.QMainWindow):
    '''the charging utility window.'''
    pstat = keithley_pstat.pstat # the keithley with which the CV or CHG is recorded.
    workingFolder = r"./dummies/" # where the openfiledialog opens

    def __init__(self, pstat: keithley_pstat.pstat):
        super(ChargingUi, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('EMRE_charging_module.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # initialization of buttons and labels:
        self.go_button.setText('Go!')
        self.abort_button.setText('Abort')
        self.save_button.setText('Save as')
        self.load_button.setText('Load')

        self.info_label.setText('')

        # binding methods to buttons:
        self.go_button.clicked.connect(self.do_chg_scan)  # code that method
        self.abort_button.clicked.connect(self.abort_chg_scan)  # Remember to code the method in the class.
        self.save_button.clicked.connect(self.save_chg)  # Remember to code the method in the class.
        self.load_button.clicked.connect(self.load_chg)  # Remember to code the method in the class.

        # --- adding the plotter: ---
        # CV plotter:
        CVplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'CV_plotter_widget')
        self.CHGplotterWGT = Plotter.Plotter(parent=CVplotterWidgetFound,type='CHG')
        self.verticalLayout_CV_plotter.addWidget(self.CHGplotterWGT)
        #self.verticalLayout_CV_plotter.addWidget(self.CHGplotter.toolbar)
        self.CHGplotter = self.CHGplotterWGT.PlotterCanvas
        self.CHGplotter.preset_CHG()  # just add some labels

        # --- connect the pstat ---
        self.pstat = pstat


    def do_chg_scan(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # apply positive current, go upto high point, then apply negative current and go downto low point
        self.chg = chg.chg()
        self.chg.time = []
        self.chg.voltage = []

        self.chg.chg_current = float(self.chg_edit.text()) / 1e6 # in Amps!
        self.chg.dcg_current = float(self.dcg_edit.text()) / 1e6  # in Amps!
        self.chg.high_voltage_level = float(self.high_edit.text()) / 1000 # in Volts!
        self.chg.low_voltage_level = float(self.low_edit.text())  / 1000 # in Volts!
        self.chg.n_cycles = int(self.ncycles_edit.text())

        # get the CHG with the potentiostat
        self.pstat.GlobalInterruptFlag = False
        self.pstat.TakeCHG(self.chg, self.CHGplotter)
        print('taking a CHG')

    def abort_chg_scan(self):
        print('stop that crazy pstat, and turn the output off!')
        self.pstat.output_off()
        self.pstat.GlobalInterruptFlag = True

    def save_chg(self):
        print('save as file dialog etc, think of the format, Be compatible with the Keithley stuff!!!')
        # open open file dialog
        try:
            self.CHGPath = filedialog.asksaveasfilename(parent=None, initialdir=self.workingFolder, title="Selekt foolder, insert name",
                                                 filetypes=(("comma separated values", "*.csv"), ("all files", "*.*")))
            self.workingFolder = os.path.split(os.path.abspath(self.CHGPath))[0]
        except:
            print('no filename given, do it again.')
            return 0

        if self.chg != 0:
            print('saving chg potentiometry...')
            self.chg.saveAs(self.CHGPath)
            print('potentiometry saved')


    def load_chg(self):
        print('load the cv file, plot the curve in the plotter and populate the fields.')
        # open open file dialog
        try:
            self.CHGPath = filedialog.askopenfilename(parent=None, initialdir=self.workingFolder, title="Select shkript", filetypes = (("comma separated values","*.csv"),("all files","*.*")))
            self.workingFolder = os.path.split(os.path.abspath(self.CHGPath))[0]
        except:
            print('no filename given, do it again.')
            return 0
        # import the chg curve as an object
        self.chg = chg.chg(filename = self.CHGPath)
        # and print it on the plotter.
        self.CHGplotter.plotChgData(self.chg)