# emre's right hand. it is glued to a mouse with Fixogum. It can move the mouse and clicks buttons on screen.

import pyautogui # Emre's right hand
import math # sin(a), cos(m_0)

class emres_right_hand(object):
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
        reporter = 'EMRE: '
        print(reporter,s)

    def move(self,x,y): # move mouse to x,y
        pyautogui.moveTo(x,y) # just move there
        self.print('moved to %d %d'%(x,y))

    def click(self,x,y): # move mouse to x,y and click there
        pyautogui.moveTo(x,y) # first move
        pyautogui.leftClick() # and click there.
        self.print('clicked at %d %d'%(x,y))