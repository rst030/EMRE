'''communication to the lock-in amplifier.
Written by Ilia Kulikov on 26/10/20
ilia.kulikov@fu-berlin.de'''

import pyvisa as visa

class lockin (object):
    model = 810                   # default model is 810 that is the lock-in at Lyra
    address = 'GPIB0::9::INSTR'   # and this is its GPIB address
    device = 0                    # pyvisa device that is populated with the constructor
    rm = 0                        # visa resource manager
    fake = False                  # use simulated outputs. Used for testing outside the lab.

    def __init__(self, rm: visa.ResourceManager, model: str): # when create a lia you'd better have a resource manager already working
        '''create an instance of the lock-in amplifier object'''
        self.rm = rm
        self.connect(model)

    def write(self, command):
        '''write data to lock-in, many lines can be accepted as an argument. Useful for pre-setting'''
        if not self.fake:
            try:
                self.device.write(command)
            except:
                print('write operation to lock-in failed')
        else:
            print('Lock-in: No device. Writing %s to fake lock-in'%command)  # when device is fake, write to console

    def read(self):
        if not self.fake:
            return(self.device.read())
        else:
            return(3.1415926353897932384626433832795028841971693993751058209749445978230164)


    def connect(self,model):
        '''connect to lock-in model model. Figure out its address by model number and then connect'''
        if (model == 860):
            self.address = 'TCPIP0::192.168.1.51::inst0::INSTR'
            print('Hall')
        if (model == 810):
            self.address = 'GPIB0::9::INSTR' # GPIB pad 9, the 810 on Lyra
            print('SR 810 on lyra.')
        if (model == 830):
            self.address = ''
            print('isaak. GIVE ME THE GPIB ADDRESS!')
        # by model we got the address
        try:
            self.device = self.rm.open_resource(self.address)
            self.write("*IDN?") # send an IDN query
            self.status = 'con'
            print('connected to lock-in: %s'%self.device.read()) # careful with fakes here

        except:
            self.status = 'dis'
            self.fake = True
            self.device = 0
            print('cant connect to lock-in. Using fake device.')

    def set_voltage(self, voltage_in_volts: float):
        '''sets amplitude in V for sin out'''
#        amplitudeForLockin = voltage_in_volts * 1000  # volts to millivolts conversion
        self.write('SLVL ' + str(voltage_in_volts) + 'V')

    def getR(self):
        # OUTP? i Query the value of X (1), Y (2), R (3) or θ (4). Returns ASCII floating point value.
        self.write('OUTP? 3')  # request for R channel
        voltage = float(self.read())  # read the lockin response in volts
        return voltage

    def getX(self):
        # OUTP? i Query the value of X (1), Y (2), R (3) or θ (4). Returns ASCII floating point value.
        self.write('OUTP? 1')  # request for R channel
        voltage = float(self.read())  # read the lockin response in volts
        return voltage

    def getY(self):
        # self.lockin.write('GAUT DAT3')  # autoscale the R channel
        self.write('OUTP? 2')  # request for R channel
        voltage = float(self.read())  # read the lockin response in volts
        return voltage



    def get_voltage(self, channel: str):
        '''get voltage in channel channel'''
        parameter = 2  # default request is R channel data

        if channel == 'r':
            parameter = 2  # request for R channel
        if channel == 'x':
            parameter = 0  # request for X channel
        if channel == 'y':
            parameter = 1  # request for Y channel
        if channel == 't':
            parameter = 3  # request for THETA channel

        self.write('OUTP? %d' % parameter)  # request for data at #parameter channel
        voltage = float(self.read())  # read the lockin response in amps
        return voltage

    def set_frequency(self, frequency_in_hz: float):
        '''set the internal oscillator frequency in Hz'''
        self.write('FREQ %f' % frequency_in_hz)  # set frequency

    def set_phase(self, phase: float):
        '''careful with commas in the float type. You might want to use int instead.'''
        self.write('PHAS %d DEG' % phase)

    def get_phase(self):
        '''get phase of detection in deg'''
        self.write('PHAS?')
        return float(self.read())

    def get_time_constant(self, getnext):
        '''get time constant of the lock-in amplifier as a code. Decode to seconds.'''
        self.write('OFLT?');  # what is your time constant in codes?
        tc = int(self.read())  # read the response

        # decode tc from code to seconds
        def times(tm):
            return {
                0: 0.000001,  # 1 us
                1: 0.000003,
                2: 0.00001,
                3: 0.00003,
                4: 0.0001,
                5: 0.0003,
                6: 0.001,
                7: 0.003,
                8: 0.01,
                9: 0.03,
                10: 0.1,
                11: 0.3,
                12: 1,
                13: 3,
                14: 10,
                15: 30,
                16: 100,  # 100 s
            }.get(tm, -1)  # default value to return is -1 that means smth went wrong and threw an error

        if getnext:  # if next TC is required.
            return times(
                tc + 1)  # returns TC+1 in seconds, i.e. next largest time constant. Note the actual TC is not changed here
        else:
            return times(tc)  # by default return current TC

    def set_time_constant(self, code:int):
        self.write('OFLT %d' % code);  # set time constant with code CODE

    def set_sensitivity(self, code: int):
        '''I could have done it human-friendly, but sensitivity setting is not often in use. Plus not all values are alowed'''
        self.write('SENS %d' % code) # sens, not scal!

    def autophase(self):  # set autophase, wait 3TC until the signal is relaxed.
        '''set autophase, wait 3TC until signal is relaxed'''
        self.write('APHS');  # first set autophase
        tc = self.get_time_constant(getnext=True)  # then get the time constant which is approx 3 times larger
        from time import sleep
        sleep(tc) # wait for that time
        print('Phase corrected, waited 3TC = %d s to stabilize' % tc)

    def checkLocked(self):  # useless junk but commands here are useful

        self.write('FREQINT?')
        status_string = 'INT: %.3f Hz' % float(self.read())
        self.write('FREQEXT?')
        status_string += '\nEXT: %.3f Hz' % float(self.read())
        self.write('FREQDET?')
        status_string += '\nDET: %.3f Hz' % float(self.read())
        return status_string

    def get_freqdet(self):  # gives the detection frequency
        self.write('FREQDET?')
        return float(self.read())
