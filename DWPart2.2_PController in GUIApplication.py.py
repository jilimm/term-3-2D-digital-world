# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 11:20:28 2017

@author: Jing Yun
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
import libdw.sm as sm
from kivy.clock import Clock
from kivy.uix.widget import Widget
import time
import random

k1=10
k2=5

class WaterPumpSM(sm.SM):
    startState=0
#create a attribute 'target' in the water pump SM class. 33.0 is just a placeholder value. target will be constantly updated in the call back function below to reflect the slider value. 
    target=33.0
    def getNextValues(self, currentState, inp):
#input is the current temperature (as decided by the slider)
        if self.target>=inp:
            outp=(0.0, 0.0)
            nextState=0 
        else:
            diff=inp-self.target
            outp=(k1*diff, k1*diff)
            nextState = 1
        return (nextState, outp)
        
waterpumpcontrol=WaterPumpSM()
waterpumpcontrol.start()

class GUIApp(App):
    
    def __init__(self, **kwargs):
        super(GUIApp, self).__init__(**kwargs)
    
    def build(self):
        root = FloatLayout() 
#building temperature slide to set temp slider
        self.target_slider = Slider(min=30.0, max=35.0, value=30.0)
        def OnSliderValueChange(instance, value):
            self.target_label.text=str(round(value,2))
        self.target_slider.bind(value=OnSliderValueChange)
#put a label
        self.target_label=Label(text=str(self.target_slider.value))
        
#building a temperature simulator to set the current temperature        
        self.current_slider = Slider(min=25.0, max=43.0, value=35.0)
        def OnSliderValueChange1(instance, value):
            self.current_label.text=str(round(value,2))
        self.current_slider.bind(value=OnSliderValueChange1)
        
#put a label
        self.current_label=Label(text=str(self.current_slider.value))
#make an attribute that is like the value fo the slider
        self.currenttemp=self.current_slider.value
#the current temperature would be the input to the state machine 
        inpreading=self.currenttemp
#pass the current tempearture into the state machine
        pumppower, fanpower = waterpumpcontrol.step(inpreading)
        
#Setting up the overall layout for the app. the rows will be placed on top/below vertically
        Tlayout=BoxLayout(orientation='vertical')
        
# first row put the target temp
        Row1=BoxLayout(orientation='horizontal')
        Row1.add_widget(Label(text='Target Temperature'))
        Row1.add_widget(self.target_label)
        
# builing second row to put the current temp (temp simulator)
        Row2=BoxLayout()
        Row2.add_widget(self.target_slider)
        
# third row will give u the current temperature
        Row3=BoxLayout(orientation='horizontal')
        Row3.add_widget(Label(text='Current Temperature'))
        Row3.add_widget(self.current_label)
        
# builing second row to put the current temp (temp simulator)
        Row4=BoxLayout()
        Row4.add_widget(self.current_slider)
        
#last row gives u the water pump power (controlled by PD)
        Row5=BoxLayout(orientation='horizontal')
        Row5.add_widget(Label(text='Water Pump Power'))
        self.pumppower_label=Label(text=str(pumppower))
        Row5.add_widget(self.pumppower_label)
        
#last row gives me the fan power
        Row6=BoxLayout(orientation='horizontal')
        Row6.add_widget(Label(text='Fan Power'))
        self.fanpower_label=Label(text=str(fanpower))
        Row6.add_widget(self.fanpower_label)
        
#compile all rows together
        Tlayout.add_widget(Row1)
        Tlayout.add_widget(Row2)
        Tlayout.add_widget(Row3)
        Tlayout.add_widget(Row4)
        Tlayout.add_widget(Row5)
        Tlayout.add_widget(Row6)
        root.add_widget(Tlayout)
        
#schedule an update every 0.1s so that you can update the values.   
        Clock.schedule_interval(self.callback, 0.1)  
        return root

    def callback(self, instance):
# this updates the values 
        newinpreading = self.current_slider.value
# up date the target temperature in the waterpump state machin
        waterpumpcontrol.target=self.target_slider.value
        pumppower, fanpower = waterpumpcontrol.step(newinpreading)
        self.pumppower_label.text = str(pumppower)
        self.fanpower_label.text = str(fanpower)
        print pumppower
        
    
        
        
if __name__ == '__main__':
    GUIApp().run() 