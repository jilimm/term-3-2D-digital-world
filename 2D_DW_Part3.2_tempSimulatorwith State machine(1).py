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
            outp=(round(self.k1*diff1+self.k2*self.diff2,2),round(self.k1*diff1+self.k2*self.diff2,2))
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
        
#TODO: this is a placeholdr value, lorem ipsum am i high?
        self.tubeSA=0.5
        self.airfreeconvec=10.0
        self.mcwater=40*4.184
        self.Si_conductivity=0.2
        self.Twater=simpy.Container(env, init=35.0)#thermometer
        self.heat=simpy.Container(env, init=51572.0)
# temp diff here is used for heat calculations so its between algae water and rt water.
        self.tempdiff=self.Twater.level-self.Tambient
#TODO: mass flow rate is equivalent to the water pump output
#TODO: fix k1 and k2 so the power doesnt exceed 100
        self.mass_flux=waterpumpcontrol.step(self.Twater.level)[0]
        self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33

        print 'initial mass flux is {}'.format(self.mass_flux)
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
            print 'diff is {} at {}'.format(self.tempdiff, env.now)
            ts.mass_flux=waterpumpcontrol.step(self.Twater.level)[0]
            self.waterconvcoeff=(0.6/0.02)*0.023*(self.mass_flux*0.02/1002)**0.8*(1002*4.1818/0.6)**0.33
            print 'mass flux is {} at {}'.format(self.mass_flux, env.now)

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
#Q loss by radiation        
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
#TODO: put free convec of air u lil biatch BAMBOOZLED!             
            print 'o'
            pass
        else:
            Qpumpout=ts.tempdiff*ts.tubeSA*ts.waterconvcoeff
            yield ts.heat.get(Qpumpout)
#TODO: make sure self.mass flux updates every second
            print 'Q loss via conv'
            yield ts.Twater.get(Qpumpout/ts.mcwater)

env=simpy.rt.RealtimeEnvironment(factor=1)
ts=TempSimul(env)        
test_gen = env.process(radiation(env, ts))
test2_gen = env.process(pumpconvec(env, ts))
test3_gen = env.process(siliconecond(env, ts))
test4_gen = env.process(bottleout(env, ts))
env.run()

#from kivy.app import App
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.label import Label
#from kivy.uix.button import Button
#from kivy.uix.gridlayout import GridLayout
#from kivy.uix.slider import Slider
#from kivy.uix.floatlayout import FloatLayout
#from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
#import libdw.sm as sm
#from kivy.clock import Clock
#from kivy.uix.widget import Widget
#import time
#import random
#
#
###raspberry pi screen 800 by 500 pixels.
#class WaterPumpSM(sm.SM):
#    startState=0
##create a attribute 'target' in the water pump SM class. 33.0 is just a placeholder value. target will be constantly updated in the call back function below to reflect the slider value. 
#    target=33.0
##we create an attribute diff2 which corresponds to the second error e(n-1). we will continually update this e(n-1) term everytime SM steps. diff 2 is 0 now because when the first input comes, the e(n-1) term is 0.
#    diff2=0
##define proportionality constnats
#    k1, k2 =15,-3
##error value is current (inp) - target
#    def getNextValues(self, currentState, inp):
##input is the current temperature (as decided by the slider)
#        if self.target>=inp:
#            outp=(0.0, 0.0)
#            nextState=0 
#        else:
#            #diff1 is e(n) which is dependent on the input. e(n) is difference between ur current inpupt and target
#            diff1=inp-self.target
#            #outp is rounded off to 2dp to prevent very long dp numbers
#            outp=(round(self.k1*diff1+self.k2*self.diff2,2), round(self.k1*diff1+self.k2*self.diff2,2))
#            #this line updates ur e(n-1) value. at the next step, your current e(n) value will be the e(n-1) value at the next step
#            self.diff2=diff1
#            nextState = 1
#        return (nextState, outp)
#    
#
#class GUIApp(App):
#    def __init__(self, **kwargs):
#        super(GUIApp, self).__init__(**kwargs)
#    
#    def build(self):
#        root = FloatLayout() 
##building temperature slide to set temp slider
#        self.target_slider = Slider(min=25.0, max=40.0, value=30.0)
#        def OnSliderValueChange(instance, value):
#            self.target_label.text=str(round(value,2))
##make sure value changes when u move the slider
#        self.target_slider.bind(value=OnSliderValueChange)
##make sure label changes with the slider
#        self.target_label=Label(text=str(self.target_slider.value))
#        
##put a label that will tell you the current temp 
#        self.current_label=Label(text=str(ts.Twater.level))
#        pumppower=ts.mass_flux
###the current temperature would be the input to the state machine 
##        inpreading=ts.Twater.level
###create an instance that links back to the waterpumpSM
##        self.waterpumpcontrol=WaterPumpSM()
###start the machine so that you can just input steps in next times
##        self.waterpumpcontrol.start()
###pass the current tempearture into the state machine
##        pumppower, fanpower = waterpumpcontrol.step(inpreading)
#        
##Setting up the overall layout for the app. the rows will be placed on top/below vertically
#        Tlayout=BoxLayout(orientation='vertical')
#        
## first row put the target temp
#        Row1=BoxLayout(orientation='horizontal')
#        Row1.add_widget(Label(text='Target Temperature'))
#        Row1.add_widget(self.target_label)
#        
## builing second row to put the current temp (temp simulator)
#        Row2=BoxLayout()
#        Row2.add_widget(self.target_slider)
#        
## third row will give u the current temperature
#        Row3=BoxLayout(orientation='horizontal')
#        Row3.add_widget(Label(text='Current Temperature'))
#        Row3.add_widget(self.current_label)
#        
##last row gives u the water pump power (controlled by PD)
#        Row5=BoxLayout(orientation='horizontal')
#        Row5.add_widget(Label(text='Water Pump Power'))
#        self.pumppower_label=Label(text=str(pumppower))
#        Row5.add_widget(self.pumppower_label)
#        
##last row gives me the fan power
#        Row6=BoxLayout(orientation='horizontal')
#        Row6.add_widget(Label(text='Fan Power'))
#        self.fanpower_label=Label(text='WIP')
#        Row6.add_widget(self.fanpower_label)
#        
##compile all rows together
#        Tlayout.add_widget(Row1)
#        Tlayout.add_widget(Row2)
#        Tlayout.add_widget(Row3)
#        #Tlayout.add_widget(Row4)
#        Tlayout.add_widget(Row5)
#        Tlayout.add_widget(Row6)
#        root.add_widget(Tlayout)
#        
##schedule an update every 0.1s so that you can update the values.   
#        Clock.schedule_interval(self.callback, 1)  
#        return root
#
##call back function calls back the simulator and GUI App to chech the target temperature and farm back current temperature        
#    def callback(self, instance):
## up date the target temperature in the waterpump state machin
#        waterpumpcontrol.target=self.target_slider.value
#        pumppower = ts.mass_flux
#        self.pumppower_label.text = str(pumppower)
#        print pumppower
#        
# # how to get GUI an env to run simultaneously?
# 
##from threading import Thread
##t1 = Thread(target = GUIApp())
##t2
#def fun1():
#    GUIApp().run()
#    
#def fun2():
#    env.run()
#    
#from multiprocessing import Process
#from multiprocessing import Pool
#import threading
#
#if __name__ == '__main__':
#    thread = threading.Thread()
#    thread.start_new_thread(env.run(),())
#    thread.start_new_thread(GUIApp().run(), ())
#    