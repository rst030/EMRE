'connect to keithley 2450 pot/SMU. Handshake.'
import communication
from time import sleep
import numpy as np

lyra_communicator = communication.communicator('@py') #create a communicator with pyvisa-py backend.
list = lyra_communicator.list_resources() #list the connected devices (except tcpip and GPIB maybe that is crap actually)
#now lets ping all our GPIB devices
'''
    ok great we have now: 
    Agilent Counter on GPIB0::3::INSTR
    SRS SR810 LIA   on GPIB0::9::INSTR
    Keithley Pot    on GPIB0::18::INSTR
    Lovely BH15 field controller on GPIB0::8::INSTR
    So we can do something by now.'''

'''------------------- connecting to the devices ---------------------------'''
lyra_communicator.connect_to_lockin(model=810) #Lyra's SR810 LIA

lyra_communicator.connect_to_field_controller()
sleep(1)
print('going remote')
lyra_communicator.goremote()
lyra_communicator.set_operating_mode_of_field_controller(0)
print('set to mode 0 now')
'''--------------------------------------------------------------------------'''

lyra_communicator.field_controller_set_center_field(3300)
sleep(5)

print('getting LED astatus with LE')
lyra_communicator.field_controller_get_led_status()


'''HERE IS THE PROBLEM. THE PROBLEM IS WITH READ
    lets try SDC - no, its not SDC. UNT? Nope.
    reading blank? - nope.
    what can it be? why it hangs?!
    It was the damn \r. Termination for writing to this can is \r, not \r\n.'''

'''lets sweep the field and print the measured values and LED statuses'''
'''and save this junk in a file not far away'''
spectrum_file = open(r"cw_spectrum_test","w")

'''let us create an array of B0s. Numpy?'''
B0_start = 3300
B0_stop  = 3500
B0_step  = 0.2 #G
B0_array = np.arange(B0_start, B0_stop, B0_step)

'''Mod Amp. Measured with the scope, for 0.2G we set 1V amplitude. Frequency is 100kHz.'''
lyra_communicator.setLockinFrequency(99000) #99 kHz
lyra_communicator.setLockinVoltage(1.0) #amp is 1V


for B0 in range(3300, 3500, 1):

    '''move to basic field control mode that is mode 0'''
    lyra_communicator.curse_BH15('MO0')
    '''set field to current B0'''
    lyra_communicator.field_controller_set_center_field(B0)
    '''move to field measure mode that is mode 5'''
    lyra_communicator.curse_BH15('MO5')
    '''get the led status'''
    ledstatus=lyra_communicator.talk_to_BH15('LE')
    '''measure field'''
    B0_measured = lyra_communicator.talk_to_BH15('FC')
    '''God save the magnet.'''

    '''lets now talk about the microwave absorption. This is measured with the LIA. Lets talk to the LIA.'''
    voltage_in_the_r_channel = lyra_communicator.getLockinR()

    '''careful there with sleep'''
    sleep(0.1)
    '''our spectrum'''

    string = 'B0 %s G | LED: %s | signal: %.3f | TC: %.3f s'%(B0_measured[3:9],voltage_in_the_r_channel)
    spectrum_file.write(string)

'''close the spectrum file'''
spectrum_file.close()

'''set field to 3300 again.'''
lyra_communicator.field_controller_set_center_field(3300)
sleep(5) #waiting for the magnet to come down




