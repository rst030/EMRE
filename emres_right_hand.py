# Emre's right hand. it is glued to a mouse with Fixogum. It can move the mouse and clicks buttons on screen.

import pyautogui # Emre's right hand
import math # sin(a), cos(m_0)

class emres_right_hand(object):
    type = 'right hand'
    address = 'local'
    # fields: mouse X, mouse Y
    x : int
    y : int
    screenWidth = 0
    screenHeight = 0  # width and height of the screen that EMRE sees now.
    currentMouseX = 0
    currentMouseY = 0  # mouse coordinates
    fake = False # fake emres hand

    def __init__(self):
        # emre wakes up
        self.screenWidth, self.screenHeight = pyautogui.size()  # look at the screen and see its size
        self.print('See screen %d x %d p'% (self.screenWidth, self.screenHeight))
        self.currentMouseX, self.currentMouseY = pyautogui.position()
        self.print('Mouse at [%d,%d]'%(self.currentMouseX, self.currentMouseY))

    def print(self,s: str):
        reporter = 'EMRE''s right hand: '
        print(reporter,s)

    def move(self,x,y): # move mouse to x,y
        pyautogui.moveTo(x,y) # just move there
        self.print('moved to %d %d'%(x,y))

    def click(self,x,y): # move mouse to x,y and click there
        pyautogui.moveTo(x,y) # first move
        pyautogui.leftClick() # and click there.
        self.print('clicked at %d %d'%(x,y))

    def start_magnettech_sequence(self,x,y):
        self.click(x=x,y=y)
        self.print('\nhacking the ESR studio: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX [100%]\n')

    def write(self,cmd):
        print('dont write on your hand, you mosquito. %s, really?'%cmd)

    def read(self):
        return('todo: get your ship together')