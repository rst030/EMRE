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
import numpy as np
import lock_in
import EPRtools


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

        # populating the sensitivity and tc combo boxes
        # --- sensitivity combo box ---
        self.lia_sensitivity_comboBox.clear()  # clear what you put there in QtDesigner
        list_of_lia_sensitivities = lock_in.lockin.list_of_lia_sensitivities
        for sens in list_of_lia_sensitivities:
            self.lia_sensitivity_comboBox.addItem('%.0e'%sens) # SCPI code = index in combobox
        self.lia_sensitivity_comboBox.setCurrentIndex(np.where(np.array(list_of_lia_sensitivities)==100e-3)[0][0])
        # --- TC combo box ---
        self.lia_TC_comboBox.clear()  # clear what you put there in QtDesigner
        list_of_lia_TC = lock_in.lockin.list_of_lia_TC # constants are given in the lia class
        for TC in list_of_lia_TC:
            self.lia_TC_comboBox.addItem('%.0e' % TC)  # SCPI code = index in combobox
        self.lia_TC_comboBox.setCurrentIndex(np.where(np.array(list_of_lia_TC)==10e-3)[0][0])

        # --- TC combo box ---
        self.lia_conversion_time_comboBox.clear()  # clear what you put there in QtDesigner
        list_of_CT = [1,2,3,4,5,6,7,8,9,10]  # order of value is its SCPI code
        for TC in list_of_CT:
            self.lia_conversion_time_comboBox.addItem('%d' % TC)  # SCPI code = index in combobox
        self.lia_conversion_time_comboBox.setCurrentIndex(np.where(np.array(list_of_CT)==3)[0][0])

        # binding methods to buttons:
        self.importButton.clicked.connect(self.Import_parameters_from_file)
        self.go_button.clicked.connect(self.do_cwepr_scan)  # code that method
        self.abort_button.clicked.connect(self.abort_scan)  # code that method
        self.save_button.clicked.connect(self.save_spectrum) # code that method
        # --- EPR TOOLS ---
        self.g_calculator =  EPRtools.g_calculator()
        self.geButton.clicked.connect(self.set_ge)

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
        # and plot that spectrum
        self.EPRplotter.clear()
        self.EPRplotter.plotEprData(tmpSpectrum)


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
        self.lia_sensitivity_comboBox.setCurrentIndex(np.where(np.array(lock_in.lockin.list_of_lia_sensitivities)
                                                               == spc.li_sens)[0][0])
        self.lia_TC_comboBox.setCurrentIndex(np.where(np.array(lock_in.lockin.list_of_lia_TC)
                                                               == spc.li_tc)[0][0])
        self.lia_conversion_time_comboBox.setCurrentIndex(np.where(np.array(lock_in.lockin.list_of_lia_conversion_times)
                                                               == spc.conv_time)[0][0])

        self.n_scans_edit.setText('%d'%spc.nruns)
        self.attn_edit.setText('%d'%spc.attn)
        self.T_edit.setText('%d'%spc.temp)
        self.comment_textEdit.setText('%s'%spc.comment)

        # to EPR Tools:
        self.mw_freq_edit.setText('%.3f'%(spc.mwfreq/1e9))

    def do_cwepr_scan(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # apply positive current, go upto high point, then apply negative current and go downto low point
        self.spectrum = cw_spectrum.cw_spectrum('')
        self.EPRplotter.clear()
        self.EPRplotter.plotEprData(self.spectrum)

        print('take a CWEPR here!')

    def abort_scan(self): # stops all
        print('mayday! MAYDAY!')

    def save_spectrum(self):
        print('save the spectrum.')

# --- EPR TOOLS ---
    def set_ge(self):
        self.g_edit.setText('%.12f'%EPRtools.ge)
        self.g_edit.setStyleSheet("QLineEdit{background: #00ff9f}")

        #todo: finish g calculator