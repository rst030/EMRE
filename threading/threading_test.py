from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import sys
import time

from multiprocessing import Queue


class TTT(QThread): # oт это у нас кусрэд, но наш, русский, родной, ТТТ.
    def __init__(self, q:Queue):  # and here is its constructor
        super(TTT, self).__init__() # from a parent to be born
        self.quit_flag = False # and no flag was given to ever quit anything
        self.q = q # there put what you have done in your miserable life

    def run(self): # it waits, like a cat in a bush, when you call it. Run! - you shout.
        while True: # for thy while truth is the truth, while there is no justice needed to be involved,
            if not self.quit_flag: # until you haven't put the quit flag
                self.doSomething()  # you will be doing it.
                time.sleep(1)  # over and over, again and again
                self.q.put('5')
                print(self.q.qsize(), 'long')
            else:
                break

        self.quit()
        self.wait()

    def doSomething(self):
        print('123')



class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.btn = QtWidgets.QPushButton("run process")
        self.btn2 = QtWidgets.QPushButton("read queue")

        self.btn.clicked.connect(self.create_generator_process)
        self.btn2.clicked.connect(self.create_listener_process)

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.btn)
        layout.addWidget(self.btn2)

        self.setLayout(layout)
        self.show()

        self.t = None
        self.q = Queue()

    def create_generator_process(self):
        if self.btn.text() == "run process":
            print("Started")
            self.btn.setText("stop process")
            self.t = TTT(self.q)
            self.t.start()
        else:
            self.t.quit_flag = True
            print("Stop sent")
            self.t.wait()
            print("Stopped")
            self.btn.setText("run process")

    def create_listener_process(self):
        if not self.q.empty():
           print('------------------------',self.q.get())



if __name__=="__main__":
    app=QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())