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

in2pin = 5
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
        return temp_c
# we changed the output to just temp_c so it only returns temperature in terms of degrees Celcius. becuase we dont need temperature in temrs of farenheit


#this is the state machine required of us by the 2D project. 
class WaterPumpSM(sm.SM):
    startState=0
    def getNextValues(self, currentState, inp):
        if inp<=target:
# state machine will change state depending on temperature sensed. State0 corresponds to stopping pump. State 1 corresponds to putting pump to 100% 
            outp=(0.0, 0.0)
            #tuple output of (0.0, 0.0) will make pump stop
            nextState=0 
        else:
            outp=(1.0, 1.0)
            #this tuple output will be used to make the pump go at 100%power
            nextState = 1
        return (nextState, outp)
        #the state machine will output a tuple
    
###Enter fan code here when physical world provides a fan###

waterPumpControl=WaterPumpSM()
#start the state machine
waterPumpControl.start()
#start the water pump. DC here is 0 because we are 
p1.start(0)

#while loop below continously reads temperature of surrounding and actuates pump based on input temperature
while True:
    PumpPower, FanPower = waterPumpControl.step(read_temp())
    p1.ChangeDutyCycle(PumpPower*100)
    time.sleep(1)

p1.stop()
#stop the pump once code exits the while loop
GPIO.cleanup()
#clean up the GPIO so you can do other stuff
    
    



            





            


