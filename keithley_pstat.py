'''Communication to the Keithley 2450 source-measure unit.
written by Ilia Kulikov on 27/10/20
ilia.kulikov@fu-berlin.de'''

import visa

class bh_15 (object):
    model = '2450'                   # default model is 2450 that is the pstat at Lyra
    address = 'GPIB0::18::INSTR'       # and this is its GPIB address
    device = 0                        # pyvisa device that is populated with the constructor
    rm = 0                            # visa resource manager
    fake = False                      # use simulated outputs. Used for testing outside the lab.

    def __init__(self, rm: visa.ResourceManager, model: str): # when create a lia you'd better have a resource manager already working
        '''create an instance of the BH-15 field controller object'''
        self.rm = rm
        self.connect(model)

    def write(self, lines):
        '''write data to BH-15, many lines can be accepted as an argument. Useful for pre-setting'''
        if not self.fake:
            try:
                for line in lines:
                    self.device.write(line)
            except:
                print('write operation to Pstat failed')
        else:
            print('Pstat: No device. Writing %s to fake Pstat'%lines)

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
                print('got instrument for Potentiostat: %s'%self.device)
            except:
                print('failed to get Pstat device. Using fake device')
                self.fake = True
                self.device = 0
        else:
            print('no support for %s'% model)


    def beep_tone(self,frequency_in_hz, duration_in_seconds): # fun stuff
        self.write(':SYSTem:BEEPer %.5f, %.5f'%(frequency_in_hz,duration_in_seconds))







    def device_clear(self):
        mnemonic = "SDC"
        command = mnemonic
        self.write(command)

    def go_remote(self):
        mnemonic = "CO"
        command = mnemonic
        print('BH-15 going remote')
        self.write(command)

    def reset(self):
        mnemonic = "DCL"
        command = mnemonic
        self.write(command)

    def curse_BH15(self,command_):
        '''send command and dont listen to the box'''
        print('BH-15 curse with %s'%command_)
        self.write(command_)

    def talk_to_BH15(self, command_): #this returns a value (string or whatever)
        print('BH-15 talking to with %s' % command_)
        self.write(command_)
        response = self.read()
        print('BH-15 replies with %s' % response)
        return response




        #--------------------------------------------------------------------------------------------
        '''---------------------------------------- KEITHLEY COMMANDS -----------------------------------------------'''

        def connect_to_sourcemeter(self):
            try:
                self.sourcemeter = self.rm.get_instrument(
                    'TCPIP0::192.168.1.20::inst0::INSTR')  # Address might change, then change it here also
                self.sourcemeter.write("*IDN?")
                response = self.sourcemeter.read()
                self.sourcemeter.write("smua.reset()")  # when connected, all reset
                self.sourcemeterstatus = 'con'
                return 'OK:\n' + response + ',sourcemeter reset.'  # if ok return smu's idn and reset it
            except:
                self.sourcemeterstatus = 'dis'
                return 'failed to connect to Keithley!\n'

        def reset_sourcemeter(self):  # a customized reset method, suitable for organics
            try:
                self.sourcemeter.write("smua.reset()")  # reset the source-meter
                self.sourcemeter.write("smua.source.limiti = 1000e-3")  # limit the current
                self.sourcemeter.write("smua.source.func = smua.OUTPUT_DCVOLTS")  # output volts
                self.sourcemeter.write("smua.source.rangev = 20")  # output range 20 V
                self.sourcemeter.write("smua.source.levelv = 0")  # output value 0 volts
            except:
                return ('could not reset sourcemeter. check connection')

        def set_voltage_sourcemeter(self, amplitude_in_volts):
            self.sourcemeter.write("smua.source.levelv = " + str(
                amplitude_in_volts))  # output value for voltage is set, keithley understands volts
            self.sourcemeter.write("smua.source.output =smua.OUTPUT_ON")  # output is on!
            return 'set voltage ' + str(amplitude_in_volts) + 'V'

        def wait_ms(self, time_in_ms):
            sleep(float(time_in_ms / 1000))  # sleep method eats seconds
            return 'waited' + str(time_in_ms) + ' ms'

        def get_current_sourcemeter(self, number_of_averages, delay_in_ms):
            tempCurrents = []
            for counter in range(number_of_averages):
                self.wait_ms(delay_in_ms)
                self.sourcemeter.write("currenta, voltagea = smua.measure.iv()")  # writing command to read current
                tempCurrents.append(float(self.sourcemeter.ask("print(currenta)")))  # creating an array of currents
            current_value = float(sum(tempCurrents)) / len(tempCurrents)  # average value of temporary currents
            return current_value

        def shutdown_output_sourcemeter(self):
            self.sourcemeter.write("smua.source.output=smua.OUTPUT_OFF")
            return 0
