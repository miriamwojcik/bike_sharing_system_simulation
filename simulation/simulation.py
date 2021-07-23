# The Simulation class controls simulation time and the number of rental events to be generated. 
# It also keeps track of the trips in progress. 

# Import packages
import random
from random import randint
import time
import sched
import datetime
from datetime import timedelta

# Import methods and classes
from .bss_events import Bss_Events
from .bike_system import Bike_System
from .bike import Bike
from .station import Station
from .trip import Trip
from .user import User

# Import data pre-processing functions
from generating_data.demand_forecast_data_prep import get_holidays, get_rain, get_temp, is_weekend

# Simulation class
# Attributes: 
# time_point - allows to track the simulation progress
# bss - Bike_System object
# current_trips - a list of the Trip objects with the attribute is_finished set to false (list of trips in progress where the bike was rented but has not been returned yet)
# dt - DateTime (can be actual or in the past when generating historical data)
# 
class Simulation:
    def __init__(self, timeout, bss, dt):
        self.time_point = 0
        self.timeout = timeout
        self.bss = bss
        self.current_trips = []
        self.dt = dt

    def new_rentals(self):
            
        # controls how many trips will be created during the given simulation step
        # more likely to generate trip during peak times, summer, weekdays, hot days
        peak = [8, 9, 16, 17, 18]
        quiet = [5, 6,21,22,23,24,1,2,3,4,0]
        # operating 24h for demonstration
        # not_operating = [0,1,2,3,4]
        not_operating=[]
        winter = [12,1,2]
        summer = [5,6,7,8]
        weekend = is_weekend(self.dt)
        holidays = get_holidays(self.dt)
        rain = get_rain(self.dt)
        temp = get_temp(self.dt)
        weight = 1.5
        if self.dt.hour in peak:
                weight+=1.8
        if self.dt.hour in quiet:
                weight-=4
        if rain==1:
                weight-=1
        if temp<50:
                weight-=1
        if temp>59:
                weight+.5
        if weekend == 1:
                weight-2.5
        if weekend == 0:
                weight+1.5
        if self.dt.month in winter:
                weight - 3
        if self.dt.month in summer:
                weight +.5
        if holidays == 1:
                weight-1

        # more likely to generate trip during peak times 
        weight = round(weight)
        if weight<=0:
            weight = 0.2

        # dont generate trips out of hours
        if self.dt.hour in not_operating:
            weight=0
        new_trips = random.randint(0,weight)
        i=0
        while i < new_trips:
            e = Bss_Events(self.bss, self.dt, True)
            new_rental =  e.create_trip()
            if new_rental != -1:
                self.current_trips.append(new_rental)
            i+=1
