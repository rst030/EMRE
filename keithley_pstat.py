'''Communication to the Keithley 2450 source-measure unit.
written by Ilia Kulikov on 27/10/20
ilia.kulikov@fu-berlin.de'''

import pyvisa as visa

class pstat (object):
    model = '2450'                    # default model is 2450 that is the pstat at Lyra
    address = 'GPIB0::18::INSTR'      # and this is its GPIB address
    usb_address = 'USB0::0x05E6::0x2450::04431893::INSTR' # this is its usb_address
    device = visa.Resource            # pyvisa device that is populated with the constructor
    rm = 0                            # visa resource manager
    fake = False                      # use simulated outputs. Used for testing outside the lab.

    def __init__(self, rm: visa.ResourceManager, model: str): # when create a lia you'd better have a resource manager already working
        '''create an instance of the pstat object''' # создать объект потенциостата.
        self.rm = rm
        self.connect(model)
        self.write('*RST')  # ресетнем ка мы его на всякий случай
        self.write('*IDN?') # и спросим, как его зовут
        self.play_tune()
        self.write(':DISPlay:SCReen SOURce')
        self.write(':DISP:CURR:DIG 5') # 5 digits to show on current display
        self.write(':DISPlay:LIGHt:STATe ON100') # full brightness
        print('Potentiostat: '+self.read())


    def write(self, command):
        '''write data to BH-15, many lines can be accepted as an argument. Useful for pre-setting'''
        if not self.fake:
            try:
                self.device.write(command)
            except:
                print('write operation to Pstat failed')
        else:
            print('Pstat: No device. Writing %s to fake Pstat'%command)

    def read(self):
        if not self.fake:
            return self.device.read()
        else:
            return 42


    def connect(self, model):
        if '2450' in model:
            self.address = 'GPIB0::18::INSTR'  # pad 8
            try:
                self.device = self.rm.open_resource(self.address)
                print('got GPIB instrument for Potentiostat: %s'%self.device)
            except:
                try:
                    self.device = self.rm.open_resource(self.usb_address)
                    print('got USB instrument for Potentiostat: %s' % self.device)
                except:
                    print('failed to get Pstat device. Using fake device')
                    self.fake = True
                    self.device = 0
        else:
            print('no support for %s'% model)


    def beep_tone(self,frequency_in_hz, duration_in_seconds): # fun stuff
        self.write(':SYSTem:BEEPer %.5f, %.5f'%(frequency_in_hz,duration_in_seconds))


    def play_tune(self):
        for offtune in range(10):
            for _ in range(1):
                # happy C goes wild:
                self.beep_tone(523.251+ 25*offtune, 0.01)
                self.beep_tone(783.991- 15*offtune, 0.01)
                self.beep_tone(659.255+ 25*offtune, 0.01)


    def set_voltage(self,voltage_in_volts):
        # ставим напряждение в вольтах на выход пстата и маряем ток. На морде показываем ток. Сам показывается он.
        self.write(':SENS:FUNC \'CURR\'')
        self.write(':SENS:CURR:RANG:AUTO ON')
        self.write('SENS:CURR:UNIT OHM') #change to amps?
        self.write('SENS:CURR:OCOM ON')
        self.write('SOUR:FUNC VOLT')
        self.write('SOUR:VOLT %.5f' %voltage_in_volts) # here we set the voltage
        self.write('SOUR:VOLT:ILIM 0.1') # limit the current. Idk how much. 100 mA looks safe to me.
        self.write('COUNT 5') # looks like this is the number of points to measure
        #self.write('OUTP ON') # here we turn output on
        #self.write('OUTP OFF') # this we dont need now


    def output_on(self): # self explanatory
        self.write('OUTP ON')  # here we turn output on
        self.write('TRAC:TRIG \“defbuffer1\”') # this is for measurement trace. So far not in use.
        self.write('TRAC:DATA? 1, 5, \“defbuffer1\”, SOUR, READ') # not sure if we need it


    def output_off(self): # self explanatory
        self.write('OUTP OFF')  # here we turn output off


