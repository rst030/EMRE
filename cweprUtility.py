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
        self.EPRplotter.preset_EPR()

        # get a sample spectrum, populate fields in form
        dummySpectrum = cw_spectrum.cw_spectrum('./dummies/a01_cwEPR_50CV_cleaned_in_PC_AN_15CV_solid_state_modified_tube_RT_22dB.akku2')
        self.PopulateFieldsFromSpectrum(spc=dummySpectrum)
        self.EPRplotter.plotEprData(spectrum=dummySpectrum)

    def Import_parameters_from_file(self):
        # get a spectrum from the filename, populate fields in the gui

        filename = QFileDialog.getOpenFileName(self, 'Open file','/home/', "CWEPR files (*.akku2 *.ch1 *.ch2)")[0]

        tmpSpectrum = cw_spectrum.cw_spectrum(filename)
        self.PopulateFieldsFromSpectrum(tmpSpectrum)


    def PopulateFieldsFromSpectrum(self,spc:cw_spectrum.cw_spectrum):
        # get parameters from spectrum and populate fields in gui
        self.info_label.setText('%s'%spc.file_name)
        self.low_B_edit.setText('%.2f'%spc.bstart)
        self.high_B_edit.setText('%.2f' % spc.bstop)
        self.npoints_edit.setText('%d' % spc.npoints)
        self.use_GM_checkbox.setChecked(spc.gaussmeterFlag)
        self.mod_freq_edit.setText('%d'% round(spc.modfreq/1000))  # [khz]
        self.lia_phase_edit.setText('%d'% spc.li_phase)
        self.mod_amp_edit.setText('%.1f'% spc.modamp)
        self.modAmpDimensionCombobox.setCurrentIndex(int("V" in spc.modamp_dim))
        setup_sens_value = spc.li_sens # read value that is to be set, and acroll the combobox
        print('%.10f'%setup_sens_value)

        sens_values = [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4,
                       5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1] # order of value is its SCPI code

        formatted_sens_values = ["%.1e V" % elem for elem in sens_values] # for better representability
        indx = sens_values.index(setup_sens_value)
        self.lia_sensitivity_comboBox.clear() #todo: continue here populating fields
        self.lia_sensitivity_comboBox.configure(values = formatted_sens_values)
        self.lia_sensitivity_comboBox.setCurrentIndex(indx)

    def do_cwepr_scan(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # apply positive current, go upto high point, then apply negative current and go downto low point
        self.spectrum = cw_spectrum.cw_spectrum('')
        self.EPRplotter.plotEprData(self.spectrum)

        print('take a CWEPR here!')