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
from time import sleep
import lock_in # i want to know the fields of lia, good for coding
import EPRtools # g calculator
import tp # tunepicture object


class CweprUi(QtWidgets.QMainWindow):
    '''the cwEPR utility window.'''

    comm = communication.communicator

    # --- EPR ---
    lock_in = comm.lockin
    field_controller = comm.field_controller
    frequency_counter = comm.frequency_counter
    workingFolder = r"./dummies/" # where the openfiledialog opens
    spectrum = cw_spectrum.cw_spectrum
    ABORT_FLAG = True # flag to abort everything

    # --- TUNE PICTURE ---
    tp = tp.tp # tunepicture

    def __init__(self, comm: communication.communicator):
        # hardware to pass!
        self.comm = comm
        self.lock_in = comm.lockin
        self.field_controller = comm.field_controller
        self.frequency_counter = comm.frequency_counter


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
        self.calcGButton.clicked.connect(self.calculate_g)
        self.calcFieldButton.clicked.connect(self.calculate_B)
        self.calcMWfreqButton.clicked.connect(self.calculate_mwfq)
        # --- TUNE PICTURE ---
        self.importDipButton.clicked.connect(self.import_tunepicture)
        self.fitDipButton.clicked.connect(self.fit_tunepicture) # draw a fit on top of the tunepicture
        self.QfactorButton.clicked.connect(self.calculate_Q) # calculate Q from fit


        # --- adding the plotter: ---
        # EPR plotter:
        #EPRplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'EPR_plotter_widget')
        self.EPRplotterWGT = Plotter.Plotter(parent=None,type = 'EPR')
        self.verticalLayout_EPR_plotter.addWidget(self.EPRplotterWGT)
        #self.verticalLayout_CV_plotter.addWidget(self.CHGplotter.toolbar)
        self.EPRplotter = self.EPRplotterWGT.PlotterCanvas
        self.Import_parameters_from_file(filename = './dummies/a01_cwEPR_50CV_cleaned_in_PC_AN_15CV_solid_state_modified_tube_RT_22dB.akku2')

        # tune picture poltter
        #TPplotterWidgetFound = self.findChild(QtWidgets.QWidget, 'TunePictureWidget')
        self.tp = tp.tp()
        self.TPplotterWGT = Plotter.Plotter(parent=None,type='TP')
        self.verticalLayout_TP_plotter.addWidget(self.TPplotterWGT)
        self.TPplotter = self.TPplotterWGT.PlotterCanvas
        self.TPplotterWGT.setMinimumWidth(230)
        self.TPplotterWGT.setMaximumWidth(230)
        self.TPplotter.plotTpData(self.tp)




    def Import_parameters_from_file(self,filename=False):
        # get a spectrum from the filename, populate fields in the gui
        if not filename:
            filename = QFileDialog.getOpenFileName(self, 'Open file','/home/', "CWEPR files (*.akku2)")[0]

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
        self.MWFQ = spc.mwfreq



    def PopulateSpectrumFromFields(self,spc:cw_spectrum.cw_spectrum):
        # get parameters from spectrum and populate fields in gui
        spc.file_name = str(self.info_label.text())
        spc.bstart = float(self.low_B_edit.text())
        spc.bstop = float(self.high_B_edit.text())
        spc.npoints = int(self.npoints_edit.text())
        spc.gaussmeterFlag = self.use_GM_checkbox.checkState()
        spc.li_phase = float(self.lia_phase_edit.text())
        spc.modamp = float(self.mod_amp_edit.text())
        spc.modamp_dim = self.modAmpDimensionCombobox.currentText()
        # LIA sensitivity
        spc.li_sens = float(self.lia_sensitivity_comboBox.currentText())
        spc.li_sens_SCPI_code = int(self.lia_sensitivity_comboBox.currentIndex())
        # LIA TC
        spc.li_tc = float(self.lia_TC_comboBox.currentText())
        spc.li_tc_SCPI_code_SCPI_code = int(self.lia_TC_comboBox.currentIndex())
        # conversion time
        spc.conv_time = int(self.lia_conversion_time_comboBox.currentText())
        # n scans
        spc.nruns = int(self.n_scans_edit.text())
        # attn
        spc.attn = int(self.attn_edit.text())
        # temperature
        spc.temp = float(self.T_edit.text())
        # comment
        spc.comment = self.comment_textEdit.toPlainText()

    def do_cwepr_scan(self):
        self.ABORT_FLAG = False
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # ????? apply positive current, go upto high point, then apply negative current and go downto low point
        self.spectrum = cw_spectrum.cw_spectrum('')
        spc = self.spectrum  # for short
        self.EPRplotter.clear()
        self.EPRplotter.plotEprData(spc)

        # capture fields and constants from the gui:
        self.PopulateSpectrumFromFields(spc)
        # preset LIA
        lia = self.lock_in
        lia.set_frequency(frequency_in_hz=spc.modfreq)
        lia.set_phase(spc.li_phase)

        if 'G' in spc.modamp_dim:
            lia.set_modamp(modamp_in_gauss = spc.modamp, frequency_in_hz = spc.modfreq) #todo
        if 'V' in spc.modamp_dim:
            lia.set_voltage(spc.modamp)

        lia.set_sensitivity(code=spc.li_sens_SCPI_code)
        lia.set_time_constant(code=spc.li_tc_SCPI_code)
        # dont forget about the conversion time!

        # Preset field vector in the field controller
        fc = self.field_controller
        bvaluesToScan = np.linspace(start = spc.bstart, stop = spc.bstop, num = spc.npoints)
        fc.preset_field_scan(bvaluesToScan)
        fc.set_field(spc.bstart) # push the fc to the left most field
        fc.check_set_field(spc.bstart) # make sure the controller is on field
        for field_to_set in bvaluesToScan:
            if self.ABORT_FLAG: # the hard way
                continue
            measured_bfield = fc.set_field(field_to_set)  # set the magnetic field, get the set magnetic field. #todo ER35M!!!
            spc.x_channel.append(lia.getX())  # get x channel of the LIA
            spc.y_channel.append(lia.getY())  # get y channel of the LIA
            spc.bvalues.append(measured_bfield)  # pop
            self.EPRplotter.clear()
            self.EPRplotter.plotEprData(spc)
            sleep(spc.li_tc*spc.conv_time)
        fc.set_field(spc.bstart)
        print('one CWEPR scan recorded.')


    def abort_scan(self): # stops all
        print('mayday! MAYDAY!')
        self.ABORT_FLAG = True
        self.lock_in.set_voltage(0)
        print("Field Modulation OFF!")

    def save_spectrum(self):
        print('save the spectrum. Steal it from the CHG module!')











# --- EPR TOOLS ---
    def set_ge(self):
        self.g_edit.setText('%.12f'%EPRtools.ge)
        self.g_edit.setStyleSheet("QLineEdit{background: #00ff9f}") # what calculated goes green
        self.B_edit.setStyleSheet("QLineEdit{background: #ffffff}")
        self.mw_freq_edit.setStyleSheet("QLineEdit{background: #ffffff}")

    def calculate_g(self):
        # get g from mwfq and B
        mwfq = float(self.mw_freq_edit.text())*1e9 # Hz
        b0 = float(self.B_edit.text())/1e4 # T
        gcalc = self.g_calculator.calculate_g(_mwfq=mwfq,_b0=b0) # calculate g from given fields

        self.g_edit.clear()
        self.g_edit.setText('%.12f' % gcalc)
        self.g_edit.setStyleSheet("QLineEdit{background: #00ff9f}")  # what calculated goes green
        self.B_edit.setStyleSheet("QLineEdit{background: #ffffff}")
        self.mw_freq_edit.setStyleSheet("QLineEdit{background: #ffffff}")

    def calculate_B(self):
        # get B from mwfq and g
        mwfq = float(self.mw_freq_edit.text()) * 1e9  # Hz
        g = float(self.g_edit.text())
        b0calc = self.g_calculator.calculate_b0(_mwfq=mwfq, _g = g)  # calculate B from given fields

        self.B_edit.clear()
        self.B_edit.setText('%.2f' % float(b0calc*1e4))
        self.B_edit.setStyleSheet("QLineEdit{background: #00ff9f}")  # what calculated goes green
        self.g_edit.setStyleSheet("QLineEdit{background: #ffffff}")
        self.mw_freq_edit.setStyleSheet("QLineEdit{background: #ffffff}")

    def calculate_mwfq(self):
        # get B from mwfq and g
        b0 = float(self.B_edit.text())/1e4 # T
        g = float(self.g_edit.text())
        mwfqcalc = self.g_calculator.calculate_mwfq(_b0=b0,_g=g)  # calculate mwfq from given fields

        self.mw_freq_edit.clear()
        self.mw_freq_edit.setText('%.4f' % float(mwfqcalc / 1e9)) # GHz
        self.mw_freq_edit.setStyleSheet("QLineEdit{background: #00ff9f}")  # what calculated goes green
        self.g_edit.setStyleSheet("QLineEdit{background: #ffffff}")
        self.B_edit.setStyleSheet("QLineEdit{background: #ffffff}")

        self.MWFQ = mwfqcalc

    # --- EPR TOOLS ---

    def import_tunepicture(self, filename=False):
        if not filename:
            filename = QFileDialog.getOpenFileName(self, 'Open file', './', "Tunepicture files (*.CSV)")[0]
        tmpTP = tp.tp(filename)
        self.tp = tmpTP # now tp is a field in the CWEPR module.
        print(self.tp)
        print('TP initiated in CWEPR module')
        self.TPplotter.clear()
        self.TPplotter.plotTpData(tmpTP)

    def calculate_Q(self):
        #MWFQ = self.MWFQ
        MWFQ = float(self.mw_freq_edit.text())*1e9 # Hz# get MWFQ from the MWFQ edit
        FWHM = self.tp.FWHM_in_hz
        self.Q = MWFQ/FWHM
        self.qEdit.setText('%.0f' % float(self.Q))




        #todo: Q fit, save, get tunepicture from scope


    #rst, 230128, fitting the Q value.
    # on FIT button press in the CWEPRUTILITY, call fitting.
    # first cut out the dip,
    # then fit the parabola
    # then fit a lorentzian
    def fit_tunepicture(self):
        tp = self.tp
        print(tp)
        tp.fitDip()  # here it happens, the fit.
        self.TPplotter.clear()
        self.TPplotter.plotTpData(tp)
        self.TPplotter.plotTpFitData(tp)



