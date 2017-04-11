def radiation(env, ts):
    ''' Process to adjust temperature based on radiation produced from the sun '''
    start_time = 3600 * 6 # Assume start at 6am
    time = start_time
    while True:
        yield env.timeout(1)

        # Change the radiation amount based on the time of the day
        # Ratio of the relative radiation at different times of the day
        # This is an estimatation with the radiation peaking at noon and decreasing over time
        heatRatio = [0, 0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.4, 0.6, 0.7, 1, 0.9, 0.8, 0.6, 0.4, 0.2, 0, 0, 0, 0, 0, 0]

        time += 1
        time %= 24 * 60 * 60 # Reset the time if the day rolls over

        # Find hour of the day rounded down
        hour = time//(3600)
        rad = 3 * heatRatio[hour]

        # If radiation is not 0, change temperature of the water
        if rad != 0:
            # Adjust temperature of the water
            yield ts.Twater.put(rad/ts.mcwater)
        
def bottleout(env, ts):
    ''' Process to adjust heat loss from the bottle through conduction to the glass and convection to air '''
    while True:
        yield env.timeout(1)
        # Calculate Qconv to air
        Qconvout=ts.airfreeconvec*ts.bottleSA*ts.tempdiff
        # Calculate Qcond to glass
        Qcondout=ts.bottle_conductivity*ts.tempdiff

        # Calculate heat loss and adjust temperature
        totalloss=Qconvout+Qcondout

        # If totalloss is not 0, adjust temperature
        if totalloss != 0:
            yield ts.Twater.get(totalloss/ts.mcwater)

def siliconecond(env, ts):
    ''' Process to adjust heat loss due to conduction to the silicon tubes from the heat exchanger '''
    while True:
        yield env.timeout(1)

        # Calculate heat loss due to conductivity using Q = k
        Qout=1.0/ts.si_res * ts.tempdiff

        # If Qout is not 0, adjust temperature
        if Qout != 0:
            yield ts.Twater.get(Qout/ts.mcwater)

def pumpconvec(env, ts):
    ''' Process to adjust heat loss based on the convection from the water pump '''
    while True:
        yield env.timeout(1)

        # If pump is not running, calculate from free convection coefficient of water
        if ts.mass_flux<=0:
            Qpumpout = ts.tempdiff * ts.tubeSA * ts.waterfreeconvcoeff
            yield ts.Twater.get(Qpumpout/ts.mcwater)
        else:
            # Otherwise if pump is running, use forced convection coefficient of water
            Qpumpout=ts.tempdiff*ts.tubeSA*ts.waterconvcoeff
            #TODO: make sure self.mass flux updates every second
            yield ts.Twater.get(Qpumpout/ts.mcwater)
  
def powerconsumption(env,ts):
    ''' Process to measure power consumption '''
    while True:
        # Loop through one week
        seconds_in_a_week = 7*24*60*60
        for i in range(seconds_in_a_week):
            # Add power consumption per second based on mass flow rate
            yield env.timeout(1)
            if ts.mass_flux<=0:
                pass
            else:
                yield ts.powerConsumption.put(ts.mass_flux/5.0*100.0)

        # Output power consumption after one week
        print 'Power Consumption for this week was {}W'.format(ts.powerConsumption.level)
        # Reset power consumption
        yield ts.powerConsumption.get(ts.powerConsumption.level)
        