# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 03:42:26 2017

@author: Jing Yun
"""

import serial
import simpy
import libdw.sm as sm
#env=simpy.Environment()
import simpy.rt

#create a pyserial instance
com=serial.Serial()
# open port where my USB serial is attached
com.port='COM6'
#configure my port
com.baudrate = 9600
com.parity=serial.PARITY_NONE
com.stopbits=serial.STOPBITS_ONE
com.bytesize=serial.EIGHTBITS
#timeout allows will only receive data every 1 second
com.timeout=1
#open the port so we cna use it to read/write data
com.open()

        

        
class TempSimul:
    def __init__(self,env):
        self.Tambient=25.0
#temperature is a container. it acts like thermometer keeping track of the algae water temperature
        self.Twater=simpy.Container(env, init=35.0)
#Container for power consumption so you can keep track of power given to the pump
        self.PowerConsumption=simpy.Container(env, init=0)
#this is the initial value of mass_flux (mass velocity), it will be updated later as the simulation goes on. at t=0 the ass flux will be 0 because it takes some time for the water to flow through tube
        self.mass_flux=0.0
# temp difference between algae water and ambient temp. this value would be updated every second as temperature changes
        self.tempdiff=self.Twater.level-self.Tambient
#send the intitial temperature to the state machine. this will start the serial commuincation loop between simulator and state machine.
        com.write('{}'.format(self.Twater.level))
#convection coefficient of water is dependent on mass flux (velocity) of water in pump. This value will be updated later as temperature changes and controller changes mass flux.
        self.waterforcedconvcoeff=900*self.mass_flux
        
#start the monitor_temp function as process so changing values in ts are constantly updated.
        self.monitor_stuff = env.process(self.monitor_temp(env))
    
#this function constantly updates variables mentioend above.
    def monitor_temp(self,env):
        while True:
            yield env.timeout(1)
            ts.tempdiff=ts.Twater.level-ts.Tambient
            ts.waterforcedconvcoeff=900*ts.mass_flux
            ts.significantforcedconv=0.001885*900*ts.mass_flux
  
        
#heat gain from radiation from the sun        
def radiation(env, ts):
#TODO: jing yu to comment?
    start_time = 3600 * 6 
    time = start_time
    while True:
        yield env.timeout(1)

        # Ratio of the relative radiation at different hours of the day beginning with midnight
        # This is an estimatation with the radiation peaking at noon and decreasing over time
        heatRatio = [0, 0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.4, 0.6, 0.7, 1, 0.9, 0.8, 0.6, 0.4, 0.2, 0, 0, 0, 0, 0, 0]

        time += 1
        time %= 24 * 60 * 60 # Reset the time if the day rolls over

        hour = time//(3600)
        print 'radiation'
        rad = 3 * heatRatio[hour]

        if rad > 0:
            yield ts.Twater.put(rad/167.36)
        print ('temp is now {}').format(ts.Twater.level)
        
#heat loss through the bottle due to conduction and convection (free convection between bottle and air)
def bottleout(env, ts):
    while True:
        print 'bottleout'
#temperature would only drop 1 sec after experiment
        yield env.timeout(1)
#Q convection = free convection coeff* surfaec area of bottle * del temp
        Qconvout=10.0*0.016*ts.tempdiff
# Q conduction = bottle conductivity (determined from PW section) * del Temp
        Qcondout=0.147*ts.tempdiff
        totalloss=Qconvout+Qcondout
# Q=mc(delT). so temp drop = total Q lost / mc of water
        yield ts.Twater.get(totalloss/167.36)    

#heat lost due to the tubing and flowing water. Q lost = (1/effective thermal resistance) * del Temp
def Qlostpipes(env, ts):
    while True:
        yield env.timeout(1)
#if the velocity of water is insignificant (0.1) or even 0. water will stay in pump so heat is lost to water via free convection. 
#or statement ensures that in the forced conv calculations there will not be a division by 0
        if ts.mass_flux<=0.1 or 0.001885*float(ts.waterforcedconvcoeff)<=0:
            print 'free convec'
            print float(0.001885*float(ts.waterforcedconvcoeff))
#thermal resistance of water (when not flowing). (1/hA). inner diameter of tubes=2mm. A(area of inner tube)=0.001885 and h=20. thermal resistance of water=26.5
#thermal resistance of Silicone tubing (t/kA). Si is 1mm thick an outer diameter of 4mm. 30cm of pipe is submerged in water. tubes have inner area os 0.001885. thermal R of Si=0.001/(0.20*0.00377). thermal resistance of silicone = 1.32626
#total heat exchange= del TEmp/ total thermal resistance
            Qpumpout=float(ts.tempdiff)/float(1.32626+26.5)
# temperature drop = heat exchanged/m*c
            yield ts.Twater.get(Qpumpout/167.36)
#when velocity of water is significant, convection coeff of water is forced convection coefficient and is dependent on velocity 
        else:
            print 'FORCEDD'
# thermal resistance of water = 1/hA
            thermalRofwater=float(1.00/(0.001885*float(ts.waterforcedconvcoeff)))
#thermal resistance of Silicone tubing
            thermalRofSi=1.32626
            Rtotal=float(thermalRofwater+thermalRofSi)
            Qpumpout=float(ts.tempdiff)/Rtotal
            yield ts.Twater.get(Qpumpout/167.36)

# this function continuously sends and receives data from controller.         
def writing_reading(env,ts):
    while True:
        yield env.timeout(1)
# reading output of controller. output is the power of the pump 
        y=com.readline()
#this if loop deals with what would happen if the pump is not on. the receiver port would wait for 1 sec, set the velocity of water to be 0 and continuously feed the current algae temperature to the controller.  
        if y=='':
            print 'pump is not connected'
            yield env.timeout(1)
            ts.mass_flux=0
            com.write('{}'.format(ts.Twater.level))
#this loop happens when pump is switched on
        else:
            print 'pump is on'
# the received input would be the velocity of water
            ts.mass_flux=float(y)
#update pump about the current algae temperature
            com.write('{}'.format(ts.Twater.level))
        
 
        

 #run the simulation in real time so 1 unit of time in env=1sec   
env=simpy.rt.RealtimeEnvironment(factor=1.1)
ts=TempSimul(env) 
#start all the functions as processes   
rad_gen = env.process(radiation(env, ts))
tubing_gen = env.process(Qlostpipes(env, ts))
bottle_gen = env.process(bottleout(env, ts))
update_gen = env.process(writing_reading(env,ts))
#run the environment
env.run()
