
# Import modules and libraries
import json
from faker import Faker
import datetime
from datetime import timedelta
import random
from random import randint
from simulation.models import Trip_Model
import time
import math
import sched

# Import classes
from simulation.bike_system import Bike_System
from simulation.bike import Bike
from simulation.station import Station
from simulation.trip import Trip
from simulation.user import User
from simulation.bss_events import Bss_Events
from simulation.simulation import Simulation

# Import methods
from simulation.sim_db_methods import update_user, update_station, save_trip, update_bike
from simulation.sim_db_methods import get_all_bikes
from simulation.sim_db_methods import get_all_users
from simulation.sim_db_methods import get_all_stations

from .demand_forecast_data_prep import get_holidays, get_rain, get_temp, is_weekend

# Faker
def generate_past_trips(start_date, number_of_days):

        # faker generates synthetic data
        faker = Faker()

        # set the starting date time
        dt = start_date

        # how many days should the data be generated for
        # set the final date the data will be generated for
        timeline= timedelta(days=number_of_days)
        last_day = dt +timeline

        
        # set delta --> increase date by 1 day in the loop
        delta = timedelta(days=1)

        # loop while date earlier than the closest date to be generated
        while(dt<last_day):
                # create random number of trips for the day; Glasgow avarage in first year 262 - avarage for selected days of the week between 205 and 301
                print(dt)
                number_of_trips = faker.random_int(200,300)
                for i in range(0, number_of_trips):
                        bike_id = str(faker.random_int(1,360))
                        bike = json.dumps(bike_id)
                        trip_id = str(faker.unique.random_int(1000000000, 999999999999))
                        user_id = str(faker.random_int(1,250))
                        user=json.dumps(user_id)
                        starting_station_id = str(faker.random_int(1,30))
                        ss = json.dumps(starting_station_id)
                        destination_station_id = str(faker.random_int(1,30))
                        dd=json.dumps(destination_station_id)
                        # get random duration of the trip;Glasgow data between 5 min to few days; majority less than 30 min
                        random_duration = faker.random_int(600,3600)
                        trip_delta = timedelta(seconds=random_duration)
                        # operating hours to be randomly chosen from
                        timed_dt_min = datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=5)
                        timed_dt_max = datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=23, minute= 59)
                        datetime_start = faker.date_time_between_dates(timed_dt_min, timed_dt_max)
                        datetime_end = datetime_start+trip_delta
                        t = Trip_Model(trip_id=trip_id, bike=bike, user=user, starting_station=ss, destination_station=dd, datetime_start = datetime_start, datetime_end=datetime_end)
                        t.save()
                dt = dt+delta

def simulate_past_trips(start_date, number_of_days):
        # Import libraries
        def run_simulation(sim):
                def rs():
                        delta = timedelta(minutes=1)
                        # run for the specified period of time
                        if sim.dt < sim.timeout:
                                while sim.dt<sim.timeout:
                                        # generate new trip
                                        sim.new_rentals()
                                        # update all current trips (move a bike or return)
                                        for r in sim.current_trips:
                                                e = Bss_Events(sim.bss, dt, False)
                                                e.update_trip(r)
                                                bike_location = r.bike.location
                                                bl=list(bike_location)

                                                if r.trip_finished == True:
                                                        sim.current_trips.remove(r)
                                                        break
                                        # update time
                                        sim.time_point += 1
                                        sim.dt = delta+sim.dt
                                        print(sim.dt)
                                        schedul.enter(2,1,rs)
                                print('Timeout. Cannot rent more bikes. Wait for bikes on the move to be parked')
                                sim.time_point += 1
                                sim.dt = delta+sim.dt
                                schedul.enter(1,1,rs)
                        # if the time passed wait until all bikes that were rented are parked
                        else:
                                if len(sim.current_trips) > 0:
                                        while len(sim.current_trips) > 0:
                                                # update unfinished trips
                                                for r in sim.current_trips:
                                                        e = Bss_Events(sim.bss, dt, False)
                                                        e.update_trip(r)
                                                        bike_location = r.bike.location
                                                        bl=list(bike_location)
                                                        # steam bikes locations to browsers
                                                        if r.trip_finished == True:
                                                                sim.current_trips.remove(r)
                                                sim.dt = delta+sim.dt
                                                schedul.enter(2,1,rs)
                                                sim.time_point += 1
                                        print('Simulation finished')
                timestep = 0
                # set up the simulation scheduler
                schedul = sched.scheduler(time.time, time.sleep)
                schedul.enter(1,1,rs)
                schedul.run()
                # delta controls how much time is added with each simulation step (itteration)
                        



        # set up the date for which the data will be simulated
        # datetime.now returns current date and time
        # format current datetime data to get consistent format


        dt = start_date

        # timestep variable controls the delay time for the simulation
        # for the real-time app set up to 10
        # for the data generation set up to 0 to speed up computation time
        timestep = 0

        # keeps track of the simulation step
        time_point = 0
        # set the time the bussiness stops operating
        # delta_out = datetime.timedelta(minutes=2)
        delta_out = timedelta(hours=24)
        timeout = dt+delta_out
        
        # track number of bikes rented
        # lost_transaction = 0
        # no_of_rents = 0

        # READ DATA FROM DATABASE
        # get bikes from database
        
        b = get_all_bikes()

        # get stations data from database 
        s = get_all_stations()

        # get user data from database
        u = get_all_users()

        # Create bike system object, pass all stations bikes and users created
        bss= Bike_System(s, b, u)
        


        # set the starting date time
        dt = start_date

        # how many days should the data be generated for
        # set the final date the data will be generated for
        timeline= timedelta(days=(number_of_days+1))
        last_day = dt +timeline

        # set delta --> increase date by 1 day in the loop
        delta = timedelta(days=1)
        while(dt<last_day):
                dt = dt.replace(hour=0)
                timeout = dt+delta_out
                dt = dt.replace(hour=5)
                print(dt)
                sim = Simulation(timeout, bss, dt)
                run_simulation(sim)
                dt = dt+delta
        
        

    