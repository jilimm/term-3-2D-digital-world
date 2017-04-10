# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 01:59:02 2017

@author: Jing Yun
"""

import time
import simpy
import libdw.sm as sm
#env=simpy.Environment()
import simpy.rt
#Q=mc(delT), mc=40*4.184
#placeholder values
#self.Twater=43.0
#mc of the water
        
class WaterPumpSM(sm.SM):
    startState=0
    target=30.0
    diff2=0
    #TODO: k1 and k2 are placeholder values  should change
    k1, k2 =15,-3
    #input is current value readings 
    def getNextValues(self, currentState, inp):
        if self.target>=inp:
            outp=(0.0,0.0)
            nextState=0 
        else:
            diff1=inp-self.target
            outPower = max(round(self.k1*diff1+self.k2*self.diff2,2), 0) # Restrict to minimum of 0
            outp=(outPower,outPower)
            self.diff2=diff1
            nextState = 1
        return (nextState, outp)

waterpumpcontrol=WaterPumpSM()
waterpumpcontrol.start()
        
class TempSimul:
    def __init__(self,env):
        self.Tambient=25.0
        self.bottleSA=0.016
        #bottle conductivity value gained from experiments 
        self.bottle_conductivity=0.187
        # i assume water is at 20 deg coz im a lazy lil bitch
        #thermal conductivity k= 0.6
        #d=hydraulic diameter=2mm=0.002
        #viscosity=1002
        #j= mass flux = 
        #cp=isobaric heat capacity (J/g K)=4.1818
                
        #TODO: this is a placeholder value, lorem ipsum am i high?
        self.tubeSA=0.001
        self.airfreeconvec=10.0
        self.mcwater=40*4.184
        self.Si_conductivity=0.2
        self.Twater=simpy.Container(env, init=35.0)#thermometer
        self.heat=simpy.Container(env, init=51572.0)
        # temp diff here is used for heat calculations so its between algae water and rt water.
        self.tempdiff=self.Twater.level-self.Tambient
        #TODO: mass flow rate is equivalent to the water pump output
        #TODO: fix k1 and k2 so the power doesnt exceed 100
        self.mass_flux=(waterpumpcontrol.step(self.Twater.level)[0]/100.0) * 5
        self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33

        # print 'initial mass flux is {}'.format(self.mass_flux)
#        self.rad_proc=env.process(radiation(env))
#        self.bot_proc=env.process(bottleout(env))
#        self.Si_proc=env.process(siliconecond(env))
#        self.pump_proc=env.process(pumpconvec(env))
        self.monitor_stuff = env.process(self.monitor_stuff(env))
        
    def monitor_stuff(self,env):
#why i dont need while true? i is bamboozled
        while True:
            yield env.timeout(1)
            ts.tempdiff=ts.Twater.level-ts.Tambient
            # print 'diff is {} at {}'.format(self.tempdiff, env.now)
            ts.mass_flux=waterpumpcontrol.step(self.Twater.level)[0]
            self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33
            # print 'mass flux is {} at {}'.format(self.mass_flux, env.now)

#TODO: make sure mass flux is in g per sec
        
#radiation from the sun        
def radiation(env, ts):
    start_time = 3600 * 6
    time = start_time
    while True:
        yield env.timeout(1)

        # Ratio of the relative radiation at different times of the day
        # This is an estimatation with the radiation peaking at noon and decreasing over time
        heatRatio = [0, 0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.4, 0.6, 0.7, 1, 0.9, 0.8, 0.6, 0.4, 0.2, 0, 0, 0, 0, 0, 0]

        time += 1
        time %= 24 * 60 * 60 # Reset the time if the day rolls over

        hour = time//(3600)
        print hour
        rad = 3 * heatRatio[hour]

        # print "Time: " + str(time) + " Radiation: " + str(rad)

        if rad > 0:
            yield ts.heat.put(rad)
            yield ts.Twater.put(rad/ts.mcwater)
        print ('temp is now {}').format(ts.Twater.level)
        
#heat loss through the bottle
def bottleout(env, ts):
    while True:
        yield env.timeout(1)
        Qconvout=ts.airfreeconvec*ts.bottleSA*ts.tempdiff
        Qcondout=ts.bottle_conductivity*ts.tempdiff
#Q loss by radiation        
        totalloss=Qconvout+Qcondout
        yield ts.heat.get(totalloss)
        # print 'heat bottle'
        yield ts.Twater.get(totalloss/ts.mcwater)    
    
            
def siliconecond(env, ts):
    while True:
        yield env.timeout(1)
        Qout=ts.Si_conductivity*ts.tempdiff
        yield ts.heat.get(Qout)
        # print 'heat Si'
        yield ts.Twater.get(Qout/ts.mcwater)

            
def pumpconvec(env, ts):
    while True:
        yield env.timeout(1)
        if ts.mass_flux<=0:
#TODO: put free convec of air u lil biatch BAMBOOZLED!             
            # print 'o'
            pass
        else:
            Qpumpout=ts.tempdiff*ts.tubeSA*ts.waterconvcoeff
            yield ts.heat.get(Qpumpout)
#TODO: make sure self.mass flux updates every second
            # print 'Q loss via conv'
            yield ts.Twater.get(Qpumpout/ts.mcwater)

# def night_day_cycle(env, ts):
#     time = 0
#     while True:
#         yield env.timeout(1) # every hour
#         time += 1
#         time %= 24

#         print "Heat multiplier due to sun position " + str(ts.heatMultiplier.level)
#         if time > 9 and time < 17:
#             yield ts.heatMultiplier.put(0.1)
#         else:
#             yield ts.heatMultiplier.get(0.1)

env=simpy.rt.RealtimeEnvironment(factor=0.05)
ts=TempSimul(env)        
test_gen = env.process(radiation(env, ts))
test2_gen = env.process(pumpconvec(env, ts))
test3_gen = env.process(siliconecond(env, ts))
test4_gen = env.process(bottleout(env, ts))
# night_day = env.process(night_day_cycle(env, ts))
env.run()
