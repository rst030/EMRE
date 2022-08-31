'''Communication to the Agilent 53181a frequency counter
written by Ilia Kulikov on 11/11/2020
ilia.kulikov@fu-berlin.de'''

import pyvisa as visa

class agilent_frequency_counter (object):
    type = 'frequency counter'
    model = '53181a'                   # default model is agilent that is the freq cntr at Lyra
    address = 'GPIB0::3::INSTR'      # and this is its GPIB address
    device = visa.Resource                        # pyvisa device that is populated with the constructor
    rm = 0                            # visa resource manager
    fake = False                      # use simulated outputs. Used for testing outside the lab.

    def __init__(self, rm: visa.ResourceManager, model: str): # when create a lia you'd better have a resource manager already working
        '''create an instance of the agilent frequency counter object'''
        self.rm = rm
        self.connect(model)

    def connect(self, model):
        if '53181' in model:
            try:
                self.device = self.rm.get_instrument('GPIB0::3::INSTR') #todo: learn about the agilent's gpib address and hook it up
                self.print('connecting to Agilent Frequency counter...')
                self.write('*RST') #connect and reset the counter
                self.print('connection to the frequency counter OK:\n' + self.device.query('*IDN?')) # if ok return counter's id
            except:
                self.agilentstatus = 'dis'
                self.fake = True
                self.print('ERROR: failed to connect to the Agilent frequency counter! Using a fake device. Something is wrong or EMRE is not on lyra.')

    def write(self,command):
        if not self.fake:
            self.device.write(command)
        else:
            self.print('talking to a fake Agilent')

    def read(self):
        if not self.fake:
            return(self.device.read())
        else:
            return('fake talking')

    def get_MW_frequency(self):
        #sleep(5)
        self.write('*CLS') #clearing the errors
        self.write('*SRE 0')  # service request enable register clear
        self.write('*ESE 0')  # event status enable register clear
        self.write(':STAT:PRES')  # prepare for operations and questionable sreuctures
        self.write(":FUNC 'FREQ 2'")  # measuring frequency on CH2
        self.write(":FREQ:ARM:STAR:SOUR IMM") #i took that from the agilent's manual. Not completely sure what it does
        self.write(":FREQ:ARM:STOP:SOUR TIM")
        self.write(":FREQ:ARM:STOP:TIM .100") #0.1 s gate time
        self.write('READ:FREQ?')  # finally reading the frequency
        frequency = float(self.read())

        print('MWFREQ MEASURED %.3e'%frequency)

        return frequency #unless communication established, return this value. Temporary.
        
        
    def print(self,s:str):
        print('- Agilent 53181a >> : %s'%s)    
    