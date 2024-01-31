'''communication to the TDS2002C oscilloscope.
221017 rst@FUB
rst030@protonmail.com'''

import usbtmc
from datetime import datetime

class scope (object):
    type = 'scope'
    model = 'TDS2002C'                   # default model is the TDS2002C at Lyra
    address = 'USB0::1689::929::C011897::0::INSTR'   # and this is its USB address
    #'USB0::2733::281::030031632::0::INSTR'          # Hall-setup R&S scope
    device = 0                   # pyvisa device that is populated with the constructor
    rm = 0                        # visa resource manager
    fake = True                  # use simulated outputs. Used for testing outside the lab.

    curve = ['a,csv,file,is,a,text,file,separated,with,commas']    # that is what we are hunting for
    dt = 0 # datetime when tp is taken

    def __init__(self):
        if len(usbtmc.list_devices()) == 0:
            print("usbtmc returned empty list of devices. usb cable?")
            self.fake = True
            return
        else:
            self.connect()


    def connect(self):
        print('connecting to', usbtmc.list_devices()[0], '...\n')
        self.scope = usbtmc.Instrument(usbtmc.list_devices()[0])
        if print(self.scope.ask("*IDN?")):
            self.fake = False


    def write(self,cmd):  # methods work with fake device
        if self.fake:
            return('fake talking')
        else:
            self.scope.write(cmd)

    def read(self):  # methods work with fake device
        if self.fake:
            return('fake bla')
        else:
            return(self.scope.read())

    def get_tunepicture(self):
        '''
         this method returns a waveform of the channel 1 of the scope.
         The connection to the scope is specified in the connect_to_scope method
         The commmands are sent in ASCII encoding via USB.

         1. configure the data format and waveform locations
         2. request a waveform of Ch1'''

        self.write("DATA:SOURCE CH1")  # choose the source of data
        self.write("DATa:ENCdg ASCII")  # choose the encoding
        self.write("DATa:WIDth 1")  # 2 bytes per point
        self.write("ACQ:MOD SAMPLE")  # sample, not averaged picture
        curve = self.scope.ask("CURVE?")
        self.dt = datetime.now()  # datetime on query
        print("tune picture captured at\n")
        print(self.dt.strftime('%A %d.%m.%Y, %H:%M:%S.%f'))
        return curve

    def saveTunePictureToFile(self,filename:str): # saves the tunepicture to a csv file

        curve = self.get_tunepicture().split(',')
        try:
            xint = self.scope.ask('WFMPre:XINcr?')  # get x interval
        except:
            xint = 2.000000e-07
            print('failed acquiring x interval using default value %.1e s' % xint)
        # now lets save this in the file.
        filename = filename
        fout = open(filename, 'w')

        i = 0
        for symb in curve:
            if i == 0:
                fout.write(
                    'datetime,%s,%.12f, %.5f,\n'
                    % (self.dt.strftime('%d.%m.%Y, %H:%M:%S.%f'),
                       float(xint) * i, float(symb)))

            else:
                fout.write(',,,%.12f, %.5f,\n' % (float(xint) * i, float(symb)))
            i = i + 1

        fout.close()
        print('tune picture saved as %s' % fout.name)
