'''Communication to the Bruker bh-15 field controller
written by Ilia Kulikov on 26/10/20
ilia.kulikov@fu-berlin.de'''

import visa

class bh_15 (object):
    model = 'BH-15'                   # default model is BH-15 that is the field controller at Lyra
    address = 'GPIB0::8::INSTR'       # and this is its GPIB address
    device = visa.Resource                        # pyvisa device that is populated with the constructor
    rm = 0                            # visa resource manager
    fake = False                      # use simulated outputs. Used for testing outside the lab.

    def __init__(self, rm: visa.ResourceManager, model: str): # when create a lia you'd better have a resource manager already working
        '''create an instance of the BH-15 field controller object'''
        self.rm = rm
        self.connect(model)

    def set_field(self, magnetic_field_in_gauss: float):
        'sets magnetic field, returns field measured by the field controller'

        self.curse_BH15('MO0')                          # move to basic field control mode that is mode 0'''
        self.set_center_field(magnetic_field_in_gauss)  # set the field
        self.curse_BH15('MO5')                          # move to field measure mode that is mode 5
        ledstatus = self.talk_to_BH15('LE')             # '''get the led status''' use it later
        B0_measured_str = self.talk_to_BH15('FC')       # measure field
        B0_measured = float(B0_measured_str[3:11])      # convert response to float
        return B0_measured
        '''God save the magnet.'''


    def write(self, command):
        '''write data to BH-15, many lines can be accepted as an argument. Useful for pre-setting'''
        if not self.fake:
            try:
                self.device.write(command)
            except:
                print('write operation to BH-15 failed')
        else:
            print('BH-15: No device. Writing %s to fake BH-15'%command)

    def read(self):
        if not self.fake:
            return self.device.read()
        else:
            return 4000

    def connect(self, model):
        if 'BH-15' in model:
            self.address = 'GPIB0::8::INSTR'  # pad 8
            try:
                self.device = self.rm.open_resource(self.address, write_termination='\r')
                print('got instrument for BH-15: %s'%self.device)
            except:
                print('failed to get a BH-15 device. Using fake device')
                self.fake = True
                self.device = 0

    def device_clear(self):
        mnemonic = "SDC"
        command = mnemonic
        self.write(command)

    def get_led_status(self):
        '''get a sting with LED statuses on the front panel of BH-15. Identify states.'''
        try:
            print('BH-15 quering LED status')
            self.write('LE')
            response = self.read()
            print('BH-15: %s'%response)
            if ('1' in str(response)):
                print('overload')
            if ('2' in str(response)):
                print('thermostat')
            if ('3' in str(response)):
                print('ext. sweep')
            if ('4' in str(response)):
                print('remote')

        except:
            print('BH-15 LE query failed')

    def go_remote(self):
        mnemonic = "CO"
        command = mnemonic
        print('BH-15 going remote')
        self.write(command)

    def set_center_field(self,field_):
        '''set central field, same as pressing CF and typing a number for center field in G'''
        field = '%.4f'%field_
        mnemonic = "CF"
        command = mnemonic + field
        print('BH-15 setting field: %s'%command)
        self.write(command)

    def reset(self):
        mnemonic = "DCL"
        command = mnemonic
        self.write(command)

    def set_operating_mod(self, mode_):
        '''0: basic field control
           1: with repetitive auto sweep
           3: with external address advance
           4: reserved
           5: basic measure mode
           6: hi-res measure mode'''

        mode = str(mode_)
        mnemonic = "MO"
        command = mnemonic + mode
        print('BH-15 change mode %s' % command)
        self.write(command)

    def curse_BH15(self,command_):
        '''send command and dont listen to the box'''
        print('BH-15 curse with %s'%command_)
        self.write(command_)

    def talk_to_BH15(self, command_): #this returns a value (string or whatever)
        if (self.fake and command_ == 'FC'):
            return('xxx1000.00')
        print('BH-15 talking to with %s' % command_)
        self.write(command_)
        response = self.read()
        print('BH-15 replies with %s' % response)
        return response

    def get_measured_field(self):
        query = "FV"
        #self.field_controller.read_termination = '\0'
        self.write(query)
        return self.read()

    def get_interlock_lines(self):
        query = "IL"
        self.write(query)
        print(self.read())

    def unlisten(self):
        query = "UNL"
        self.write(query)

    def untalk(self):
        cmnd= "UNT"
        self.write(cmnd)

    def go_local(self):
        print('BH-15 goes local')
        query = "GTL"
        self.write(query)