# term-3-2D-digital-world
2D digital world Part 1

'''
16 f09 2D digi world part 1 submission GROUP 6
LIM JING YUN
WU YUFEI
RYAN TEO
KOH JING YU
LIANG CHENYOU
'''

import libdw.sm as sm
import RPi.GPIO as GPIO
import os
import glob
import time

GPIO.setmode(GPIO.BCM)

in2pin = 26
in1pin = 17
en = 18

target=30
#target temp is 30

GPIO.setup(en, GPIO.OUT)
GPIO.setup(in2pin, GPIO.OUT)
GPIO.setup(in1pin, GPIO.OUT)
#set all pins connected to the IR to be out. Becuase everything is coming out of the rapsberry pi 

GPIO.output(en, GPIO.HIGH)
#set en to be high so it can receive stuff from the rtaspberry pi

p1 = GPIO.PWM(in1pin, 300)
#freqeuncy value obtained through experiments with water pump

#temperature code copied from online. This uses the probe to read temperature
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
#this function is the main function that outputs temperature
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c
# we changed the output to just temp_c so it only returns temperature in terms of degrees Celcius. becuase we dont need temperature in temrs of farenheit


#this is the state machine required of us by the 2D project. 
class WaterPumpSM(sm.SM):
    startState=0
    def getNextValues(self, currentState, inp):
        # if input temp is lower than target, its at state 0 which is pump off
        if inp<target:
            nextState=0 
        else:
            # if input if higher then it will be at state 1 where pump is on at 100%
            nextState=1 
        if currentState==0:
            #at this current State, the pump always be off
            if nextState == 1:
                #if the next State is 1 the state machine moves to state1 and pump turns on
                #else the state remains at 0 and remains off
                p1.start(100)
                #make water pump on at 100% power
            outp=(0.0, 0.0) 
            #tuple of power ouptput of water pump and 'fan'
                
        elif currentState==1:
            #if the current state is 1 then the pump turns on (see above)
            if nextState == 0:
                #pump will remain on until the next state is 0.
                p1.stop()
            outp=(1.0, 1.0) 
            #tuple of power ouptput of water pump and 'fan'

        return (nextState, outp)
        #the state machine will output a tuple
    
waterPumpControl=WaterPumpSM()
waterPumpControl.start()

while True: 
#This while loop continuously check temperature and actuate water pump
    waterPumpControl.step(read_temp())
    # the input to the state machine is the temp measured by the thermometer probe
GPIO.cleanup() #clean up GPIO so you can do other things
