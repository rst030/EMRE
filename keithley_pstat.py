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
        response = self.read()
        self.play_tune()
        self.write(':DISPlay:SCReen SOURce')
        self.write(':SENSe:CURRent:RSENse ON')
        self.write('SENS:FUNC \'CURR\'')
        self.write('SENS:CURR:RANG:AUTO ON')
        self.write('SENS:CURR:UNIT AMP') # double check it
        self.write('SENS:CURR:OCOM ON')
        self.write('SOUR:FUNC VOLT')
        self.write('SOUR:VOLT 0')
        self.write('SOUR:VOLT:ILIM 0.01')
        self.write('COUNT 125') # 250 points of current to measuer



        #self.write(':DISP:CURR:DIG 5') # 5 digits to show on current display
        #self.write(':DISPlay:LIGHt:STATe ON100') # full brightness
        #self.write(':SENSe:CURRent:RSENse ON') #for 4 wire measurements.
        #self.write(':DISPlay:SCReen HOME_LARGe_reading') # show large readings on the display
        #self.write('CURR:NPLC 0.5') # how quickly meas current 0.5/60 s

        print('Potentiostat: '+response)


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

    def play_short_beep(self):
        self.beep_tone(713,0.1)

    def play_tune(self):
        for offtune in range(10):
            for _ in range(1):
                # happy C goes wild:
                self.beep_tone(523.251+ 25*offtune, 0.01)
                self.beep_tone(783.991- 15*offtune, 0.01)
                self.beep_tone(659.255+ 25*offtune, 0.01)


    def set_voltage(self,voltage_in_volts):  # sets voltage and presets the trigger (1 second transient for now)
        # ставим напряждение в вольтах на выход пстата и маряем ток. На морде показываем ток. Сам показывается он.
        # nope, we just set the measurement and trigger it maually.

        self.write('SOUR:VOLT %.3f'%voltage_in_volts)



        # Set the transient meas. duration loop for duration_in_seconds s, no delay (167 ns), saving to buf100
        # :TRIGger:LOAD "DurationLoop"
        # This command loads a predefined trigger model configuration that makes continuous measurements for a
        # specified amount of time.
        # :TRIGger:LOAD "DurationLoop", <duration>, <delay>, "<readingBuffer>"
        # 167 ns minimal delay between measurement points



        # after this we just need to turn on the output and to fire the trigger right after that

    def configure_transient_trigger(self,duration_in_seconds, delay_in_seconds):  # duration_in_seconds s measurements into buffer

        self.write(':SENSe:CURRent:NPLCycles 10') # change to 0.5 to measure faster. Youll get oscillations! Affects measurement speed.

        print('setting up trigger model to DurationLoop: %.2f s'%duration_in_seconds)
        self.write('TRAC:MAKE \"CYKA_BLYAT\", 65536')  # create buffer with 65536 points
        self.write('TRIG:LOAD \"DurationLoop\", %.2f, %.6f, \"CYKA_BLYAT\"' % (duration_in_seconds,delay_in_seconds))  # load trigger model 0.5 us TEMPORARY!


    def delete_trace(self):
        self.write(':TRACe:DELete \"CYKA_BLYAT\"')


    def query_current_transient(self):# returns the current readings in a string!
        print('attempting to read 1 values from CYKA_BLYAT butter ++++ P')
        self.write('TRAC:DATA? 1, 512, \"CYKA_BLYAT\", SOUR, READ, REL') # Read the 5 data points, reading, programmed source, and relative time for each point.


        transients = self.read()

        return transients

    def output_on(self): # self explanatory
        self.play_short_beep()  # short beep when pot on
        self.write('OUTP ON')  # here we turn output on
    #    self.trigger_current_transient()  # and immediately after, start measuring it. For 1 second as for now



        # #self.write('TRAC:TRIG \“defbuffer1\”') # this is for measurement trace. So far not in use.
        #self.write('TRAC:DATA? 1, 5, \“defbuffer1\”, SOUR, READ') # not sure if we need it

    def trigger_current_transient(self): # starts current transient measurement.
        print('__________ ptriggering the measurement of a current transient NOW! ++++ P')
        self.write('INIT') # initiate the readings of current WOUD THIS WORK ???
        self.write('*WAI') # postpone execution of successive commands while this is executed.
        self.write('OUTP ON')  # keep output on

        # This sets the trigger on time loop
        # and store the readings in the buf100 reading buffer.

        #self.write('TRAC:TRIG \"defbuffer1\"') # this puts readings on its face.

    def output_off(self): # self explanatory
        from time import sleep
        self.write('OUTP OFF')  # here we turn output off
        self.play_short_beep()  # short beep when pot on
        sleep(0.25)
        self.play_short_beep()  # twice

