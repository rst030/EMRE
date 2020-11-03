import communication
import numpy as np

'''connector connects to the scope and to the Agilent. Reading Q and reading F'''

frequency = 9.4e9 # MW frequency to be read from the Agilent frequency counter.
tunepicture = [0,1,2,3,4,5,6,7,8,9,9,9,10,5,2,1,2,5,10,9,9,9,8,7,6,5,4,3,2,1,0] # tunepicture to be read from the scope
frequency_span = 1e7 #TODO: get this value from Christopher's script!
frequency_scaling_factor = 6.94e4 #MHz/s
start_freq = frequency - frequency_span/2
stop_freq = frequency + frequency_span/2
numpts = 31 # TODO: get real number of pts from the scope. There was a command, look up in the manual.
sweepvals = np.linspace(0,5e-5, numpts) # vector of frequencies - look up in Christopher's Matlab script for getQ.
communicator = 0 # a global var

'''Connect. Here we connect to our devices and read the tunepicture and the central frequency'''
def connect():


    communicator = communication.communicator(backend='@py')#(backend = '@py') #todo: when on Debian, change it to '@py', there is no NI backend available.
    communicator.list_resources() # printing available resources. Useful for NI, useless for PY, but with GPIB working its useful for both.
    '''connecting to the scope:'''
    communicator.connect_to_scope() #prints IDN if all good
    '''connecting to Agilent:'''
    communicator.connect_to_agilent()  # prints IDN of the Agilent if all good

    # hall's R&S scope:
    #tunepicture_raw = (communicator.get_tunepicture().split(','))
    #tunepicture_raw = tunepicture_raw[10:len(tunepicture_raw)-10]
    #tunepicture = []
    #for k in tunepicture_raw:
    #    tunepicture.append(float(k))

# this is for the Tek scope:
    tunepicture_raw = communicator.get_tunepicture().split(',') #this contains time axis and tunepicture. we need both in order to be consistent with Christopher E.
    print('raw data is:\n')
    print(tunepicture_raw)
    tunepicture = []
    for element in tunepicture_raw:
        tunepicture.append(float(element))

    sweepvals = np.linspace(0,50e-6,len(tunepicture)) #time trace length is 50 us!
    print(len(sweepvals))
    '''ok now we have the scope data. Now reading the frequency of the agilent'''

    return communicator, sweepvals, tunepicture #a mess, but dont see another way for now...

def get_MW_frequency(communicator):
    MW_frequency = communicator.agilent_get_MW_frequency()
    return MW_frequency


def refresh(communicator):
 # hall's R&S scope:
 #   tunepicture_raw = (communicator.get_tunepicture().split(','))
 #   tunepicture_raw = tunepicture_raw[10:len(tunepicture_raw)-10]
 #   tunepicture = []
 #   for k in tunepicture_raw:
 #       tunepicture.append(float(k))

    tunepicture_raw = communicator.get_tunepicture().split(',')
    tunepicture = []
    for element in tunepicture_raw:
        tunepicture.append(int(element))
    sweepvals = np.linspace(0,50e-6,len(tunepicture)) #50 us timebase . We return timebase with time in order to check with Christophers script. 6.94e4 Hz/sec scale factor - later
    '''We return real frequencies and absolute tunepicture when refreshing!'''

    return sweepvals, tunepicture
#def save():
#    '''saving temporary tunepicture to a file'''
#    tunepicturefile = open(r"D:\PycharmProjects\q\tune_pic_temp.txt","w") #todo: change address while on linux!
#    for i in tunepicture:
#        tunepicturefile.write('%d\n'%i)
#    tunepicturefile.close()



