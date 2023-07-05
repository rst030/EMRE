'''two threads communicate through a queue.
one thread generates data (quickly) and puts it to the queue.
other thread reads data from the queue and plots it.
230706 rst rst030@protonmail.com'''

import random
from multiprocessing import Process, Queue
from time import sleep
import plotting_GUI

import cv
import cv as cvclass

cvGlob = cv.cv # global variable, careful.

def data_generator(q: Queue):
    cvG = cvclass.cv()
    i=0
    while 1:
        i=i+1
        print('writing %d'%i)
        cvG.time.append(i)
        cvG.current.append(random.uniform(-1, 1))
        q.put(cvG)
        sleep(0.0001)

def data_receiver(q: Queue):

    import plotting_GUI
    pltr = plotting_GUI.plotter()

    cvR = cvclass.cv() # cv curve to be updated from the queue q
    while not q.empty():
        print('getting cvG as cvR')
        print('to read: %d'%q.qsize())
        while not q.empty():
            cvR = q.get()
            print('size of queue: %d'%q.qsize())

        print('received',cvR.current[-1])

        pltr.replot(cvR.time,cvR.current);





if __name__ == '__main__':

    q = Queue(maxsize = 100000)
    p_generator = Process(target=data_generator, args=(q,))
    p_generator.start()

    p_receiver = Process(target=data_receiver, args=(q,))
    p_receiver.start()

    p_generator.join()
    p_receiver.join()

    #todo make a mpl plotter in data_receiver method
