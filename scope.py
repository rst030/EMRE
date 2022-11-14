'''communication to the TDS2002C oscilloscope.
221017 rst @ FUB
rst030@protonmail.com'''

import communication
import pyvisa as visa

class scope (object):
    type = 'scope'
    model = 'TDS2002C'                   # default model is the TDS2002C at Lyra
    address = 'USB0::1689::929::C011897::0::INSTR'   # and this is its USB address
    #'USB0::2733::281::030031632::0::INSTR'          # Hall-setup R&S scope
    device = 0                   # pyvisa device that is populated with the constructor
    rm = 0                        # visa resource manager
    fake = True                  # use simulated outputs. Used for testing outside the lab.

    curve = ['a,csv,file,is,a,text,file,separated,with,commas']    # that is what we are hunting for


    def __init__(self, rm: visa.ResourceManager): # when create a scope you'd better have a resource manager already working
        '''create an instance of the lock-in amplifier object'''
        self.rm = rm
        self.connect()

    def connect(self):
        ''' constructor for the scope.
        Need rights. Modify the 99-ni... file and restart udev. have a look here:
        https://stackoverflow.com/questions/52256123/unable-to-get-full-visa-address-that-includes-the-serial-number
        we will need to use the system interpreter. If so, installing packages is not possible for non-roots.
        When using vitrual eivironment, accessing gpib can be troublesome.
        '''
        try:
            self.device.close()
        except:
            print('no scope to close, ok.')

        try:
            self.device = self.rm.open_resource(self.address) #LYRA tds 2002C scope
            self.write('*IDN?')
            response = self.read()
            print('scope connected:\n' + response)  # if ok return scope's id)
            self.fake = False
        except:
            print('ERROR: failed connecting to scope')
            self.fake = True

    def write(self,cmd):  # methods work with fake device
        if self.fake:
            return('fake talking')
        else:
            self.device.write(cmd)

    def read(self):  # methods work with fake device
        if self.fake:
            return('fake bla')
        else:
            return(self.device.read())

    def get_tunepicture(self):
        '''
        this method returns a waveform of the channel 1 of the scope.
        The connection to the scope is specified in the connect_to_scope method
        The commmands are sent in ASCII encoding via GPIB or USB interface.

        1. configure the data format and waveform locations
        2. request a waveform of Ch1'''


        self.write("DATA:SOURCE CH1")#choose the source of data
        self.write("DATa:ENCdg ASCII") #choose the encoding
        self.write("DATa:WIDth 1") # 2 bytes per point
        self.write("ACQ:MOD SAMPLE") # sample, not averaged picture
        self.write("CURVE?") # qurey it is
        curve = self.read()
        print("tune picture captured\n")
        self.curve = curve
        return curve

    def saveTunePictureToFile(self,filename:str): # saves the tunepicture to a csv file

        curve = self.curve.split(',')
        self.write('WFMPre:XINcr?')
        xint = self.read() # interval on x axis between the points.
        # now lets save this in the file.
        fout = open('%s.csv' % filename, 'w')

        i = 0
        for symb in curve:
            if i == 0:
                fout.write('datetime,00.00.0000,00:00:00.000,%.12f, %.5f\n' % (float(xint) * i, float(symb)))
                continue

            fout.write(',,,%.12f, %.5f\n' % (float(xint) * i, float(symb)))
            i = i + 1
        fout.close()
        print('tune picture saved as %s' % fout.name)
