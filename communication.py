'''
    This is the communicator class that unifies the communication between all our devices.
    Devices are fields of the communicator. Once device is connected, its methods can be applied.
    Looks like we need to inherit devices from the visa.resource_pyclass and use proper constructors.
    For that we will need a real programmer who knows what they are doing.
    A suggestion to separate this module into small modules to import them separately, but for now, we
    stick to this library-like file.
'''

import pyvisa as visa

from time import sleep #time-dependent business for IV curves and time-constants

import windfreak_synth

interval = 0.01 # an interval in seconds that is waited whenever a command is sent to the Osilla's X200 SMU.
# Can be made a little shorter, but Osilla is unpredictable often.

import lock_in  # lock in amplifier class.
import bh_15   # field controller class
import keithley_pstat  # potentiostat keithley model 2450 source meter
import agilent_53181a  # frequency counter class.
import Plotter
import emres_right_hand

class communicator(object):
    rm = 0 # no resource manager for beginning
    lockin = lock_in.lockin # lock in detector
    field_controller = bh_15.bh_15 # Bruker BH15 field controller
    keithley_pstat = keithley_pstat.pstat #
    frequency_counter = agilent_53181a.agilent_frequency_counter # Agilent/HP microwave frequency counter
    right_hand = emres_right_hand.emres_right_hand # software tool for moving and clicking the mouse
    windfreak = windfreak_synth.windfreak_synth # windfreak microwave synthesizer board

    devices_list = [] # to be popuylated in the constructor

    # for the beginning only two devices. then we may expand. Gaussmeter is a must, frequency counter is desirable too

    def __init__(self, backend, cvPlotter: Plotter.Plotter): #  BUGS!!!!! <---------- the fucking plotter, noone really needs it at this point.
        '''The constructor of the communicator class.'''
        # visa.log_to_screen() #here we initialize the communicator. But there is nothing really to initialize logging is temporary
        backend = '@py'# for PyVISA-py backend, '' for NIVISA backend
        self.rm = visa.ResourceManager('%s'%backend) # forget about Windows for a while.
        # populating devices:
        self.lockin = lock_in.lockin(rm = self.rm, model = '810') # creating lia, that easy.
        self.devices_list.append(self.lockin)
        self.field_controller = bh_15.bh_15(rm = self.rm, model = 'BH-15') # creating field controller. that easy.
        self.devices_list.append(self.field_controller)
        self.keithley_pstat = keithley_pstat.pstat(rm = self.rm, model = '2450', plotter=cvPlotter) # creating pstat. That easy BUGS!!!!! <---------- the fucking plotter, noone really needs it at this point.
        self.devices_list.append(self.keithley_pstat)
        self.frequency_counter = agilent_53181a.agilent_frequency_counter(rm=self.rm, model = '53181')
        self.devices_list.append(self.frequency_counter)
        self.right_hand = emres_right_hand.emres_right_hand()
        self.devices_list.append(self.right_hand)
        self.windfreak = windfreak_synth.windfreak_synth()
        self.devices_list.append(self.windfreak)

    def list_devices(self):
        '''list all devices, no matter available or not'''
        list_of_resources = (self.rm.list_resources())
        print(self.devices_list)
        # for device in self.devices_list:
        #     list_of_connected_devices.append(device)
        #     device.print(device.address,'>')
        return self.devices_list





































class old_communicator (object):
    '''Our lab is a village with neighbors. There is a very communicative guy that knows all names and all addresses, the communicator.
    This person knows good manners and has found a common language to all his neighbors.
    When new neighbors move in, the person writes down their names and numbers in a list.
    So far there are not so many neighbors so the communicator can remember all names
    It is not meant to be like this forever though.
    We will observe with excitement as our small village expands to the gulf of Isaak and one day to the everfrost of XQ'''
    rm = 0 # resource manager. '@py' for PyVISA-py backend. Sent as parameter to the constructor,

    #now we have just four devices but we plan on expanding this list

    lockin = 0               # SR860 LIA is a Visa.instrument     | TCPIP
    sourcemeter = 0          # Keithley 2611A SMU                 | TCPIP
    xtralien = 0             # Xtralien X200 SMU by Osilla        | Serial TODO: would be nice to have type declaration here. Emre?
    scope = 0                # Lyra's Tektronix scope             | USB  Using it to get the tune picture
    agilent = 0              # Lyra's Agilent Frequency Counter   | GPIB
    field_controller = 0     # B-H 15 Field controller by Bruker  | GPIB
    gaussmeter = 0           # ER 035 M NMR Gaussmeter by Bruker  | Serial
    keithley_potentiostat = 0# Keithley 2450 source-measure unit. | GPIB
    t_sensor = 0   # Oxford temperature controller.       | GPIB

    '''Here come some labels aka flags. 
    The following fields needed when we want to use a fancy GUI which indicates states of devices in real time.
    For example, if the lock-in is connected to the computer, a green light may go on on the gui.'''

    lockin_status =      'dis'  # also possible 'con' 'ext' 'int' and 'dua'. These vars are no serious, mainly for the GUI
    sourcemeter_status = 'dis'  # they can be fields of the corresponding objects but im not sure how to implement that
    xtralien_status =    'dis'  #  When we separate the modules, to make a field 'status' for each device. Its easier to track the statuses of the setup this way.
    scope_status =       'dis'
    agilent_status =     'dis'
    # field_controller_status = 'dis'


    def __init__(self, backend):
        '''The constructor of the communicator class.'''
        visa.log_to_screen() #here we initialize the communicator. But there is nothing really to initialize logging is temporary
        # backend = '@py' for PyVISA-py backend, '' for NIVISA backend
        self.rm = visa.ResourceManager('%s'%backend) # forget about Windows for a while.
        pass

    def list_resources(self):
        '''communicator can list connected resources but so far it is just the PyVisa code.
        Visa is bad at listing GPIB and USB devices as well as TCPIP devices (there are billions addresses to go through!)
        What we want here is to try accessing all known resources on all known protocols,
        More precisely, you have listed here some devices, say, 18 devices in total. The lock-ins, the Keithley and so on.
        Then you run this script on a new machine. Script tries to find all the 18 devices and to perform a hand-shake
        with each of them. '''
        listres = self.rm.list_resources() #this is lame!
        print(listres)
        return listres

    '''Next the script is divided into sets of commands, 
    because the programmer was not familiar with classes at that point.'''

    def handshake(self, address):
        '''shake hands with a device on address address. Address i8s a string, Send IDN. Print response.'''
        self.dummy = self.rm.get_instrument(address)
        try:
            self.dummy.write("*IDN?")
            response = self.dummy.read()
            print('%s : %s'%(address,response))
        except:
            print('handshake to %s failed'%str(address))


    '''----------------------------- BH15 Field Controller COMMANDS --------------------------------------------'''
    def connect_to_field_controller(self):
        addr_string = 'GPIB0::8::INSTR'  # pad 8
        self.field_controller = self.rm.get_instrument(addr_string, write_termination = '\r')
        print(self.field_controller)
        #getting led status of BH15:

    def field_controller_device_clear(self):
        mnemonic = "SDC"
        command = mnemonic
        print(self.field_controller.write(command))
    def field_controller_read_blank(self):
        self.field_controller.read()

    def field_controller_get_led_status(self):
        try:
            print(self.field_controller.write('LE'))
            response = self.field_controller.read()
            print(response)
            if ('1' in str(response)):
                print('overload')
            if ('2' in str(response)):
                print('thermostat')
            if ('3' in str(response)):
                print('ext. sweep')
            if ('4' in str(response)):
                print('remote')

        except:
            print('LE query to BH15 failed')

    def goremote(self):
        mnemonic = "CO"
        command = mnemonic
        print(self.field_controller.write(command))

    def field_controller_set_center_field(self,field_):
        field = str(field_)
        mnemonic = "CF"
        command = mnemonic + field
        print(command)
        print(self.field_controller.write(command))

    def reset_field_controller(self):
        mnemonic = "DCL"
        command = mnemonic
        print(self.field_controller.write(command))

    def set_operating_mode_of_field_controller(self,mode_):
        '''0: basic field control
           1: with repetitive auto sweep
           3: with external address advance
           4: reserved
           5: basic measure mode
           6: hi-res measure mode'''

        mode = str(mode_)
        mnemonic = "MO"
        command = mnemonic + mode
        print('sending %s to BH15'%command)
        print(self.field_controller.write(command))

    def curse_BH15(self,command_):
        print(self.field_controller.write(command_))

    def talk_to_BH15(self, command_): #this returns a value (string or whatever)
        print(self.field_controller.write(command_))
        response = (self.field_controller.read())
        print(response)
        return response

    def get_measured_field(self):
        query = "FV"
        #self.field_controller.read_termination = '\0'
        print(self.field_controller.query(query))

    def get_interlock_lines(self):
        query = "IL"
        self.field_controller.write(query)
        print(self.field_controller.read())

    def field_controller_unlisten(self):
        query = "UNL"
        print(self.field_controller.write(query))

    def field_controller_untalk(self):
        cmnd= "UNT"
        print(self.field_controller.write(cmnd))

    def gotolocal(self):
        query = "GTL"
        print(self.field_controller.write(query))

    '''----------------------------------------LOCK-IN COMMANDS-------------------------------------------------'''

    def connect_to_lockin(self, model): # constructor for the lock-in amplifier.
    # TODO:  take a pencil and a piece of paper. Go around the lab, Write down the devices. Implement here, we have 510, 810, 860 lockins.
    # We might need machine files at this point. But it is a different story.
        if (model == 860):
            addr_string = 'TCPIP0::192.168.1.51::inst0::INSTR'
            print('Hall')
        if (model == 810):
            addr_string = 'GPIB0::9::INSTR' #pad 9
            print('SR 810 on lyra. Connection OK.')
        if (model == 830):
            addr_string = ''
            print('isaak. GIVE ME THE GPIB ADDRESS!')


        try:
            self.lockin = self.rm.get_instrument(addr_string) # connecting via lan to the lockin.
            # Device's IP might change, if you cannot connect you might need to enter the IP here.
            self.lockin.write("*IDN?") # if connected this should return the lockin's id
            response = self.lockin.read()
            print(response)
            self.lockinstatus = 'con' #tracking of the status. Good for bulletproof scripts
            #would be cool to inherit the lockin from visa.instrument and add lockinstatus as a lockin's field, but im ok like this
            #self.moveLockinToTheHallmode() # a default state of the lock-in is the hall-effect measurement. It makes sense to change it to CW EPR mode
            return 'OK:\n'+response #if ok return lockin's id
        except:
            self.lockinstatus = 'dis'
            return'failed to connect to LOCK-IN!'

    def writeLockin(self, lines): # to make things easier we can call this to write many successive commands
        for line in lines:
            self.lockin.write(line)

    def setLockinVoltage(self, voltage_in_volts: float):
        '''sets amplitude in V for sin out'''
        amplitudeForLockin = voltage_in_volts * 1000  # volts to millivolts conversion
        self.lockin.write('SLVL ' + str(amplitudeForLockin) + ' MV')
        return 0

    def getLockinR(self):
        # self.lockin.write('GAUT DAT3')  # autoscale the R channel

        self.lockin.write('OUTP? 2')  # request for R channel
        voltage = float(self.lockin.read())  # read the lockin response in volts
        return voltage

    def get_lockin_voltage(self, channel: str):
        parameter = 2  # default request is R channel data

        if channel == 'r':
            parameter = 2
        if channel == 'x':
            parameter = 0  # request for X channel
        if channel == 'y':
            parameter = 1  # request for Y channel
        if channel == 't':
            parameter = 3  # request for THETA channel

        self.lockin.write('OUTP? %d' % parameter)  # request for data at #parameter channel
        current = float(self.lockin.read())  # read the lockin response in amps
        return current

    def setLockinFrequency(self, frequency_in_hz: float):  # set the internal oscillator frequency in Hz
        lkin = self.lockin
        lkin.write('FREQ %f' % frequency_in_hz)  # set frequency

    # return str(lkin.read()) #careful! might be buggy!

    def set_lockin_time_constant(self, CODE: int):
        lockin = self.lockin
        lockin.write('OFLT %d' % CODE);  # Go to new time constant with code CODE

    def set_lockin_phase(self, phase: float):
        '''careful with commas in the float type. You might want to use int instead.'''
        self.lockin.write('PHAS %d DEG' % phase)

    def get_lockin_phase(self):
        self.lockin.write('PHAS?')
        return float(self.lockin.read())

    def get_time_constant(self, getnext):
        lockin = self.lockin
        lockin.write('OFLT?');  # what is your time constant in codes?

        tc = int(lockin.read())  # read the response

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

        if getnext == 'next':  # if next TC is required.
            return times(
                tc + 1)  # returns TC+1 in seconds, i.e. next largest time constant. Note the actual TC is not changed here
        else:
            return times(tc)  # by default return current TC

    def set_lockin_sensitivity(self, code: int):
        '''I could have done it human-friendly, but sensitivity setting itself is alien.'''
        lockin = self.lockin
        lockin.write('SCAL %d' % code)

    def moveLockinToTheIVmode(self):  # a brave attempt to implement an AC IV measurement
        '''
            here we send commands to the lockin so that it goes to IV mode:
            Time constant: TC = 100 us
            Reference source: internal
            Internal frequency: 20KHz
            Input Range: 1V
        '''
        self.writeLockin([
            'OFLT 4',  # set TC to 100 us
            'FREQ 5 KHZ',  # set frequency to 5khz
            'RSRC 0',  # detection to the single mode
            'IRNG 1V',  # input range to 1v
            'REFM DIF',  # output to difference
        ])

    def moveLockinToCurrentMeasurementMode(self):  # this is used within the Hall mode when current is measured
        ''' current input, single detection mode, mind the range and time constant '''
        self.lockinstatus = 'int'

        lockin = self.lockin

        lockin.write('IRNG 1V')  # input range to 1v
        lockin.write('OFLT 4')  # set TC to 100 us
        lockin.write('RSRC 0')  # detection to the internal mode
        self.lockinstatus = 'int'
        lockin.write('REFM COM')  # output to common
        lockin.write('IVMD CURRENT')  # input to current


    def moveLockinToTheHallmode(self):  # this is needed just to check that all settings are fine. might be called with initialization of the lock-in.
        '''
        here we send commands to the lockin so that it goes to Hall mode:
        Time constant: TC = 1 s
        Reference source: dual
        Input Range: 1 V
        '''
        self.writeLockin([
            'OFLT 9',  # set TC to 300 ms?
            'ISRC A-B',  # input mode to difference
            'IVMD VOLT',  # input to voltage to avoid spikes, thanks Naitik and Dasha
            'IRNG 1V',  # input range to 1v
            'REFM COM',  # output to common
        ])
        sleep(1)  # let voltage drop to normal value with a short time constant first.
        self.writeLockin([
            'OFLT 14',  # set TC to 10 s but for the future, let user choose in Hall module. We really need fields for that all. I am doing it wrong.
            'RSRC 2',  # detection to the dual mode
        ])
        self.lockinstatus = 'dua'

    def autophase(self):  # set autophase, wait 3TC until the signal is relaxed.

        lockin = self.lockin
        lockin.write('APHS');  # first set autophase
        tc = self.get_time_constant(
            argument='next')  # then get the time constant which is approx 3 times larger than the current time constant
        self.wait_ms(tc * 1000)
        self.lockin.write('GAUT DAT3')  # rescale the R channel just to see it better on the LIA's face

        return 'Phase corrected, waited 3TC = %d s to stabilize' % tc

    def checkLocked(self):  # useless junk but commands here are useful

        lockin = self.lockin
        lockin.write('FREQINT?')
        status_string = 'INT: %.3f Hz' % float(lockin.read())
        lockin.write('FREQEXT?')
        status_string += '\nEXT: %.3f Hz' % float(lockin.read())
        lockin.write('FREQDET?')
        status_string += '\nDET: %.3f Hz' % float(lockin.read())
        return status_string

    def get_freqdet(self):  # gives the detection frequency
        self.lockin.write('FREQDET?')
        return float(self.lockin.read())

    '''--------------------------------------------Tektronix Scope Commands -------------------------------------'''

    def connect_to_scope(self):
        ''' constructor for the scope. TODO: need more rights to get access to USB.
        Need rights. Modify the 99-ni... file and restart udev. have a look here:
        https://stackoverflow.com/questions/52256123/unable-to-get-full-visa-address-that-includes-the-serial-number
        we will need to use the system interpreter. If so, installing packages is not possible for non-roots.
        When using vitrual eivironment, accessing gpib can be troublesome.
        '''
        sleep(0.1)
        #self.scope = self.rm.get_instrument('USB0::2733::281::030031632::0::INSTR') # Hall-setup R&S scope
        try:
            self.scope.close()
        except:
            print('no scope to close, but its okay.')
#        self.scope = self.rm.get_instrument('USB0::1689::872::C030318::0::INSTR')  # standard tektronix scope
        try:
            self.scope = self.rm.get_instrument('USB0::1689::929::C011897::0::INSTR') #LYRA tds 2002C scope
            sleep(0.1)
            self.scope.write('*IDN?')
            sleep(0.1)
            response = self.scope.read()
            print('connection to the scope OK:\n' + response)  # if ok return scope's id)
        except:
            print('ERROR: failed connecting to scope')
#        except:
 #           self.scopestatus = 'dis'
  #          return 'failed to connect to the scope!'

    def get_tunepicture(self):
        '''
        this method returns a waveform of the channel 1 of the scope.
        The connection to the scope is specified in the connect_to_scope method
        The commmands are sent in ASCII encoding via GPIB or USB interface.

        1. configure the data format and waveform locations
        2. request a waveform of Ch1'''

        self.scope.write("DATA:SOURCE CH1")#choose the source of data
        self.scope.write("DATa:ENCdg ") #choose the encoding
        #DATa: WIDth #specify number of bytes
        preamble = self.scope.query('WFMPRE?') #transfers waveform preampbe information
        curve = self.scope.query('CURVE?') #transfers the waveform data
        #initially we want the hardcopy through the usb port
        hardcopy_prt = self.scope.query('HARDCOPY:PORT?')
        print(hardcopy_prt)


        sleep(1)
        # Hall-setup R&S, 1 chan time trace:
        #curve = self.scope.query('FORM ASC;:CHAN1:DATA?')

        # standard Tektronix scope:
        #self.scope.write("DATA:SOURCE CH1")
        print(''
              'R                eprequesting tunepicture from scope Channel 1')
        #curve = self.scope.query('CURVe?') # for tektronix
        print(preamble)
        return curve


    '''-------------------------------------- Agilent Frequency Counter Commands --------------------------------'''

    def connect_to_agilent(self):
        try:
            self.agilent = self.rm.get_instrument('GPIB0::3::INSTR') #todo: learn about the agilent's gpib address and hook it up
            print('connecting to Agilent Frequency counter...')
            self.agilent.write('*RST') #connect and reset the counter
            print('connection to the frequency counter OK:\n' + self.agilent.query('*IDN?')) # if ok return counter's id
        except:
            self.agilentstatus = 'dis'
            print('ERROR: failed to connect to the Agilent frequency counter!')

    def agilent_get_MW_frequency(self):
        frequency = 0
        #sleep(5)
        self.agilent.write('*CLS') #clearing the errors
        self.agilent.write('*SRE 0')  # service request enable register clear
        self.agilent.write('*ESE 0')  # event status enable register clear
        self.agilent.write(':STAT:PRES')  # prepare for operations and questionable sreuctures
        self.agilent.write(":FUNC 'FREQ 2'")  # measuring frequency on CH2
        self.agilent.write(":FREQ:ARM:STAR:SOUR IMM") #i took that from the agilent's manual. Not completely sure what it does
        self.agilent.write(":FREQ:ARM:STOP:SOUR TIM")
        self.agilent.write(":FREQ:ARM:STOP:TIM .100") #0.1 s gate time
        self.agilent.write('READ:FREQ?')  # finally reading the frequency
        frequency = float(self.agilent.read())
        print(frequency)

        return frequency #unless communication established, return this value. Temporary.

    '''---------------------------------------- XTRALIEN COMMANDS -----------------------------------------------'''

    def connect_to_xtralien(self):
        ''' the xtralien likes to jump between the virtual ports so you never know where is it going to be
            connected to next time. Never saw ACM3 so I assume 2 is enough '''
        # TODO: finish it when you can talk to the x200
        import serial
        devices = [
            '/dev/ttyACM0',
            '/dev/ttyACM1',
            '/dev/ttyACM2',
        ]

        for device in devices:
            try:
                self.xtralien = serial.Serial(device, timeout=1)
                self.xtralienstatus = 'con'
                print(self.xtralienstatus)
                self.set_xtralien_shutter(0) # shutter is a good use for the Van-der-Pauw measurement. To be continued..
                return 'OK: ' + self.xtralien.name
            except:
                continue

        # NOTE: если хотя бы один девайс сработал, то функция закончила выполнение.

        return 'failed to connect to Xtralien SMU'


    def set_pin(self, mode: str, pin: int): # super useful stuff.
        ''' sets pin number pin to a mode mode.
            There is an arduino inside that Xtralien board and you can talk to it, too.
            Syntax is standard (LOW, HIGH)'''

        string = 'io set %s %d' % (mode, pin)
        bytestring = string.encode('ASCII')
        sleep(interval) # this is annoying but you have to do this in case you want to use Visa for talking
        self.xtralien.write('io set %s %d' % (mode, pin))

    def set_xtralien_voltage(self, source, voltage, currentrange):
        '''
        sets output of one of the source
        :param source: 1 or 2
        :param voltage: float Volts

        :param currentrange selects among the applied current ranges:
        1   100 mA
        2   10 mA
        3   1 mA
        4   10 uA
        '''
        # setting the range of current first, you don't want to burn it
        msg = 'smu%d set range %d'%(source,currentrange)
        bytemsg = msg.encode('ASCII')
        sleep(interval)
        self.xtralien.write(bytemsg)
        #here setting the voltage at the output safely
        msg = 'smu%d set voltage %f'%(source,voltage)
        bytemsg = str.encode('ASCII')
        sleep(interval)
        self.xtralien.write(bytemsg)

    def set_xtralien_averaging(self,source,N): # average over N measurements before returning result
        string = 'smu%d set filter %d'%(source,N)
        bytestring = string.encode('ASCII')
        #print(bytestring)
        self.xtralien.write(bytestring)
        sleep(interval)

    def get_xtralien_voltage(self, source):
        '''returns voltage of the corresponding source in volts
        :returns float'''

        #first set the averaging to lets say 10
        self.set_xtralien_averaging(source, 10) # okay. here we set 10 averages. might need to wait longer.
        # This is temporary

        string = 'smu%d measurev' % source
        bytestring = string.encode('ASCII')
        #print(bytestring)
        self.xtralien.write(bytestring)
        sleep(10*interval)
        response = self.xtralien.read_until('\n')
        #print(response)
        return float(response.decode('ASCII')[1:-2])

    def get_xtralien_current(self,source): # returns current in Amps, format: FLOAT

        # first set the averaging to lets say 10
        self.set_xtralien_averaging(source, 10)  # okay. here we set 10 averages. might need to wait longer

        string = 'smu%d measurei'%source
        bytestring = string.encode('ASCII')
        #print(bytestring)
        self.xtralien.write(bytestring)
        sleep(interval)
        response = self.xtralien.read_until('\n')
        return float(response.decode('ASCII')[1:-2])

    def set_xtralien_shutter(self,state: bool):
        '''writes STATE to the D12 pin,'''
        #string = 'io digital write %d %d'%(12, state)
        string = 'shutter %d'%state
        bytestring = string.encode('ASCII')
        print(bytestring)
        sleep(interval)
        self.xtralien.write(bytestring)
        return 'shutter set to %s'%state

    def move_xtralien_to(self,state: str):
        if state == 'mnop':
            sleep(interval)
            self.set_xtralien_shutter(False) # for mnop van-der-pauw measurements relay is off
        if state == 'nopm':
            sleep(interval)
            self.set_xtralien_shutter(True) # for nopm vdp meas relay needs to be on
        else:
            return ('wrong argument')

    def set_xtralien_osr(self, target: str, value: int):
        string = '%s set osr %d'%(target,value)  # herewe set OSR to a target
        bytestring = string.encode('ASCII')
        self.xtralien.write(bytestring)
        sleep(interval)

    def xtralien_interact(self, s):
        self.xtralien.write(s.encode('ASCII'))
        sleep(interval)
        response = self.xtralien.read_until('\n').decode('ASCII')
        sleep(interval)
        return response

    def get_xtralien_osr(self):
        pairs = [
            ('SMU1 OSR', 'smu1 get osr'),
            ('SMU2 OSR', 'smu2 get osr'),
            ('Vsense1 OSR', 'vsense1 get osr'),
            ('Vsense2 OSR', 'vsense2 get osr'),
        ]

        for (name, command) in pairs:
            print('%s %s' % (name, self.xtralien_interact(command)))


    def get_xtralien_vsense(self, sense: int, N: int): # measures N times at Vsense[sense] and returns voltage in Volts, format: FLOAT

      #TODO: look carefully at this section!

        string = 'vsense%d measure %d'%(sense,N) #here vsense measures N values in a row, giving an array
        bytestring = string.encode('ASCII')
        self.xtralien.write(bytestring)
        sleep(interval*2*N)
        response = self.xtralien.read_until('\n').decode('ASCII')[1:-2].split(';')
        '''TEMOPORARY!'''
        print('----- collected voltages: -----')
        print (response)
        #now we have the array of data and doing the averaging by hand
        sumup_voltage=0
        for k in response:
            sumup_voltage += float(k)
            #print('current > %s, sumup > %.3f\n'%(k,sumup_voltage))
        averaged_voltage = sumup_voltage/N
        return averaged_voltage

    '''---------------------------------------- KEITHLEY COMMANDS -----------------------------------------------'''
    def connect_to_sourcemeter(self):
        try:
            self.sourcemeter = self.rm.get_instrument('TCPIP0::192.168.1.20::inst0::INSTR') #Address might change, then change it here also
            self.sourcemeter.write("*IDN?")
            response = self.sourcemeter.read()
            self.sourcemeter.write("smua.reset()") # when connected, all reset
            self.sourcemeterstatus = 'con'
            return 'OK:\n'+response + ',sourcemeter reset.'#if ok return smu's idn and reset it
        except:
            self.sourcemeterstatus = 'dis'
            return 'failed to connect to Keithley!\n'

    def reset_sourcemeter(self): # a customized reset method, suitable for organics
        try:
            self.sourcemeter.write("smua.reset()")  # reset the source-meter
            self.sourcemeter.write("smua.source.limiti = 1000e-3")  # limit the current
            self.sourcemeter.write("smua.source.func = smua.OUTPUT_DCVOLTS")  # output volts
            self.sourcemeter.write("smua.source.rangev = 20")  # output range 20 V
            self.sourcemeter.write("smua.source.levelv = 0")  # output value 0 volts
        except:
            return('could not reset sourcemeter. check connection')

    def set_voltage_sourcemeter(self, amplitude_in_volts):
        self.sourcemeter.write("smua.source.levelv = " + str(amplitude_in_volts))  # output value for voltage is set, keithley understands volts
        self.sourcemeter.write("smua.source.output =smua.OUTPUT_ON")  # output is on!
        return 'set voltage '+str(amplitude_in_volts)+ 'V'

    def wait_ms(self,time_in_ms):
        sleep(float(time_in_ms / 1000)) #sleep method eats seconds
        return 'waited'+str(time_in_ms)+' ms'

    def get_current_sourcemeter(self, number_of_averages, delay_in_ms):
        tempCurrents = []
        for counter in range (number_of_averages):
            self.wait_ms(delay_in_ms)
            self.sourcemeter.write("currenta, voltagea = smua.measure.iv()") #writing command to read current
            tempCurrents.append(float(self.sourcemeter.ask("print(currenta)"))) #creating an array of currents
        current_value = float(sum(tempCurrents))/len(tempCurrents) #average value of temporary currents
        return current_value

    def shutdown_output_sourcemeter(self):
        self.sourcemeter.write("smua.source.output=smua.OUTPUT_OFF")
        return 0
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
  #      f2w = open('haram.txt','w')  # create and open a file for writing
    
 #       c = self.machine.process_text('WAKEUPNEO', replace_char='X') #KLOWCYJVF CFAUPBURPFRHLTY YWZABSLJHLSOQLCLXYGV
#        f2w.write('%s\n'%c)

     #   f2w.write('%s\n'%c)
    #    c = self.machine.process_text('thebodycannotlivewithoutthemind', replace_char='X') #KLOWCYJVF CFAUPBURPFRHLTY YWZABSLJHLSOQLCLXYGV
   #     self.machine.set_display('EAC')
  #      msg_key = self.machine.process_text('RST')
        
    #    f2w.write('%s\n'%c)
   #     c = self.machine.process_text('mindyourfreedom', replace_char='X') #KLOWCYJVF CFAUPBURPFRHLTY YWZABSLJHLSOQLCLXYGV
  #      self.machine.set_display('EAC')
 #       msg_key = self.machine.process_text('RST')
        
   #     f2w.write('%s\n'%c)
  #      c = self.machine.process_text('whatdoallmenwithpowerwant?Morepower', replace_char='X') #KLOWCYJVF CFAUPBURPFRHLTY YWZABSLJHLSOQLCLXYGV
 #       self.machine.set_display('EAC')
#        msg_key = self.machine.process_text('RST')
        
        #f2w.write('%s\n'%c)
        #c = self.machine.process_text('perhapsweareaskingthewrongquestion', replace_char='X') #KLOWCYJVF CFAUPBURPFRHLTY YWZABSLJHLSOQLCLXYGV
       # self.machine.set_display('EAC')
      #  msg_key = self.machine.process_text('RST')
        
   #     f2w.write('%s\n'%c)
    #    c = self.machine.process_text('youhaveaproblemwithauthority,Mr.Anderson.Youbelieveyouarespecial,thatsomehowtherulesdonotapplytoyou.Obviously,youaremistaken', replace_char='X') #KLOWCYJVF CFAUPBURPFRHLTY YWZABSLJHLSOQLCLXYGV
     #   self.machine.set_display('EAC')
  #      msg_key = self.machine.process_text('RST')
        
 #       f2w.write('%s\n'%c)

    
#        f2w.close()
