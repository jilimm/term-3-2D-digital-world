# -*- coding: utf-8 -*-
"""
Created on Sun Apr 09 01:57:49 2017

@author: Jing Yun
"""
import time
import simpy
env=simpy.Environment()
import simpy.rt
#Q=mc(delT), mc=40*4.184
#placeholder values
#self.Twater=43.0
#mc of the water
        
        
class TempSimul:
    def __init__(self,env):
        self.Tambient=25.0
        self.bottleSA=0.016
#TODO: this is a placeholder value
        self.bottle_conductivity=2.1
#TODO: make mass flux in terms of output of state machine
#TODO: this is a placeholder value, lorem ipsum. what a scrub\
#TODO: make sure mass flux is in g per sec
        self.mass_flux=0.5
# i assume water is at 20 deg coz im a lazy lil bitch
#thermal conductivity k= 0.6
#d=hydraulic diameter=2mm=0.002
#viscosity=1002
#j= mass flux = 
#cp=isobaric heat capacity (J/g K)=4.1818
        self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33
#TODO: this is a placeholdr value, lorem ipsum am i high?
        self.tubeSA=0.5
        self.airfreeconvec=10.0
        self.mcwater=40*4.184
        self.Si_conductivity=0.2
        self.Twater=simpy.Container(env, init=43.0)
        self.heat=simpy.Container(env, init=51572.0)
        self.tempdiff=self.Twater.level-self.Tambient
        self.rad_proc=env.process(self.radiation(env))
        self.bot_proc=env.process(self.bottleout(env))
        self.Si_proc=env.process(self.siliconecond(env))
        self.pump_proc=env.process(self.pumpconvec(env))
#radiation from the sun        
    def radiation(self, env):
        while True:
             yield env.timeout(1)
             yield ts.heat.get(3)
             yield ts.Twater.put(3/ts.mcwater)
             print ('temp is now {}').format(ts.Twater.level)      
        
#heat loss through the bottle
    def bottleout(self, env):
        while True:
            yield env.timeout(1)
            Qconvout=ts.airfreeconvec*ts.bottleSA*ts.tempdiff
            Qcondout=ts.bottle_conductivity*ts.tempdiff
            totalloss=Qconvout+Qcondout
            yield ts.heat.get(totalloss)
            yield ts.Twater.get(totalloss/ts.mcwater)
        
    def siliconecond(self, env):
        while True:
            yield env.timeout(1)
            Qout=ts.Si_conductivity*ts.tempdiff
            yield ts.heat.get(Qout)
            yield ts.Twater.get(Qout/ts.mcwater)
        
    def pumpconvec(self, env):
        while True:
            yield env.timeout(1)
            Qpumpout=ts.tempdiff*ts.tubeSA*ts.waterconvcoeff
            yield ts.heat.get(Qpumpout)
            yield ts.Twater.get(Qpumpout/ts.mcwater)
       
        
env=simpy.Environment()
ts=TempSimul(env)
env.run(until=5)