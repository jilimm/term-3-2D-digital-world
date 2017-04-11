# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 07:21:53 2017

@author: Jing Yun
"""


import serial
import time
import libdw.sm as sm

class WaterPumpSM(sm.SM):
    startState=0
    target=30.0
    diff2=0
#k1 and k2 obtained through experimentations
    k1, k2 =11,-4
#input is current temperature readings 
    def getNextValues(self, currentState, inp):
        if self.target>=inp:
            outp=(0.0,0.0)
            nextState=0 
        else:
#e(n) is the difference between target and current input
            diff1=inp-self.target
#implementing pd here so power is k1e(n)-k2e(n-1). /100 to ensure its a fraction from 0 to 1.0
            outPower = max(round((self.k1*diff1+self.k2*self.diff2)/100.0,5), 0) # Restrict to minimum of 0
#output will be tuple 
            outp=(outPower,outPower)
#shift current e(n) to be the e(n-1) in the next state
            self.diff2=diff1
            nextState = 1
        if outp[0]>1.0:
            outp=(1.0,1.0)
        else:
            outp=outp
        return (nextState, outp)

#starting water pump SM so i can step it later
waterpumpcontrol=WaterPumpSM()
waterpumpcontrol.start()

#create my serial instance
Rpi=serial.Serial()
#according to my raspberry pi, I configure the serial port created
Rpi.port='/dev/ttyAMA0'
Rpi.baudrate = 9600
Rpi.parity=serial.PARITY_NONE
Rpi.stopbits=serial.STOPBITS_ONE
Rpi.bytesize=serial.EIGHTBITS
#time out of 1 to allow program to receive input only every 1 sec
Rpi.timeout=1
#open serial port so you can receive things
Rpi.open()

while True:
    #serial port will continuously read data sent to it
    x=Rpi.readline()
    if x=='':
# is the simulator does not send any data, 'no input' is printed, the serial port tries chekcing for data 1 sec later
        print 'no input'
        time.sleep(1)
    else:
        pumppower, fanpower = waterpumpcontrol.step(float(x))
#output the pumppower determined by state machine to the simulator in the computer
        Rpi.write(str(pumppower)+'\n')
