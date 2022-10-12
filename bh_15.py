'''Communication to the Bruker bh-15 field controller
written by Ilia Kulikov on 26/10/20
ilia.kulikov@fu-berlin.de'''

# hardware constants. Values are in Gauss

EOS = '\r'
BH15_FC_MIN_FIELD      = -50.0
BH15_FC_MAX_FIELD      = 23000.0
BH15_FC_MAX_SWEEP_WIDTH= 16000.0
BH15_FC_MIN_FIELD_STEP = 1e-3
MIN_SWA        =    0
CENTER_SWA     =    2048
MAX_SWA        =    4095

import pyvisa as visa
from time import sleep
import numpy as np

class bh_15 (object):
    type = 'field controller'
    model = 'BH-15'                   # default model is BH-15 that is the field controller at Lyra
    address = 'GPIB0::8::INSTR'       # and this is its GPIB address
    device = visa.Resource                        # pyvisa device that is populated with the constructor
    rm = 0                            # visa resource manager
    fake = False                      # use simulated outputs. Used for testing outside the lab.
    header = 'BH-15 Field Controller: ' # header, used for the prompt output.

    '''magnetic parameters'''
    CF = 464 # center field
    SW = 100 # sweep width
    SWA = CENTER_SWA # sweep address - in the center of the field
    bvalues = np.linspace(CF-SW/2,CF+SW/2,SWA)
    '''___________________'''

    def __init__(self, rm: visa.ResourceManager, model: str): # when create a lia you'd better have a resource manager already working
        '''create an instance of the BH-15 field controller object'''
        self.rm = rm
        self.connect(model)

    def connect(self, model):
        if 'BH-15' in model:
            self.address = 'GPIB0::8::INSTR'  # pad 8
            try:
                self.device = self.rm.open_resource(self.address, write_termination='\r')
                self.print('got instrument: %s'%self.device)

                # Switch off service requests.
                self.curse_BH15('SR0')
                self.curse_BH15('MO0') # itnl gen, set CF [center field], SW [sweep width] and SWA [sweep adress < 2048]
                # Set IM0 sweep mode (we don't use it, just to make sure we don't trigger a sweep start inadvertently).
                self.curse_BH15('IM0')
                # The device seems to need a bit of time after being switched to remote mode
                sleep(1)

                self.preset_field_scan(self.bvalues)
                self.print('BH-15: CF SW configured, SWA set to 0')

            except:
                self.print('failed to get a BH-15 device. Using fake device')
                self.fake = True
                self.device = 0



    def preset_field_scan(self,bvalues:np.linspace): # sets the width and the center field. 2048 points!
        self.bvalues = np.linspace(bvalues[0],bvalues[-1],MAX_SWA) # this is in its rusty head now
        self.SW = max(bvalues) - min(bvalues)  # setting sweep width of BH15
        self.CF = (max(bvalues) + min(bvalues)) / 2  # do it in a convenient way, man noone likes to code here
        self.SWA = 0
        # set CF as center field
        # set SW as sweep width
        self.set_sw(sweepWidthInGauss_ = 0) # set the width to 0 for the next line

        self.set_swa(swa_=CENTER_SWA)  # go to the center of that 0 G - field range
        self.set_cf(field_in_gauss_ = self.CF) # set the center field, here the machine starts to move.
        self.set_sw(sweepWidthInGauss_ = self.SW) # set the width of the scan
        self.set_swa(swa_=self.SWA) # go to the left most field

        self.check_set_field(SetField=self.bvalues[self.SWA]) # check if field is really there

        return self.get_field()

    def check_set_field(self,SetField):
        # if the set field is not

        attemptsCtr = 1000 # how much time can we wait until the rusty box sets the field. Huge magnet! Huge!

        while (self.get_field() - SetField) >  self.SW/MAX_SWA: # while not on field:
            print('BH-15: crawling on the field (doing its best)')
            sleep(0.2)
            attemptsCtr -=1
            if attemptsCtr == 0:
                print('BH-15 crawling on the field for too long! Only at %.3f G by now'%self.get_field())
                return -1
        return(self.get_field() - SetField)

    def get_field(self):
        B0_measured_str = self.talk_to_BH15('FC')       # measure field
        B0_measured = float(B0_measured_str[3:13])      # convert response to float
        return B0_measured

    def set_field(self, magnetic_field_in_gauss: float):
        # take magnetic_field_in_gauss, get closest SWA
        step_in_B = self.SW/MAX_SWA # step that BH15 has chosen

        closest_swa = 0 # to be safe

        for swa in range(MAX_SWA):
            if abs(self.bvalues[swa]-magnetic_field_in_gauss) < step_in_B: # if close to desired field
                closest_swa = swa
                break

        self.set_swa(closest_swa) # here the magnet jumps on the field

        return self.get_field()

    def write(self, command):
        '''write data to BH-15, many lines can be accepted as an argument. Useful for pre-setting'''
        if not self.fake:
            try:
                self.device.write(command)
            except:
                self.print('write failed: %s'%command)
        else:
            self.print('No device. Writing to fake: %s'%command)

    def read(self):
        if not self.fake:
            return self.device.read()
        else:
            self.print('Fake device! Reading dummy values!')
            return 666

    def print(self, s:str): # adds a header to string and prints it to prompt
        print(self.header+s)

    def device_clear(self):
        mnemonic = "SDC"
        command = mnemonic
        self.write(command)

    def get_led_status(self):
        '''get a sting with LED statuses on the front panel of BH-15. Identify states.'''
        try:
            self.print('quering LED status')
            self.write('LE')
            response = self.read()
            self.print(response)
            if ('1' in str(response)):
                self.print('overload')
            if ('2' in str(response)):
                self.print('thermostat')
            if ('3' in str(response)):
                self.print('ext. sweep')
            if ('4' in str(response)):
                self.print('remote')

        except:
            self.print('LE query failed')

        return str(response)

    def go_remote(self):
        mnemonic = "CO"
        command = mnemonic
        self.print('going remote')
        self.write(command)

    def set_cf(self,field_in_gauss_):
        '''set central field, same as pressing CF and typing a number for center field in G'''
        field = '%.4f'%field_in_gauss_
        mnemonic = "CF"
        command = mnemonic + field
        self.write(command)

    # for a field sweep, set up CF, SW and SWA
    # for that go to 2 MODE, set CF, SW and SWA
    # -50G <= CF <= 23000 G
    # 0G <= SW <= 16 kG
    # 0 <= SWA <= 4095

    def set_sw(self,sweepWidthInGauss_):
        # check if width is within controller's capabilities
        if (sweepWidthInGauss_ > BH15_FC_MAX_SWEEP_WIDTH):
            print('BH 15 field controller: too high sweep width!')
            return

        SW = '%.4f' % sweepWidthInGauss_
        mnemonic = "SW"
        command = mnemonic + SW
        self.write(command)

    def set_swa(self,swa_: int):
        if not (swa_ in range(MIN_SWA,MAX_SWA)):
            print('BH15 field controller: sweep address not in range!')
            return

        SWA = '%.4f' % swa_
        mnemonic = "SS"
        command = mnemonic + SWA
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
        #print('BH-15 change mode %s' % command)
        self.write(command)

    def curse_BH15(self,command_):
        '''send command and dont listen to the box'''
        #print('BH-15 curse with %s'%command_)
        self.write(command_)

    def talk_to_BH15(self, command_): #this returns a value (string or whatever)
        if (self.fake and command_ == 'FC'):
            return('xxx1000.00')
        #print('BH-15 talking to with %s' % command_)
        self.write(command_)
        response = self.read()
        #print('BH-15 replies with %s' % response)
        return response

    def get_measured_field(self):
        query = "FV"
        #self.field_controller.read_termination = '\0'
        self.write(query)
        return self.read()

    def get_interlock_lines(self):
        query = "IL"
        self.write(query)
        #print(self.read())

    def unlisten(self):
        query = "UNL"
        self.write(query)

    def untalk(self):
        cmnd= "UNT"
        self.write(cmnd)

    def go_local(self):
        #print('BH-15 goes local')
        query = "GTL"
        self.write(query)