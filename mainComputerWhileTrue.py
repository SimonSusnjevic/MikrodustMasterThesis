# Imports
import pyb
import machine
from pyb import Accel
from pyb import Pin

# In/Out -puts defenition
accel = Accel() # built in accelorometer

led1 = pyb.LED(1)
led2 = pyb.LED(2)
led3 = pyb.LED(3)

switch = pyb.Switch() # built in switch

# defenition of pins
# input pins used with interupts
lightCurtain_x5 =   Pin('X5', Pin.IN, Pin.PULL_UP)
dutFinished_x6  =   Pin('X6', Pin.IN, Pin.PULL_UP)
closeLid_x7     =   Pin('X7', Pin.IN, Pin.PULL_UP)
allLightsOff_x8 =   Pin('X8', Pin.IN, Pin.PULL_UP)
switch          =   Pin('X17', Pin.IN, Pin.PULL_UP)
# output pins connected to the cylindervalves
# passRelay:
#   True: valve can move to right or left
#   False: valve is in non powerd state
# switchRelay:
#   True: cylinder retracts (gets pushed in)
#   False: cylinder extends (gets pushed out)
passRelay50_x1         =   Pin('X1', Pin.OUT)
cylinderRetract50_x2   =   Pin('X2', Pin.OUT)
passRelay80_x3         =   Pin('X3', Pin.OUT)
cylinderRetract80_x4   =   Pin('X4', Pin.OUT)
startValue = False
passRelay50_x1.value(startValue)
cylinderRetract50_x2.value(startValue)
passRelay80_x3.value(startValue)
cylinderRetract80_x4.value(startValue)

# Constants
# tuning parameters for accelorometer output
fullyClosedX        =   [ -7,  -4]
fullyClosedY        =   [ 19,  22]
closedNotLockedX    =   [ 15,  17]
closedNotLockedY    =   [ 11,  13]
fullyOpenX          =   [ 15,  18]
fullyOpenY          =   [-17, -14]


################################################################################################
########################################Program start###########################################
################################################################################################

# Pin debounce
def pinDebounce(pin):
    prev = None
    for _ in range(32):
        current_value = pin.value()
        if prev != None and prev != current_value:
            return None
        prev = current_value
    return prev




# External interupts

#=================TEST=================
#def lightCurtain_x5_Callback(pin):
#    if not pinDebounce(pin):
#        passRelay50_x1.value(not passRelay50_x1.value())
#        print("btn1")

#def dutFinished_x6_Callback(pin):
#    if not pinDebounce(pin):
#        cylinderRetract50_x2.value(not cylinderRetract50_x2.value())
#        print("btn2")

#def closeLid_x7_Callback(pin):
#    if not pinDebounce(pin):
#        passRelay80_x3.value(not passRelay80_x3.value())
#        print("btn3")

#def allLightsOff_x8_Callback(pin):
#    if not pinDebounce(pin):
#        cylinderRetract80_x4.value(not cylinderRetract80_x4.value()) 
#        print("btn4")

#def switch_Callback(pin):
#    if not pinDebounce(pin):
#            cylinderRetract80_x4.value(not cylinderRetract80_x4.value())
#            print("btn4")
#=================TEST=================



def lightCurtain_x5_Callback(pin):
    if not pinDebounce(pin):
        print("LIGHT CURTAIN!!!")
        led1.on() # Debug
        passRelay50_x1.value(False)
        passRelay80_x3.value(False)
        cylinderRetract50_x2.value(False)
        cylinderRetract80_x4.value(False)
        temp = True
        while temp:
            temp = allLightsOff_x8.value()
            pyb.delay(1)
    elif pinDebounce(pin):
        led1.off() # Debug


def dutFinished_x6_Callback(pin):
    if not pinDebounce(pin):
        led2.on() # Debug
        if lidState() == "fullyClosed":
            print("Lid is fully closed")
            if unlockLid():
                print("lid was successfully unlcoked")
                if openLid():
                    print("lid was successfully opened")
                else:
                    print("failed to open")
            else:
                print("failed to unlock")
        else:
            print('failed to unlock')
            
    elif pinDebounce(pin):
        led2.off() # Debug


def closeLid_x7_Callback(pin):
    if not pinDebounce(pin): # button pressed
        led3.on() # debug
        if lidState() == "fullyOpen":
            print("lid is fully opened")
            if closeLid():
                print("lid was successfully closed")
                if lockLid():
                    print("lid was successfully locked")
                else:
                    print("failed to lock lid")
            else:
                print("failed to close lid")
        else:
            print('failed to close')
    elif pinDebounce(pin): # button released
            led3.off()

def allLightsOff_x8_Callback(pin):
    if not pinDebounce(pin):
        passRelay50_x1.value(startValue)
        passRelay80_x3.value(startValue)
        cylinderRetract50_x2.value(startValue)
        cylinderRetract80_x4.value(startValue)
        led1.off()
        led2.off()
        led3.off()



# the lines bellow triggers the interupts (?)
lightCurtain_x5.irq(trigger = Pin.IRQ_FALLING, handler = lightCurtain_x5_Callback)
#dutFinished_x6.irq(trigger = Pin.IRQ_FALLING, handler = dutFinished_x6_Callback)
#closeLid_x7.irq(trigger = Pin.IRQ_FALLING, handler = closeLid_x7_Callback)
#allLightsOff_x8.irq(trigger = Pin.IRQ_FALLING, handler = allLightsOff_x8_Callback)
#switch.irq(trigger = Pin.IRQ_FALLING, handler = switch_Callback)








# General functions used throughout the program

# Returns the lids position. Returns: fullyClosed, closedNotLocked, fullyOpen, moving
#def lidState():
#    fullyClosed     = 0
#    closedNotLocked = 0
#    fullyOpen       = 0
#    moving          = 0
#    for _ in range(10):
#        if lidStateSimple() == "fullyClosed":
#            fullyClosed += 1
#        elif lidStateSimple() == "closedNotLocked":
#            closedNotLocked += 1
#        elif lidStateSimple() == "fullyOpen":
#            fullyOpen += 1
#        else:
#            moving += 1
#        pyb.delay(1)

#    maxValue = max([fullyClosed, closedNotLocked, fullyOpen, moving])
#    if fullyClosed == maxValue:
#            return "fullyClosed"
#    elif closedNotLocked == maxValue:
#        return "closedNotLocked"
#    elif fullyOpen == maxValue:
#        return "fullyOpen"
#    else:
#        return "moving"

def lidState():
    # fully closed
    if (accel.x() >= fullyClosedX[0]        and accel.x() <= fullyClosedX[1])       and (accel.y() >= fullyClosedY[0]       and accel.y() <= fullyClosedY[1]):
        return "fullyClosed"
    # closed but not locked                                                                        
    if (accel.x() >= closedNotLockedX[0]    and accel.x() <= closedNotLockedX[1])   and (accel.y() >= closedNotLockedY[0]   and accel.y() <= closedNotLockedY[1]):
        return "closedNotLocked"
    # fully open                                                                                   
    if (accel.x() >= fullyOpenX[0]          and accel.x() <= fullyOpenX[1])         and (accel.y() >= fullyOpenY[0]         and accel.y() <= fullyOpenY[1]):
        return "fullyOpen"
    return "moving"


# movement of the fixture
# return:
#   0: error/did not execute as wished
#   1: finished/executed as intended
errorTime = 5 # seconds

# unlocks the fixture
def unlockLid():
    if lidState() != "fullyClosed":
        return 0
    passRelay50_x1.value(True)
    passRelay80_x3.value(False)
    cylinderRetract50_x2.value(True)
    temp = 0
    while (temp <= errorTime*1000) and (lidState() != "closedNotLocked"):
        temp += 1
        pyb.delay(1)
    if temp != errorTime*1000 + 1: # this means that lidState() == "closedNotLocked"
        cylinderRetract50_x2.value(True)
        cylinderRetract80_x4.value(False)
        passRelay50_x1.value(True)
        passRelay80_x3.value(False)
        return 1
    # if we end up here, lidState() != "closedNotLocked"
    cylinderRetract50_x2.value(False)
    cylinderRetract80_x4.value(False)
    passRelay50_x1.value(False)
    passRelay80_x3.value(False)
    return 0
            

# opens the fixture
def openLid():
    if lidState() != "closedNotLocked":
        return 0
    passRelay50_x1.value(True)
    passRelay80_x3.value(True)
    cylinderRetract50_x2.value(True)
    cylinderRetract80_x4.value(False)
    temp = 0
    while (temp <= errorTime*1000) and (lidState() != "fullyOpen"):
       temp += 1
       pyb.delay(1)
    if temp != errorTime*1000 + 1: # this means that lidState() == "fullyOpen"
        passRelay50_x1.value(False)
        passRelay80_x3.value(True)
        cylinderRetract50_x2.value(False)
        cylinderRetract80_x4.value(False)
        return 1
    # if we end up here, lidState() != "fullyOpen"
    passRelay50_x1.value(False)
    passRelay80_x3.value(False)
    cylinderRetract50_x2.value(False)
    cylinderRetract80_x4.value(False)
    return 0


# closes the fixture
def closeLid():
    if lidState() != "fullyOpen":
        return 0
    passRelay50_x1.value(True)
    passRelay80_x3.value(True)
    cylinderRetract50_x2.value(True)
    cylinderRetract80_x4.value(True)
    temp = 0
    while (temp <= errorTime*1000) and (lidState() != "closedNotLocked"):
       temp += 1
       pyb.delay(1)
    if temp != errorTime*1000 + 1: # this means that lidState() == "closedNotLocked"
        passRelay50_x1.value(True)
        passRelay80_x3.value(False)
        cylinderRetract50_x2.value(False)
        cylinderRetract80_x4.value(False)
        return 1
    # if we end up here, lidState() != "closedNotLocked"
    passRelay50_x1.value(False)
    passRelay80_x3.value(False)
    cylinderRetract50_x2.value(False)
    cylinderRetract80_x4.value(False)
    return 0

# locks the fixture
def lockLid():
    if lidState() != "closedNotLocked":
        return 0
    passRelay50_x1.value(True)
    passRelay80_x3.value(False)
    cylinderRetract50_x2.value(False)
    cylinderRetract80_x4.value(False)
    temp = 0
    while (temp <= errorTime*1000) and (lidState() != "fullyClosed"):
       temp += 1
       pyb.delay(1)
    if temp != errorTime*1000 + 1: # this means that lidState() == "fullyClosed"
        passRelay50_x1.value(False)
        passRelay80_x3.value(False)
        cylinderRetract50_x2.value(False)
        cylinderRetract80_x4.value(False)
        return 1
    # if we end up here, lidState() != "fullyClosed"
    passRelay50_x1.value(False)
    passRelay80_x3.value(False)
    cylinderRetract50_x2.value(False)
    cylinderRetract80_x4.value(False)
    return 0







while True:
    if dutFinished_x6.value() == 0:
        dutFinished_x6_Callback(dutFinished_x6)
    if closeLid_x7.value() == 0:
        closeLid_x7_Callback(closeLid_x7)
    if allLightsOff_x8.value() == 0:
        allLightsOff_x8_Callback(allLightsOff_x8)
    pyb.delay(10)




# Example of ext int block
#def myFunc_Callback(pin):
#    if not pinDebounce(pin):
#        # what should happen when the button is pressed?
#    elif pinDebounce(pin) == None:
#        # what should happen when the button is released?
#myBtn.irq(trigger = Pin.IRQ_FALLING, handler = myFunc_Callback)