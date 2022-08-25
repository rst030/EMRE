'''Communication to the Keithley 2450 source-measure unit.
written by rst on 27/10/20
ilia.kulikov@fu-berlin.de'''

import numpy as np
import pyvisa as visa
from time import sleep
from datetime import datetime  # this thing gets current time
import Plotter
import random # for fake data
import cv # a CV object, for saving and running a cv
import chg # a CHG object, for saving and running a chg

CURRENTSENSITIVITYLIMIT = 5e-3 # change it for different samples

class pstat (object):
    model = '2450'                    # default model is 2450 that is the pstat at Lyra
    address = 'GPIB0::18::INSTR'      # and this is its GPIB address
#    usb_address = 'USB0::0x05E6::0x2450::04509830::INSTR' # this is its usb_address of the new pstat
    usb_address = 'USB0::0x05E6::0x2450::04431893::INSTR' # this is its usb_address of the new pstat
    device = visa.Resource            # pyvisa device that is populated with the constructor
    rm = 0                            # visa resource manager
    fake = False                      # use simulated outputs. Used for testing outside the lab.

    plotter = Plotter.Plotter

    # emergency stop break handle
    GlobalInterruptFlag = False

    def __init__(self, rm: visa.ResourceManager, model: str, plotter: Plotter.Plotter): # when create a lia you'd better have a resource manager already working
        '''create an instance of the pstat object''' # создать объект потенциостата.
        self.rm = rm
        self.connect(model)
        self.write('*RST')  # ресетнем ка мы его на всякий случай
        self.write('*IDN?') # и спросим, как его зовут
        response = self.read()
        self.play_tune()
        self.write('DISP:SCR SWIPE_GRAP')
        self.write('SENS:CURR:RSEN ON') # 4 WIRE SENSING MODE.
        self.write('SENS:FUNC \'CURR\'')
        self.write('SENS:CURR:RANG:AUTO OFF')
        self.write('SENS:CURR:RANG %.4f'%CURRENTSENSITIVITYLIMIT)
        self.write('SENS:CURR:UNIT AMP') # double check it
        self.write('SENS:CURR:OCOM ON')
        self.write('SOUR:FUNC VOLT')
        self.write('SOUR:VOLT 0')
        self.write('SOUR:VOLT:ILIM %.4f'%CURRENTSENSITIVITYLIMIT)
        
        self.write('COUNT 1') # 1 points of current to measuer

################## CHANGE THIS FOR DITS!!! ######################
        self.ConfigureForTransient() # ! change for PDITS. for testing ok.
#################################################################

        self.print(response)

        self.plotter = plotter #
        self.plotter.axes.set_title('TEST')
        tstx = [-1, 0, 1, 2, 3]
        tsty = [1, 0, 3, 5, 3.14159265358979323846264338327950288419716939937510]
        self.plotter.plotCvData(tstx,tsty)

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
            self.address = 'GPIB0::18::INSTR'  # pad 18
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

    def play_reading_beep(self):
        self.beep_tone(1413,0.1)

    def play_tune(self):
        for offtune in range(5):
            for _ in range(1):
                # happy C goes wild:
                self.beep_tone(523.251+ 35*offtune, 0.005)
                self.beep_tone(783.991+ 35*offtune, 0.005)
                self.beep_tone(659.255+ 35*offtune, 0.005)
        for offtune in range(5,0,-1):
            for _ in range(1):
                # happy C goes wild:
                self.beep_tone(523.251+ 35*offtune, 0.005)
                self.beep_tone(783.991+ 35*offtune, 0.005)
                self.beep_tone(659.255+ 35*offtune, 0.005)
        self.print('call the police.')


    def set_voltage(self,voltage_in_volts):  # sets voltage and presets the trigger (1 second transient for now)
        # ставим напряждение в вольтах на выход пстата и марuм ток. На морде показываем ток. Сам показывается он.
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

        self.write(':SENSe:CURRent:NPLCycles 0.01') # change to 0.5 to measure faster. Youll get oscillations! Affects measurement speed.

        self.print('setting up trigger model to DurationLoop: %.2f s'%duration_in_seconds)
        self.write('TRIG:LOAD \"DurationLoop\", %.2f, %.4f, \"CYKA_BLYAT\"' % (duration_in_seconds,delay_in_seconds))  # load trigger model 0.5 us TEMPORARY!


    def delete_trace(self):
        self.write(':TRACe:DELete \"CYKA_BLYAT\"')

    def trigger_current_transient(self): # starts current transient measurement.
        print('trigger current transient [NOW] <-')
        self.write('INIT') # initiate the readings of current WOUD THIS WORK ??? apparently it does
        self.write('*WAI') # postpone execution of successive commands while this is executed.
        self.write('OUTP ON')  # keep output on

        # This sets the trigger on time loop
        # and store the readings in the \"CYKA_BLYAT\" reading buffer.

        self.write('TRAC:TRIG \"CYKA_BLYAT\"') # this puts readings on its face / also to the buffer.

    def query_current_transient(self, NPTS: int):# returns the current readings in a string!
        print('attempting to read %d values from CYKA_BLYAT buffer ++++ P'%NPTS)
        self.play_reading_beep()
        self.write('TRAC:DATA? 1, %d, \"CYKA_BLYAT\", SOUR, READ, REL'%NPTS) # Read the NPTS data points, reading, programmed source, and relative time for each point.

        return self.read()


    def output_on(self): # self explanatory
        self.play_short_beep()  # short beep when pot on
        self.write('OUTP ON')  # here we turn output on
    #    self.trigger_current_transient()  # and immediately after, start measuring it. For 1 second as for now



        # #self.write('TRAC:TRIG \“defbuffer1\”') # this is for measurement trace. So far not in use.
        #self.write('TRAC:DATA? 1, 5, \“defbuffer1\”, SOUR, READ') # not sure if we need it

    def output_off(self): # self explanatory
        self.write('OUTP OFF')  # here we turn output off
        self.play_short_beep()  # short beep when pot on
        sleep(0.2)
        self.play_short_beep()  # twice

    def configureCv(self):
        #self.write(':TRACe:MAKE \"CYKA_BLYAT\", 10')
        self.write(':SENSe:CURRent:NPLCycles 0.01') # change to 0.5 to measure faster. Youll get oscillations! Affects measurement speed.
        self.print('goddamnit I am quick')
        self.write(':SENS:FUNC \"CURR\"') # measure current
        self.write(':SOUR:VOLT:ILIM %.4f'%CURRENTSENSITIVITYLIMIT) # 100 mA typically
        self.write('SENSe:COUNt 1') # 1 point to record
        self.print('CV measurement configured. Turning output ON. Jesus Christ saves your battery.')
        self.write(':OUTP ON')

    def configureCHG(self,absoluteValueOfVoltageLimit: float):
        self.write(':SENSe:CURRent:NPLCycles 0.01') # change to 0.5 to measure faster. Youll get oscillations! Affects measurement speed.
        self.write(':SENS:FUNC \"VOLT\"') # measure volts
        self.write(':SOUR:CURR:VLIM %.4f' % absoluteValueOfVoltageLimit)  # 100 mA typically

        #todo: set it up on a working machine. the voltage limit of the current source!!!

    def getCHGpoint(self, current_in_amps):
        # setting the current
        self.write(':SOUR:CURR %.3f' % current_in_amps)
        try:
            voltageString = self.device.query('MEASure:VOLTage:DC?') # 1 point it is supposed to be.
        except:
            return random.randint(50,790)/1000
        #self.write('TRACe:DATA? 1,2, \"CYKA_BLYAT\", READ, REL, SOUR')# 2, 9')
        #currentString = self.read() instead of query if you want to wait for a few plc.
        #print(currentString) # temp
        voltage = float(voltageString)#np.mean(np.array(self.read().split(',')).astype(float))
        return voltage


    def getCvPoint(self, voltage_in_volts: float, sleeptime: float):
        
        self.write(':SOUR:VOLT %.3f' % voltage_in_volts)
        sleep(sleeptime) # if CV intensity behaves weirdly vs your scan rate, the problem may be in this line.
        #self.write(':TRAC:CLEAR')
        try:
            currentString = self.device.query('MEASure:CURRent:DC?') # 1 point it is supposed to be.
        except:
            return random.randint(0,100)
        #self.write('TRACe:DATA? 1,2, \"CYKA_BLYAT\", READ, REL, SOUR')# 2, 9')
        #currentString = self.read() instead of query if you want to wait for a few plc. 
        #print(currentString) # temp
        current = float(currentString)#np.mean(np.array(self.read().split(',')).astype(float))
        return current


    def TakeCV(self, cv_input:cv.cv, plotter: Plotter.Plotter):
        '''take a cv curve with parameters specified in the given cv.cv. plot in the given  plotter'''
        cvTaken = cv_input

        self.plotter = plotter # plot cv in the plotter that is given as argument

        # do the electrochemical business here
        nStepsUp = 128 # n steps in voltages when going up in potentials

        # delay time arithmetics. It took 184.440660 - 0.000225 s to complete 10 scans of 2 volts each.
        # that makes it 20 volts per 184.440435 s that is 0.10843609211830367 V/S = 108 mV/s,
        # the MAX rate limited by the matplotlib at my x220. Stupid but I dont have another machine now.
        # so what is the default delay that it is adding? 0.06 ... 0.11 s per point.
        # i guess id not plot it at all then, but I have to see the stuff.
        # using a thread would be a great option
        # but anyways, if plotted every 5 points the delay is OKAY.
        # how much to wait every time I get a CV?

        scanWidthInMv = cvTaken.high_voltage_point - cvTaken.low_voltage_point # in mV
        rateInMvPerSecond = cvTaken.scan_rate # in millivolts per second
        numberOfPointsInScan = nStepsUp
        delayBetweenPointsInSeconds = scanWidthInMv / rateInMvPerSecond / numberOfPointsInScan

        # considering that fucking matplotlib delay
        if delayBetweenPointsInSeconds < 0.1: #second
            delayBetweenPointsInSeconds = 0
        else:
            delayBetweenPointsInSeconds = delayBetweenPointsInSeconds - 0.1

        # make vector with potentials
        pot_up_vector = np.linspace(cvTaken.low_voltage_point, cvTaken.high_voltage_point, nStepsUp)
        pot_down_vector = np.linspace(cvTaken.high_voltage_point, cvTaken.low_voltage_point, nStepsUp)
        pot_vector = np.concatenate((pot_up_vector,pot_down_vector),axis = 0)

        starttime = datetime.now()  # get current time. start of the cv
        cvTaken.datetime = str(starttime)

        # ELECTRICITY ON!
        self.configureCv()
        for _ in range(cvTaken.n_cycles):

            for i in range(len(pot_vector)):
                potential = pot_vector[i]
                cvTaken.voltage.append(potential)
                current = self.getCvPoint(voltage_in_volts=potential,sleeptime = delayBetweenPointsInSeconds)
                cvTaken.current.append(current)
                reltime = (datetime.now() - starttime).total_seconds()
                cvTaken.time.append(reltime) # relative time in microseconds
                if i%1 == 0: # how often to plot. Each point is ok for now but that would be a constant delay!!!
                    self.plotter.plotCvData(cvTaken.voltage, cvTaken.current)

                self.plotter.title = 'cycle %d/%d' % (_+1, cvTaken.n_cycles)
                # emergency stop break:
                if self.GlobalInterruptFlag:
                    self.GlobalInterruptFlag = False
                    return cvTaken

        return cvTaken

    def TakeCV_the_old_way(self, lowPotential: float, highPotential: float, rate: float, filePath:str):


        nstepsup = 100
        dv = (highPotential-lowPotential)/nstepsup # step in voltages assuming nstepsup steps up and 100 down
        R = rate / 1000 # in volts per second.
        dt = dv/R
        print('pstat:cv: dt=%.2e s'% dt)
        print('pstat:cv: dv=%.2e V' % dv)
        print('pstat:cv: R=%.2e V/s' % R)

        setVoltages = []  # to be appended
        measuredCurrents = [] # to be measured and appended


        starttime = str(datetime.now())  # get current time. start of the cv



        self.configureCv()
        for ctr in range(0,nstepsup,1):
            voltagetoset = lowPotential+ctr*dv
            currents = self.getCvPoint(voltage_in_volts=voltagetoset)
            sleep(dt)
            setVoltages.append(voltagetoset)
            #print('cv up, step: %d'%ctr)
            #print('...voltage: %.2e V' % voltagetoset)
            #print('...%.2e A'%currents)
            measuredCurrents.append(currents)
            # now plotting it irl also
        
            self.plotter.plotCvData(setVoltages,measuredCurrents)
        voltagetoset = highPotential
        self.set_voltage(voltagetoset)

        for ctr in range(0, nstepsup, 1):
            voltagetoset = highPotential - ctr * dv
            self.set_voltage(voltagetoset)
            currents = self.getCvPoint(voltage_in_volts=voltagetoset)
            sleep(dt)
            setVoltages.append(voltagetoset)
            #print('cv down, step: %d' % ctr)
            #print('cv: voltage: %.2e V' % voltagetoset)
            #print('cv%.2e A' %currents)
            measuredCurrents.append(currents)
            # now plotting it irl also
        
            self.plotter.plotCvData(setVoltages, measuredCurrents)
        voltagetoset = lowPotential
        self.set_voltage(voltagetoset)

        self.output_off()


        # ------------------------- saving CV to csv file ------------------------------
        savefile = open(filePath+'.csv', 'w')  # open the file
        f2w = savefile
        f2w.write('start, %s\n' % (str(starttime)))
        endtime = str(datetime.now())  # get current time. start of the cv
        f2w.write('end, %s\n' % (str(endtime)))

        f2w.write('low, %.3f, V\n' % float(lowPotential))
        f2w.write('high, %.3f, V\n' % float(highPotential))
        f2w.write('rate, %.3f, mV/s\n' % float(rate))

        for i in range(len(measuredCurrents)):
            f2w.write("%.8e, %.8e,\n" % (setVoltages[i], measuredCurrents[i]))

        f2w.close()
        



    def TakeCHG(self, chg_input:chg.chg, plotter: Plotter.Plotter):
        '''take a chg cycle with parameters specified in the given chg.chg. plot in the given  plotter'''
        chgTaken = chg_input

        self.plotter = plotter # plot cv in the plotter that is given as argument, switchable SNOUT!

        highVoltageLimit = chg_input.high_voltage_level
        lowVoltageLimit = chg_input.low_voltage_level

        starttime = datetime.now()  # get current time. start of the cv
        chgTaken.datetime = str(starttime)

        # ELECTRICITY ON!
        for _ in range(chgTaken.n_cycles):
            # do chg until the high limit ---- CHG CHG CHG CHG CHG CHG CHG CHG CHG ----
            self.configureCHG(absoluteValueOfVoltageLimit=highVoltageLimit)  # go set the knobs there
            measuredVoltage = -65535  # for sure less than the high limit

            while measuredVoltage < highVoltageLimit:
                currentToApply = chg_input.chg_current # charging with the chg current of the passed chg object
                reltime = (datetime.now() - starttime).total_seconds()
                chgTaken.time.append(reltime)
                chgTaken.current.append(currentToApply)
                measuredVoltage = self.getCHGpoint(current_in_amps=currentToApply)
                chgTaken.voltage.append(measuredVoltage)

                # keep plotting
                self.plotter.plotChgData(chgTaken)
                self.plotter.title = 'CHG %d/%d | %.1f / %.1f [V]' % (_ + 1, chgTaken.n_cycles, measuredVoltage, highVoltageLimit)

                # emergency stop break:
                if self.GlobalInterruptFlag:
                    self.GlobalInterruptFlag = False
                    return chgTaken


            # then do dcg until the low limit ---- DCG DCG DCG DCG DCG DCG DCG DCG ----
            self.configureCHG(absoluteValueOfVoltageLimit=lowVoltageLimit)  # go set the knobs there
            measuredVoltage = 65535  # for sure less than the high limit

            while measuredVoltage > lowVoltageLimit:
                currentToApply = chg_input.dcg_current  # discharging with the dcg current of the passed chg object
                reltime = (datetime.now() - starttime).total_seconds()
                chgTaken.time.append(reltime)
                chgTaken.current.append(currentToApply)
                measuredVoltage = self.getCHGpoint(current_in_amps=currentToApply)
                chgTaken.voltage.append(measuredVoltage)

                # keep plotting
                self.plotter.plotChgData(chgTaken)
                self.plotter.title = 'DCG %d/%d | %.1f / %.1f [V]' % (_ + 1, chgTaken.n_cycles, measuredVoltage, lowVoltageLimit)

                # emergency stop break:
                if self.GlobalInterruptFlag:
                    self.GlobalInterruptFlag = False
                    return chgTaken

        return chgTaken

    def ConfigureForTransient(self):
        #self.write(':TRACe:MAKE \"CYKA_BLYAT\", 10')
        self.write('TRAC:MAKE \"CYKA_BLYAT\", 65535')  # create buffer with n points
        self.write('SENSe:CURRent:RANG %.4f'%CURRENTSENSITIVITYLIMIT)
        self.write(':SENS:FUNC \"CURR\"') # measure current
        self.write(':SOUR:VOLT:ILIM %.4f'%CURRENTSENSITIVITYLIMIT) # 100 mA
        self.write('SENSe:COUNt 1') # 1 point to record
        self.write(':OUTP OFF')
        
    def TakeChargingTransient(self, potentialToSet: float, durationInSeconds: float, filePath:str):
        # taking the current transient.
        # setting the potentialToSet for durationInSeconds
        # saving the transient in filePath
        
         
        interval = 0.001 # interval between the points in the transient
        
        self.print('configure transient trigger')
        self.configure_transient_trigger(durationInSeconds, interval)
        self.print('setting voltage %.2f'%potentialToSet)
        self.set_voltage(potentialToSet)
        self.trigger_current_transient()
        sleep(durationInSeconds+1) # one sec
        self.print('query %d pts from buffer'%durationInSeconds*220)
        try:
            transients = self.query_current_transient(durationInSeconds*220) # SOUR, READ, REL 13500 for 60 s -> 255 pts/s -> 1125 pts for 5 s
        except:
            self.print('reading transient failed. Launching ICBMs.')
        self.print('OUTPUT is still on!')
        
        dt = str(datetime.now())  # get current time. start of the CT
        
        print(transients)
        
        # saving those guys to a file
        current_transient_file = open('%s.chg' %filePath, 'w')  # open the file            
        #  header
        current_transient_file.write('Pot_set[V], Pot_meas[V], Current[A], rel_time[s], scan_state\n')
        try:
            # query the current transient
            # saving current transient
            vls = transients.split(',')
            for i in range(0, len(vls), 3):
                current_transient_file.write(
                    '%.2f, %.6e, %.6e, %.6e,\n' % (potentialToSet, float(vls[i]), float(vls[i + 1]), float(vls[i + 2])))

        except:
            self.print('[   Failed reading current transient.\n   The warhead is ready for combat.\n  Launchpad 78\n  Calculating trajectory...]')
      
        # closing the current transient file
        current_transient_file.write('\n'+dt+'\n')
        current_transient_file.write('dt = %.3e s, t = %.3e s\n'%(interval,durationInSeconds))
        current_transient_file.close()                                                      

    #todo: chg/dcg potentiometry with voltage limits
        
    def print(self,s:str):
        print('Keithley 2450-EC >> : %s'%s)