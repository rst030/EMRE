'''communication to the windfreak microwave synth.
Written by rat on 12/10/22
rst030@protonmail.com
see https://github.com/christian-hahn/windfreak-python for docs'''

from windfreak import SynthHD

class windfreak_synth(object):
    type = 'windfreak MW synth'
    model = ''
    address = '/dev/ttyACM0'
    synth = SynthHD
    fake = True

    def __init__(self):
        self.connect()

    def connect(self):
        try:
            self.synth = SynthHD(self.address)
            self.synth.init()
            self.fake = False
        except:
            self.synth = 0
            self.fake = True


    def write(self,cmd): # might be buggy!
        if self.fake:
            print('writing %s to fake windfreak.'%cmd)
            return
        self.synth.write('',str(cmd))

    def read(self):
        if self.fake:
            print('reading from fake windfreak.')
            return(1620)
        return self.synth.read('')