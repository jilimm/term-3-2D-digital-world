'''
16 f09 2D digi world part 2.2 submission GROUP 6
LIM JING YUN
WU YUFEI
RYAN TEO
KOH JING YU
LIANG CHENYOU
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty

from kivy.clock import Clock
from kivy.uix.widget import Widget
import time
import random
from kivy.core.window import Window
from kivy.uix.image import AsyncImage, Image
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout

from waterPumpSM import WaterPumpSM

# Custom class for background image
class RootWidget(BoxLayout):
    pass

# Custom class for background image purposes
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
    ''' Main Kivy app '''
    def __init__(self, **kwargs):
        super(GUIApp, self).__init__(**kwargs)
    
    def OnSliderValueChange(self, instance, value):
        self.target_label.text=str(round(value,2))

    def OnSliderValueChange1(self, instance, value):
        self.current_label.text=str(round(value,2))

    def build(self):
        root = RootWidget() 
        c= CustomLayout()
        
        #building temperature slider for setting temp slider
        self.target_slider = Slider(min=25, max=40.0, value=30.0, orientation='vertical', size_hint_x=0.5)
        self.target_slider.bind(value=self.OnSliderValueChange)
        # Label for target temperature
        self.target_label=Label(text=str(self.target_slider.value), color=[0,0,0,1], font_size=18)
        
        #building a temperature simulator to set the current temperature        
        self.current_slider = Slider(min=25.0, max=40.0, value=35.0, orientation='vertical', size_hint_x=0.5)
        self.current_slider.bind(value=self.OnSliderValueChange1)
        
        # Label for current temperature
        self.current_label=Label(text=str(self.current_slider.value),color=[0,0,0,1], font_size=18)
        self.currenttemp=self.current_slider.value

        #the current temperature would be the input to the state machine 
        inpreading=self.currenttemp
        #create an instance that links back to the waterpumpSM
        self.waterpumpcontrol=WaterPumpSM()
        #start the machine so that you can just input steps in next times
        self.waterpumpcontrol.start()
        #pass the current tempearture into the state machine the outputs are put in terms of percentages so it is easier to read
        pumppower, fanpower = self.waterpumpcontrol.step(inpreading)[0]*100, self.waterpumpcontrol.step(inpreading)[1]*100

        #Setting up the overall layout for the app. the rows will be placed on top/below vertically
        Tlayout=GridLayout(cols=2, rows=2)
        
        #adding the background wall paper
        root.add_widget(c)
        c.add_widget(Image(source="2D GUI (1).png"))
        
        #first quadrant is a vertical boxlayout so widgets are added form top to bottom
        Quad1=BoxLayout(orientation='vertical')
        #first row of Quad1 is anchor layout, anchor_x='right' so all widgets added to this row would be aligned to the right of the layout. this is done to leave space for the icon in the background
        Q1row1=AnchorLayout(anchor_x='right')
        #add slider to the first row of Q1
        Q1row1.add_widget(self.target_slider)
        #add the row to the top of the quadrant
        Quad1.add_widget(Q1row1)
        # second row of Quadrant 1 is a horizontal box layout so widgets are added from left to right. size_hint_y means this second row would be 31.5% of the height of quadrant 1, thus row 1  would be 69.5 percent of the height of quadrant 1
        Q1row2=BoxLayout(orientation='horizontal', size_hint_y=0.315)
        # Add a label with text target temperature
        Q1row2.add_widget(Label(text='Target Temperature', color=[0,0,0,1], font_size=18))
        # add a label whose text will displat the numerical value of the target temperature
        Q1row2.add_widget(self.target_label)
        #add the second row to the quadrant and quadrant is complete
        Quad1.add_widget(Q1row2)
        
        #same logic applies    
        Quad2=BoxLayout(orientation='vertical')
        Q2row1=AnchorLayout(anchor_x='right')
        Q2row1.add_widget(self.current_slider)
        Quad2.add_widget(Q2row1)
        Q2row2=BoxLayout(orientation='horizontal', size_hint_y=0.315)
        Q2row2.add_widget(Label(text='Current Temperature', color=[0,0,0,1], font_size=18))
        Q2row2.add_widget(self.current_label)
        Quad2.add_widget(Q2row2)
        
        #create a label that will display the numerical value of the pumppower
        self.pumppower_label=Label(text=str(pumppower) + "%",color=[1,1,1,1], size_hint_x=0.5, font_size=50, bold=True)
        #quadrant 3 is a vertical box layout so widgets are added form the top to the bottom
        Quad3=BoxLayout(orientation='vertical')
        #first row of quadrant 3 is a anchor_x right anchor layout so widgets added are aligned to its right, we do this to leave space for the icon in the background
        Q3row1=AnchorLayout(anchor_x='right')
        #add label whose text will display the numerical value of the pump power
        Q3row1.add_widget(self.pumppower_label)
        #add the row to the quadrant
        Quad3.add_widget(Q3row1)
        #row 2 is a horizontal layout so the widgets are aded form the left to the right. row 2 is 29.5% of the height of quadrant 3 so row 1 would be 70.5% of the height of quadrant 3. size_hint_x means row 2 only takes up half the width of quadrant 3
        Q3row2=BoxLayout(orientation='horizontal', size_hint_y=0.295, size_hint_x=0.5)
        # add a label to display the text Water Pump power. size_hint_x is 0.5 so it only takes up 50% of the width of qaudrant 3 this is done so the text is aligned and directly underneath the icon
        Q3row2.add_widget(Label(text='Water Pump Power', color=[1,1,1,1], font_size=18))
        #add row 2 to quadrant 3 and the row is compelte
        Quad3.add_widget(Q3row2)
        
        #same logic as quadrant 3 but with quadrant 4 and fanpower this time. 
        self.fanpower_label=Label(text=str(fanpower) + "%",color=[1,1,1,1], size_hint_x=0.5, font_size=50, bold=True)
        Quad4=BoxLayout(orientation='vertical')
        Q4row1=AnchorLayout(anchor_x='right')
        Q4row1.add_widget(self.fanpower_label)
        Quad4.add_widget(Q4row1)
        Q4row2=BoxLayout(orientation='horizontal', size_hint_y=0.295, size_hint_x=0.5)
        Q4row2.add_widget(Label(text='Fan Power', color=[1,1,1,1], font_size=18))
        Quad4.add_widget(Q4row2)
        
        #add all four quadrants to the Tlayout. Quadrants are addded in the order 1,2,3 then 4. this is becuase kivy adds the widgets in the cloack wise direction. THis order ensures the correct widgets will appear in the desires places relative to the background image. 
        Tlayout.add_widget(Quad1)
        Tlayout.add_widget(Quad2)
        Tlayout.add_widget(Quad3)
        Tlayout.add_widget(Quad4)

        # Add the grid layout to the custom layout which contains our custom background image
        c.add_widget(Tlayout)
        
        #schedule an update every 0.1s so the values of pump power, fan power , taret temperature and current temperature will change accordingly to the current slider values
        Clock.schedule_interval(self.callback, 0.1)  
        return root

    def callback(self, instance):
        ''' Updates values for the labels and slides '''
        newinpreading = self.current_slider.value
        # update the target temperature in the waterpump state machine
        self.waterpumpcontrol.target=self.target_slider.value
        # update pumppower and fan power accordingly 
        pumppower, fanpower = self.waterpumpcontrol.step(newinpreading)[0]*100, self.waterpumpcontrol.step(newinpreading)[1]*100
        #update the text in the respective labels with the correct numbers 
        self.pumppower_label.text = str(pumppower) + "%"
        self.fanpower_label.text = str(fanpower) + "%"
        
        
if __name__ == '__main__':
    # Fix the window size of the app to match the touch screen size and also the size of our custom background image
    Window.size = (800,500)  
            
    GUIApp().run() 