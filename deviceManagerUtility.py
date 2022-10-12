''' Device Manager GUI module for EMRE.
    29 Aug 2022
    rst '''
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTreeWidgetItem
import communication

class deviceManagerUI(QtWidgets.QMainWindow):
    '''the Dvice Manager utility window.'''
    communitator = communication.communicator # the communicator to be passed with a constructor
    devList = []

    def __init__(self, comm: communication.communicator):
        super(deviceManagerUI, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('EMRE_device_manager_module.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # --- connect the communicator ---
        self.communitator = comm

        # getting the devices from the communicator
        pstat = comm.keithley_pstat
        lockin = comm.lockin
        field_controller = comm.field_controller
        freq_counter = comm.frequency_counter
        right_hand = comm.right_hand

        self.devList = [pstat,lockin,field_controller,freq_counter,right_hand]

        # initialization of buttons and labels:
        self.info_label.setText('Device Manager')

        tree = self.treeWidget
        tree.setColumnCount(3)
        tree.setHeaderLabels(['type','address','connected'])


        devItems = []  # list of QTreeWidgetItem to add

        self.refresh_list()
        # for dev in self.devList:
        #     itm = QTreeWidgetItem()
        #     itm.setText(0, dev.type)
        #     itm.setText(1, str(dev.address))
        #     itm.setText(2, str(not dev.fake))
        #
        #     devItems.append(itm)  # create QTreeWidgetItem's and append them
        #
        # tree.addTopLevelItems(devItems)  # add everything to the tree



        self.refresh_button.setText('Refresh List')

        # binding methods to buttons:
        self.refresh_button.clicked.connect(self.refresh_list)  # code that method
        self.send_button.clicked.connect(self.send_commend)  # code that method
        self.read_button.clicked.connect(self.read_device)  # code that method


    def refresh_list(self):
        '''get all devices seen by the communicator'''
        list_of_devices = self.communitator.list_devices()
        ListOfDeviceItems = []
        for dev in list_of_devices:
            itm = QTreeWidgetItem()
            itm.setText(0,dev.type)
            itm.setText(1, str(dev.address))
            itm.setText(2, str(not dev.fake))
            itm.device = dev
            ListOfDeviceItems.append(itm)

        self.treeWidget.clear()
        self.treeWidget.addTopLevelItems(ListOfDeviceItems)

        #todo: add all devices that have to be there'''


    def send_commend(self):
        try:
            slectedTreeWidgetItem = self.treeWidget.selectedItems()[0]
            device = slectedTreeWidgetItem.device
        except:
            print('no dev selected, click on an item!')
            return 0

        cmd = self.lineEdit.text()
        print('writing ',cmd,' to ',device)
        try:
            device.write(cmd)
        except:
            print('cant write to', device)



    def read_device(self):
        try:
            slectedTreeWidgetItem = self.treeWidget.selectedItems()[0]
            device = slectedTreeWidgetItem.device
        except:
            print('no dev selected, click on an item!')
            return 0
        try:
            response = device.read()
            print('read from',device,' : ',str(response))
            self.lineEdit.setText(str(response))
        except:
            print('cant read from', device)
            self.lineEdit.setText("CANT SPEAK")