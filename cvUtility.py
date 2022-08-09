''' CV utility module for EMRE.
    09 Aug 2022
    rst '''
from PyQt5 import QtWidgets, uic
import Plotter

class CyclingUi(QtWidgets.QMainWindow):
    '''the cycling utility window.'''
    # todo: think about the pstat.

    def __init__(self):
        super(CyclingUi, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('EMRE_cycling_module.ui', self)  # Load the .ui file #todo: draw the EMRE_cycling_module.ui
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
        self.CVplotter = Plotter.Plotter(parent=CVplotterWidgetFound)
        self.verticalLayout_CV_plotter.addWidget(self.CVplotter)
        self.verticalLayout_CV_plotter.addWidget(self.CVplotter.toolbar)
        self.CVplotter.preset_CV()  # just add some labels

    def do_cv_scan(self):
        print('get the fields from the gui\ncheck if everygthing is ok,\nrun the sequence.')
    def abort_cv_scan(self):
        print('stop that crazy pstat, and turn the output off!')
    def save_cv(self):
        print('save as file dialog etc, think of the format, Be compatible with the Keithley stuff!!!')
    def load_cv(self):
        print('load the cv file, plot the curve in the plotter and populate the fields.')

