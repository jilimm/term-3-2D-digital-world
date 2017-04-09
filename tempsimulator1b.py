# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 01:59:02 2017

@author: Jing Yun
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Apr 09 01:57:49 2017

@author: Jing Yun
"""
import time
import simpy
import libdw.sm as sm
env=simpy.Environment()
import simpy.rt
#Q=mc(delT), mc=40*4.184
#placeholder values
#self.Twater=43.0
#mc of the water
        
class WaterPumpSM(sm.SM):
    startState=1
    target=30.0
    diff2=0
    k1, k2 =15,-3
    #input is current value readings 
    def getNextValues(self, currentState, inp):
        if self.target>=inp:
            outp=(0.0,0.0)
            nextState=0 
        else:
            diff1=inp-self.target
            outp=(round(self.k1*diff1+self.k2*self.diff2,2),round(self.k1*diff1+self.k2*self.diff2,2))
            self.diff2=diff1
            nextState = 1
        return (nextState, outp)

pumpcontrol=WaterPumpSM()
pumpcontrol.start()
        
class TempSimul:
    def __init__(self,env):
        self.Tambient=25.0
        self.bottleSA=0.016
#TODO: this is a placeholder value
        self.bottle_conductivity=2.1
# i assume water is at 20 deg coz im a lazy lil bitch
#thermal conductivity k= 0.6
#d=hydraulic diameter=2mm=0.002
#viscosity=1002
#j= mass flux = 
#cp=isobaric heat capacity (J/g K)=4.1818
        
#TODO: this is a placeholdr value, lorem ipsum am i high?
        self.tubeSA=0.5
        self.airfreeconvec=10.0
        self.mcwater=40*4.184
        self.Si_conductivity=0.2
        self.Twater=simpy.Container(env, init=43.0)
        self.heat=simpy.Container(env, init=51572.0)
        self.tempdiff=self.Twater.level-self.Tambient
#TODO: mass flow rate is equivalent to the water pump output
#TODO: fix k1 and k2 so the power doesnt exceed 100
        self.mass_flux=pumpcontrol.step(self.Twater.level)[0]
        self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33

        print 'initial mass flux is {}'.format(self.mass_flux)
#        self.rad_proc=env.process(radiation(env))
#        self.bot_proc=env.process(bottleout(env))
#        self.Si_proc=env.process(siliconecond(env))
#        self.pump_proc=env.process(pumpconvec(env))
        self.monitor_stuff = env.process(self.monitor_stuff(env))
        
    def monitor_stuff(self,env):
        while True:
#somehow it doesnt matter if u put this on top or below i is bamboozled but i think top makes more sense
            yield env.timeout(1)
            ts.tempdiff=ts.Twater.level-ts.Tambient
            print 'diff is {} at {}'.format(self.tempdiff, env.now)
            ts.mass_flux=pumpcontrol.step(self.Twater.level)[0]
            self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33
            print 'mass flux is {} at {}'.format(self.mass_flux, env.now)
#somehow 

#TODO: make sure mass flux is in g per sec
        
#radiation from the sun        
def radiation(env, ts):
    while True:
        yield env.timeout(1)
        yield ts.heat.put(3)
        yield ts.Twater.put(3/ts.mcwater)
        print ('temp is now {}').format(ts.Twater.level)
        
#heat loss through the bottle
def bottleout(env, ts):
    while True:
        yield env.timeout(1)
        Qconvout=ts.airfreeconvec*ts.bottleSA*ts.tempdiff
        Qcondout=ts.bottle_conductivity*ts.tempdiff
        totalloss=Qconvout+Qcondout
        yield ts.heat.get(totalloss)
        print 'heat bottle'
        yield ts.Twater.get(totalloss/ts.mcwater)    
    
            
def siliconecond(env, ts):
    while True:
        yield env.timeout(1)
        Qout=ts.Si_conductivity*ts.tempdiff
        yield ts.heat.get(Qout)
        print 'heat Si'
        yield ts.Twater.get(Qout/ts.mcwater)

            
def pumpconvec(env, ts):
    while True:
        yield env.timeout(1)
        if ts.mass_flux==0:
            print 'o'
            pass
        else:
            Qpumpout=ts.tempdiff*ts.tubeSA*ts.waterconvcoeff
            yield ts.heat.get(Qpumpout)
#TODO: make sure self.mass flux updates every second
            print 'Q loss via conv'
            yield ts.Twater.get(Qpumpout/ts.mcwater)

        
env=simpy.Environment()
ts=TempSimul(env)
test_gen = env.process(radiation(env, ts))
test2_gen = env.process(pumpconvec(env, ts))
test3_gen = env.process(siliconecond(env, ts))
test4_gen = env.process(bottleout(env, ts))
env.run(until=6)