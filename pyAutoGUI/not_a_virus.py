import pyautogui # Emre's right hand
import math # sin(a), cos(m_0)

#https://pypi.org/project/PyAutoGUI/

screenWidth, screenHeight = pyautogui.size() # returns two integers, width and gheight of the screen. 
print(screenWidth,'by',screenHeight)

currentMouseX, currentMouseY = pyautogui.position() # Returns mouse coordinates
print('mouse at ',currentMouseX,';',currentMouseY)

# move the mouse from python
pyautogui.moveTo(300,720)

currentMouseX, currentMouseY = pyautogui.position() # Returns two integers, the x and y of 
print('mouse at ',currentMouseX,';',currentMouseY)

# now move the mouse
def MoveInAine(inc:int):
# inc < 0 -> going up
	curX, curY = pyautogui.position()
	for i in range(42):
		newX = curX
		newY = curY+inc*i
		pyautogui.moveTo(newX,newY)

def MoveSemiCircle(rad:int, initphase:int):
	
	curX, curY = pyautogui.position()
	newX = curX - rad*math.sin(math.pi/42*0+initphase)
	newY = curY + rad*math.cos(math.pi/42*0+initphase)
	pyautogui.moveTo(newX,newY)
	curX = curX 
	curY = newY
	
	for i in range(42):
		newX = curX + rad*math.sin(math.pi/42*i+initphase)
		newY = curY - rad*math.cos(math.pi/42*i+initphase)
		pyautogui.moveTo(newX,newY)

# draw
while 1:
	pyautogui.moveTo(302,800)
	MoveSemiCircle(rad=68,initphase = -math.pi)
	MoveInAine(inc=-10)
	MoveSemiCircle(rad=32,initphase = -math.pi/2)
	MoveInAine(inc=10)
	MoveSemiCircle(rad=70,initphase = 0)






 

		
		









