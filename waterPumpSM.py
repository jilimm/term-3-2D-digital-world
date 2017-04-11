import libdw.sm as sm

class WaterPumpSM(sm.SM):
    startState=0
    #create a attribute 'target' for the target temperature in the water pump SM class.
    # 33.0 is just a placeholder value. target will be constantly updated in the call back function below to reflect the slider value. 
    target=33.0
    # we create an attribute diff2 which corresponds to the second error e(n-1). we will continually update this e(n-1) term everytime SM steps.
    # diff 2 is initialized as 0 because the e(n-1) term is initially 0.
    diff2=0
    #TODO: actual proprtionality constant 
    k1, k2 =11,-4
    # Error value is current (inp) - target
    def getNextValues(self, currentState, inp):
        #input is the current temperature (as decided by the slider)
        if self.target>=inp:
            outp=(0.0, 0.0)
            nextState=0 
        else:
            #diff1 is e(n) which is dependent on the input. e(n) is difference between ur current inpupt and target
            diff1=inp-self.target
            # Power output is rounded off to 2dp for simplicity
            power=round(self.k1*diff1+self.k2*self.diff2,2)
            # Output is a tuple returns two values from 0.0 to 1.0
            outp=(power/100.0, power/100.0)
            # update e(n-1) value. at the next step, current e(n) value will be the new e(n-1) value
            self.diff2=diff1
            nextState = 1

        #ensure that output never exceeds 100
        if outp[0]>1.0:
            outp=(1.0,1.0)
        #ensure outp never goes negative because pump cannot have negative pwoer
        elif outp[0]<0:
            outp=(0,0)
        else:
            outp=outp
        return (nextState, outp)