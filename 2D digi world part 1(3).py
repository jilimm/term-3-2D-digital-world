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

#naming the pins we connected to in our set up 

in2pin = 5
in1pin = 17
en = 18

#target temp is 30
target=30

#set all pins connected to the IR to be out. Becuase everything is coming out of the rapsberry pi
GPIO.setup(en, GPIO.OUT)
GPIO.setup(in2pin, GPIO.OUT)
GPIO.setup(in1pin, GPIO.OUT) 

#set en to be high so it can receive stuff from the rtaspberry pi
GPIO.output(en, GPIO.HIGH)

#freqeuncy value obtained through experiments with water pump
p1 = GPIO.PWM(in1pin, 300)

#temperature code copied from online. This uses the probe to measure surrounding temperature
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
# output is changed to only temp_c becuase we are only concerned with temperature in degrees Celsius. 
        return temp_c
#this is the state machine required of us by the 2D project. 
class WaterPumpSM(sm.SM):
    startState=0
    def getNextValues(self, currentState, inp):
# state machine will change state depending on temperature sensed. State0 corresponds to stopping pump. State 1 corresponds to putting pump to 100% 
        if inp<=target:
            #tuple output of (0.0, 0.0) will be used to make pump stop
            outp=(0.0, 0.0)
            nextState=0 
        else:
            #tuple output of (1.0, 1.0) will be used to make poump go at 100% power
            outp=(1.0, 1.0)
            nextState = 1
        #the state machine will output a tuple    
        return (nextState, outp)
        
    
###Enter fan code here when physical world provides a fan###



waterPumpControl=WaterPumpSM()
#start the state machine
waterPumpControl.start()
#start the water pump. DC here is 0 because we are not sure of the input temperature
p1.start(0)

#while loop below continously reads temperature of surrounding and actuates pump based on input temperature
while True:
    PumpPower, FanPower = waterPumpControl.step(read_temp())
    p1.ChangeDutyCycle(PumpPower*100)
    #pause for 1 second to let the pump run before it gets a new instruction. 
    time.sleep(1)

# stop pump once we are done
p1.stop()
#clean up the GPIO so you can do other stuff
GPIO.cleanup()

    
    



            





            


