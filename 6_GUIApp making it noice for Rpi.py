# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 16:19:46 2017

@author: Jing Yun
"""

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
from kivy.core.window import Window
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout

#raspberry pi screen 800 by 500 pixels.
class WaterPumpSM(sm.SM):
    startState=0
#create a attribute 'target' in the water pump SM class. 33.0 is just a placeholder value. target will be constantly updated in the call back function below to reflect the slider value. 
    target=33.0
#we create an attribute diff2 which corresponds to the second error e(n-1). we will continually update this e(n-1) term everytime SM steps. diff 2 is 0 now because when the first input comes, the e(n-1) term is 0.
    diff2=0
#TODO: actual proprtionality constant 
    k1, k2 =15,-3
#error value is current (inp) - target
    def getNextValues(self, currentState, inp):
#input is the current temperature (as decided by the slider)
        if self.target>=inp:
            outp=(0.0, 0.0)
            nextState=0 
        else:
            #diff1 is e(n) which is dependent on the input. e(n) is difference between ur current inpupt and target
            diff1=inp-self.target
            #outp is rounded off to 2dp to prevent very long dp numbers
            outp=(round(self.k1*diff1+self.k2*self.diff2,2), round(self.k1*diff1+self.k2*self.diff2,2))
            #this line updates ur e(n-1) value. at the next step, your current e(n) value will be the e(n-1) value at the next step
            self.diff2=diff1
            nextState = 1
        return (nextState, outp)
        
#TODO: test code to make the bakcground img
class RootWidget(BoxLayout):
    pass

class CustomLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(CustomLayout, self).__init__(**kwargs)
        
        with self.canvas.before:
            self.rect=Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        

        
class GUIApp(App):
    def __init__(self, **kwargs):
        super(GUIApp, self).__init__(**kwargs)
    
    def build(self):
        root = RootWidget() 
        c= CustomLayout()
        
#building temperature slide to set temp slider
        self.target_slider = Slider(min=25.0, max=40.0, value=30.0, orientation='vertical', background_width=20, size_hint_x=0.5)
        def OnSliderValueChange(instance, value):
            self.target_label.text=str(round(value,2))
        self.target_slider.bind(value=OnSliderValueChange)
#put a label
        self.target_label=Label(text=str(self.target_slider.value), color=[0,0,0,1])
        
#building a temperature simulator to set the current temperature        
        self.current_slider = Slider(min=25.0, max=40.0, value=35.0, orientation='vertical', backgroun_width=20, size_hint_x=0.5)
        def OnSliderValueChange1(instance, value):
            self.current_label.text=str(round(value,2))
        self.current_slider.bind(value=OnSliderValueChange1)
        
#put a label
        self.current_label=Label(text=str(self.current_slider.value),color=[0,0,0,1])
#make an attribute that is like the value fo the slider
        self.currenttemp=self.current_slider.value
#the current temperature would be the input to the state machine 
        inpreading=self.currenttemp
#create an instance that links back to the waterpumpSM
        self.waterpumpcontrol=WaterPumpSM()
#start the machine so that you can just input steps in next times
        self.waterpumpcontrol.start()
#pass the current tempearture into the state machine
        pumppower, fanpower = self.waterpumpcontrol.step(inpreading)
        
#Setting up the overall layout for the app. the rows will be placed on top/below vertically
        Tlayout=GridLayout(cols=2, rows=2)
        #Tlayout=BoxLayout(orientation='vertical')
        
#adding the background wall paper
#TODO: make sure the background is purely colour then u add in the icons and the slidesr separately.
        root.add_widget(c)
        c.add_widget(AsyncImage(source="http://server.myspace-shack.com/d22/gui asthetic interface look with texts and sliders.png"))
        
# first row put the target temp
        Quad1=BoxLayout(orientation='vertical')
#specify that row 1 is like 70% of the quadrant
        Q1row1=AnchorLayout(anchor_x='right')
        Q1row1.add_widget(self.target_slider)
        Q1row1.add_widget(Label(text=''))
        Quad1.add_widget(Q1row1)
        Q1row2=BoxLayout(orientation='horizontal', size_hint_y=0.20)
        Q1row2.add_widget(Label(text='Target Temperature', color=[0,0,0,1]))
        Q1row2.add_widget(self.target_label)
        Quad1.add_widget(Q1row2)
 
        Quad2=BoxLayout(orientation='vertical')
        Q2row1=AnchorLayout(anchor_x='right')
        Q2row1.add_widget(self.current_slider)
        Quad2.add_widget(Q2row1)
        Q2row2=BoxLayout(orientation='horizontal', size_hint_y=0.20)
        Q2row2.add_widget(Label(text='Current Temperature', color=[0,0,0,1]))
        Q2row2.add_widget(self.current_label)
        Quad2.add_widget(Q2row2)
        
        self.pumppower_label=Label(text=str(pumppower),color=[0,0,0,1], size_hint_x=0.5, font_size=40)
        Quad3=BoxLayout(orientation='vertical')
        Q3row1=AnchorLayout(anchor_x='right')
        Q3row1.add_widget(self.pumppower_label)
        Quad3.add_widget(Q3row1)
        Q3row2=BoxLayout(orientation='horizontal', size_hint_y=0.20, size_hint_x=0.5)
        Q3row2.add_widget(Label(text='Water Pump Power', color=[0,0,0,1], font_size=15, size_hint_x=0.5))
        Quad3.add_widget(Q3row2)
        
        self.fanpower_label=Label(text=str(fanpower),color=[0,0,0,1], size_hint_x=0.5, font_size=40)
        Quad4=BoxLayout(orientation='vertical')
        Q4row1=AnchorLayout(anchor_x='right')
        Q4row1.add_widget(self.fanpower_label)
        Quad4.add_widget(Q4row1)
        Q4row2=BoxLayout(orientation='horizontal', size_hint_y=0.20, size_hint_x=0.5)
        Q4row2.add_widget(Label(text='Fan Power', color=[0,0,0,1], font_size=15, size_hint_x=0.5))
        Quad4.add_widget(Q4row2)
        
        Tlayout.add_widget(Quad1)
        Tlayout.add_widget(Quad2)
        Tlayout.add_widget(Quad3)
        Tlayout.add_widget(Quad4)
        #Tlayout.add_widget(Row2)
#        Tlayout.add_widget(Row3)
#        Tlayout.add_widget(Row4)
#        Tlayout.add_widget(Row5)
#        Tlayout.add_widget(Row6)
## I add the layout of the widgets to the back ground (custom background)
        c.add_widget(Tlayout)
        
#schedule an update every 0.1s so that you can update the values.   
        Clock.schedule_interval(self.callback, 0.1)  
        return root

        
    def callback(self, instance):
# this updates the values
        newinpreading = self.current_slider.value
# up date the target temperature in the waterpump state machin
        self.waterpumpcontrol.target=self.target_slider.value
        pumppower, fanpower = self.waterpumpcontrol.step(newinpreading)
        self.pumppower_label.text = str(pumppower)
        self.fanpower_label.text = str(fanpower)
        print pumppower
        
Window.size = (800,500)  
        
        
if __name__ == '__main__':
    GUIApp().run() 