from PyQt5 import QtWidgets, uic
class Ui(QtWidgets.QMainWindow):
    """the main User Interface window."""
    connect_button = None
    def __init__(self):

        self.CWEPRgui = None
        self.CHGgui = None
        self.CVgui = None
        self.DevManGui = None

        self.communicator = None
        self.scriptPath = None # weirdly implemented user experiment class
        self.script = None
        self.experiment = None

        # get the script's directory
        # print('scripts working directory',os.path.dirname(sys.argv[0]))
        # os.chdir(os.path.dirname(sys.argv[0]))
        # get the root dir of the main exec script

        super(Ui, self).__init__() # Call the inherited classes __init__ method
        try:
            uic.loadUi('../EMRE.ui', self) # Load the .ui file
        except:
            print('loading UI failed, cd to script folder')
            exit()
        self.show() # Show the GUI