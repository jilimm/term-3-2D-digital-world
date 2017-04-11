'''
16 f09 2D digi world part 3.2 submission GROUP 6
LIM JING YUN
WU YUFEI
RYAN TEO
KOH JING YU
LIANG CHENYOU
'''

import time
import simpy
import libdw.sm as sm
import simpy.rt

from waterPumpSM import WaterPumpSM
import environmentProcesses

#Q=mc(delT), mc=40*4.184
#placeholder values
#self.Twater=43.0
#mc of the water

waterpumpcontrol=WaterPumpSM()
waterpumpcontrol.start()
        
class TempSimul:
    def __init__(self,env):
        self.Tambient=25.0

        # Surface area in contact with bottle - calculated in Physical World
        self.bottleSA=0.00632
        # Bottle conductivity value gained from Physical World experiments 
        self.bottle_conductivity=0.187

        #TODO: this is a placeholder value, lorem ipsum am i high?
        self.tubeSA=0.001
        self.airfreeconvec=10.0 # Free convection value of still air - from http://www.engineeringtoolbox.com/overall-heat-transfer-coefficient-d_434.html
        self.mcwater=40*4.184 # Heat capacity for 40 ml of water - https://water.usgs.gov/edu/heat-capacity.html
        self.si_res=0.06847 # Using thickness of the tube as 1.2mm and thermal conductivity from http://www.ioffe.ru/SVA/NSM/Semicond/Si/thermal.html, we calculate thermal resistance
        self.Twater=simpy.Container(env, init=35.0) # Initialize temperature of the algae water at 35 degrees

        # Temp difference between algae water and room temp water is used for heat calculations
        self.tempdiff=self.Twater.level-self.Tambient

        #TODO: mass flow rate is equivalent to the water pump output
        #TODO: fix k1 and k2 so the power doesnt exceed 100
        self.mass_flux=(waterpumpcontrol.step(self.Twater.level)[0]/100.0) * 5
        self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33
        self.waterfreeconvcoeff = 20.0

        # Keep track of power consumption of heat exchanger
        self.powerConsumption=simpy.Container(env, init=0)

        # Start an update process to continuously update temperature
        self.update = env.process(self.update(env))
        
    def update(self,env):
        ''' Continuously the attributes '''
        while True:
            yield env.timeout(1)
            ts.tempdiff=ts.Twater.level-ts.Tambient
            ts.mass_flux=waterpumpcontrol.step(self.Twater.level)[0]
            self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33

            # Output current temperature
            print ('Water temperature is now {}').format(ts.Twater.level)

# Create our RealtimeEnvironment for simulations
# Process definitions can be found in environmentProcesses.py
env=simpy.rt.RealtimeEnvironment(factor=0.05)
ts=TempSimul(env)
rad_process = env.process(environmentProcesses.radiation(env, ts))
conv_process = env.process(environmentProcesses.pumpconvec(env, ts))
cond_process = env.process(environmentProcesses.siliconecond(env, ts))
bottle_process = env.process(environmentProcesses.bottleout(env, ts))
power_process = env.process(environmentProcesses.powerconsumption(env, ts))
env.run()
