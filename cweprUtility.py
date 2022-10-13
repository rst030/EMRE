''' CWEPR utility module for EMRE.
    12 Okt 2022
    rst '''

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

import os
#from tkinter import filedialog
import Plotter # an EMRE module for plotting
import communication
import cw_spectrum # class of cw_spectrum, makes an object of a cw_spectrum. Can import from file

class CweprUi(QtWidgets.QMainWindow):
    '''the cwEPR utility window.'''
    lock_in = communication.communicator.lockin
    field_controller = communication.communicator.field_controller
    frequency_counter = communication.communicator.frequency_counter
    workingFolder = r"./dummies/" # where the openfiledialog opens
    spectrum = cw_spectrum.cw_spectrum

    def __init__(self, comm: communication.communicator):
        super(CweprUi, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('EMRE_CWEPR_module.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # initialization of buttons and labels:
        self.go_button.setText('Go!')

        self.info_label.setText('')

        # binding methods to buttons:
        self.importButton.clicked.connect(self.Import_parameters_from_file)
        self.go_button.clicked.connect(self.do_cwepr_scan)  # code that method


        # --- adding the plotter: ---
        # EPR plotter:
        EPRplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'EPR_plotter_widget')
        self.EPRplotterWGT = Plotter.Plotter(parent=EPRplotterWidgetFound)
        self.verticalLayout_EPR_plotter.addWidget(self.EPRplotterWGT)
        #self.verticalLayout_CV_plotter.addWidget(self.CHGplotter.toolbar)
        self.EPRplotter = self.EPRplotterWGT.PlotterCanvas
        self.EPRplotter.preset_EPR()  # just add some labels

    def Import_parameters_from_file(self):
        # get a spectrum from the filename, populate fields in the gui

        filename = QFileDialog.getOpenFileName(self, 'Open file','/home/', "CWEPR files (*.akku2 *.ch1 *.ch2)")[0]

        tmpSpectrum = cw_spectrum.cw_spectrum(filename)
        self.PopulateFieldsFromSpectrum(tmpSpectrum)
        print(tmpSpectrum.time)
        print(tmpSpectrum.mwfreq)
        print(tmpSpectrum.modfreq)
        print(tmpSpectrum.attn)


    def PopulateFieldsFromSpectrum(self,spc:cw_spectrum.cw_spectrum):
        # get parameters from spectrum and populate fields in gui
        self.info_label.setText('%s'%spc.file_name)



    def do_cwepr_scan(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # apply positive current, go upto high point, then apply negative current and go downto low point
        self.spectrum = cw_spectrum.cw_spectrum('')

        print('take a CWEPR here!')