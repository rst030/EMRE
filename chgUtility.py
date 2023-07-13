''' CHG utility module for EMRE.
    25 Aug 2022
    rst '''
from PyQt5 import QtWidgets, uic
import os
import Plotter  # an EMRE module for plotting
import keithley_pstat  # an EMRE module for communicating to a keithley potentiostat
import chg  # class of cv, makes an object of a cv. Can import from file. Attributes: voltage[], current[], etc

from time import sleep
from PyQt5 import QtWidgets
from PyQt5.QtCore import *

from multiprocessing import Queue


class data_visualisation_thread(QThread):  # this is the data vis thread. Reads data from q and plots to Plotter
    def __init__(self, plotter: Plotter.Plotter, q: Queue):
        super(data_visualisation_thread, self).__init__()
        self.plotter = plotter
        self.q = q

    def run(self):
        print('CHG plotter: queue empty?', self.q.empty())
        tmpCHG = chg.chg()

        while 1==1:
            sleep(0.05)
            while not self.q.empty():
                tmpCHG = self.q.get()
                print(self.q.qsize())
            else:
                self.plotter.plotChg(tmpCHG)
                sleep(0.1)
                if self.q.empty():
                    self.wait()
                    self.quit()
                    break



class data_generating_thread(QThread):  # oт это у нас кусрэд, но наш, русскaй, родной, ТТТ.
    def __init__(self, pstat: keithley_pstat, q: Queue, chg_init: chg.chg):  # and here is its constructor
        super(data_generating_thread, self).__init__()  # from a parent to be born
        self.quit_flag = False  # and no flag was given to ever quit anything
        self.pstat = pstat
        self.q = q  # there put what you have done in your miserable life
        self.chg = chg_init  # whsat kind of function to be called in this thread

    def run(self):  # it waits, like a cat in a bush, when you call it. Run! - you shout.

        print('chgUTility QThread running, type CHG')

        self.do_chg()

        self.wait()
        self.quit()


    def do_chg(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        chgTmp = self.chg
        print(chgTmp.filename)

        # get the CHG with the potentiostat
        self.pstat.GlobalInterruptFlag = False
        self.pstat.TakeCHG(self.chg, self.q)
        print('taking a CHG')


class ChargingUi(QtWidgets.QMainWindow):
    '''the charging utility window.'''
    pstat = keithley_pstat.pstat  # the keithley with which the CV or CHG is recorded.

    chg = chg.chg  # instance of cv, global variable, careful.
    q = Queue  # queue for pstat to put things into

    workingFolder = r"./dummies/"  # where the openfiledialog opens

    def __init__(self, pstat: keithley_pstat.pstat, q: Queue):
        super(ChargingUi, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('gui/EMRE_charging_module.ui', self)  # Load the .ui file
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
        self.CHGplotterWGT = Plotter.Plotter(parent=CVplotterWidgetFound, plotType='CHG')
        self.verticalLayout_CV_plotter.addWidget(self.CHGplotterWGT)
        # self.verticalLayout_CV_plotter.addWidget(self.CHGplotter.toolbar)
        self.CHGplotter = self.CHGplotterWGT.PlotterCanvas
        self.CHGplotter.preset_CHG()  # just add some labels

        # --- connect the pstat ---
        self.pstat = pstat
        self.q = q

    def closeEvent(self, event):
        # do stuff
        if self.q.empty():
            while not self.q.empty():
                print(self.q.get())
            event.accept()  # let the window close
        else:
            event.ignore()

        self.gen_trd.quit()
        self.vis_trd.quit()
        print('user closed CHG window, measurement stopped')
        self.destroy()

    def do_chg_scan(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
        # apply positive current, go upto high point, then apply negative current and go downto low point
        self.chg = chg.chg()
        self.chg.time = []
        self.chg.voltage = []

        self.chg.chg_current = float(self.chg_edit.text()) / 1e6  # in Amps!
        self.chg.dcg_current = float(self.dcg_edit.text()) / 1e6  # in Amps!
        self.chg.high_voltage_level = float(self.high_edit.text()) / 1000  # in Volts!
        self.chg.low_voltage_level = float(self.low_edit.text()) / 1000  # in Volts!
        self.chg.n_cycles = int(self.ncycles_edit.text())

        # parallel computing
        self.gen_trd = data_generating_thread(pstat=self.pstat, q=self.q, chg_init=self.chg)
        # because it hangs on a laptop
        self.vis_trd = data_visualisation_thread(plotter=self.CHGplotter, q=self.q)

        self.gen_trd.start()
        self.vis_trd.start()

    def abort_chg_scan(self):
        print('stop that crazy pstat, and turn the output off!')
        self.pstat.output_off()
        self.pstat.GlobalInterruptFlag = True
        self.gen_trd.quit()
        self.vis_trd.quit()

    def save_chg(self):
        print('save as file dialog etc, think of the format, Be compatible with the Keithley stuff!!!')
        # open open file dialog
        try:
            # self.CHGPath = filedialog.asksaveasfilename(parent=None, initialdir=self.workingFolder, title="Selekt foolder, insert name",
            # filetypes=(("comma separated values", "*.csv"), ("all files", "*.*")))
            self.CHGPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Select folder, insert name",
                                                                    directory=self.workingFolder,
                                                                    filter="comma separated values (*,csv);all files (*)")
            self.workingFolder = os.path.split(os.path.abspath(self.CHGPath))[0]
        except:
            print('no filename given, do it again.')
            return 0

        if self.chg != 0:
            print('saving chg potentiometry...')
            self.chg.saveAs(self.CHGPath)
            print('potentiometry saved')

    def load_chg(self):
        print('load the CHG file, plot the curve in the plotter and populate the fields.')
        # open file dialog

        try:
            self.CHGPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Select CHG data",
                                                                   directory=self.workingFolder,
                                                                   filter="All Files (*);;CSV Files (*.csv)")
            self.workingFolder = os.path.split(os.path.abspath(self.CHGPath))[0]

        except:
            print('no filename given, do it again.')
            return 0


        # import the chg curve as an object
        self.chg = chg.chg(filename=self.CHGPath)
        print(self.chg.filename)
        print(self.chg.time)

        # and print it on the plotter.
        self.CHGplotter.plotChg(self.chg)
