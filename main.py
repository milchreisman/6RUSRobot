from sixRUS import sixRUS
import time
import controller as con
import RPi.GPIO as GPIO
import demo 
import types
import random

from threading import Timer, Event

# GLOBALS
programStopped = Event()  # Event to set if program gets
shouldNotListen2Cont = Event()  # Event for checking if the program should listen to the Controller
robotMode = ''
joystick = None
# joy = None  # global varriable for joystick-class


def call_every_5_sec():
    """execute everything in here every 5 seconds after"""
    if not programStopped.is_set():  # only execute routine if program is not terminated

        # Do the things we want to every so often  #TODO: explain connection to controller
        ans = con.stillConnected()
        if ans == False:
            print('controller not connected')    
        else:
            # print('connected')
            pass

        init_global_joystick()  # (try to) init controller

        Timer(5.0, call_every_5_sec).start()

def call_every_tenth_sec():
    # TODO: add discription
    if not programStopped.is_set() and not shouldNotListen2Cont.is_set():  # only execute routine if program is not terminated

        global joystick
        ans = con.listen2Cont(joystick)

        eval_controller_response(ans)  # evaluate the answer from controller

        Timer(0.1, call_every_tenth_sec).start()

def init_global_joystick():
    # TODO: discription

    global joystick
    joystick = con.initCont()


def eval_controller_response(response):
    """evaluates the answer from the listen2Cont-function"""
    if isinstance(response, str):
        # controller gave an answer

        global robotMode

        if response == 'stop':
            pass
        elif response == 'homing':
            pass
        elif response == 'demo':
            pass
        elif response == 'manual':
            pass
        else:
            raise Exception("Unknown answer from controller")
        print(response)
        robotMode = response  # set robot mode to the response
    else:
        # controller has given a pose
        pass
        
    

# Main program
def main():
    global robotMode
    robotMode = 'manual'  # current mode (check documentation for all possible modes)

    robo = sixRUS(stepperMode=1/32, stepDelay=0.002)

    robo.homing('90')

    init_global_joystick()

    startListening2Cont()  # start listening to controller

    

    while True:  # infinite loop only breaks on Keyboard-Interrupt
        # time.sleep(0.5)
        while robotMode == 'demo':  # TODO
            pass

        while robotMode == 'homing':
            stopListening2Cont()  # stop listening to controller to prevent program change while homing
            time.sleep(0.2)
            robo.homing('90')  # use homing method '90'
            startListening2Cont()  # listen again
            robotMode = 'stop'  # exit homing

        while robotMode == 'manual':
            mov_with_controller(robo)

        while robotMode == 'stop':  # TODO
            # time.sleep(0.001)
            pass

def startListening2Cont():
    global shouldNotListen2Cont
    shouldNotListen2Cont.clear()
    Timer(0.1, call_every_tenth_sec).start()

def stopListening2Cont():
    global shouldNotListen2Cont
    shouldNotListen2Cont.set()


def mov_with_controller(robot, dt=0.1, scale=1):
    """""" # TODO: enter discription

    stopListening2Cont()  # stop listening to controller (bc. we listen all the time in here)

    ans = ''
    global joystick

    while True:  # infinite loop
        time.sleep(dt)
        ans = con.listen2Cont(joystick, robot.currPose)

        if isinstance(ans, str):  # string was given as an answer

            eval_controller_response(ans)
            
            break  # break out of infinite loop

        else:  # pose was given as an answer
            # print([round(n, 3) for n in ans])
            robot.mov(ans)

    startListening2Cont()  # let the program listen to the controller periodically again


def move_with_demo(robot):
    """Function to select a demo programm and execute it
    """
    modules = list_of_modules(demo)
    Prog = random.choice(modules)
    demoPosList = Prog()

    for pos in demoPosList:
        if pos[6] == 'lin':
            coord = pos[:6]
            robot.mov(coord)

        if pos[6] == 'mov':
            coord = pos[:6]
            robot.mov(coord)


def list_of_modules(packageName):
    """Function to find all modules in a package 
    `packageName`: Name of package
    `return`: List of all modules in this package
    """
    modulList = []
    for a in dir(demo):
        if isinstance(getattr(demo, a), types.FunctionType):
            modulList.append(getattr(demo,a))

    return modulList

# Main program if this file get executed

if __name__ == '__main__':

    Timer(5.0, call_every_5_sec).start()  # call subroutine every n-seconds

    try:
        main()
    except KeyboardInterrupt:  # shutdown python program gently
        GPIO.cleanup()  # cleanup GPIOs (to avoid warning on next startup)
        programStopped.set()  # set event for stopping interrupt

        # Exiting message
        print("6-RUS program was terminated by Keyboard-Interrupt. (Please wait ca. 5s) \nPlease start the program again to control the robot again!")
