# The 'real-time' simulation controller

# import packages
from channels.generic.websocket import WebsocketConsumer
from django_eventstream import send_event
from channels.layers import get_channel_layer
import threading
import json
import time
from time import sleep
import sched
import datetime
from datetime import timedelta
import random
from random import randint

# Import openrouteservice
import openrouteservice
from openrouteservice import Client
from openrouteservice.directions import directions

#Import Folium
import folium
from folium.features import DivIcon
from folium import plugins as pg

# Import classes
from simulation.simulation import Simulation
from simulation.bss_events import Bss_Events
from simulation.bike_system import Bike_System
from simulation.bike import Bike
from simulation.station import Station
from simulation.trip import Trip
from simulation.user import User

# Import methods
from simulation.sim_db_methods import save_bikes, get_all_bikes, save_users, get_all_users, save_stations, get_all_stations, clear_db


class SimThread():
        # a method to run the process
    def run(self):
        channel_layer = get_channel_layer()

        # a data for the browser to draw stations and initial bike locations
        def get_set_up_data(bss):
                stations_loc = []
                for station in bss.stations:
                        station_location = reversed(station.location)
                        station_location = list(station_location)
                        station_id = station.id
                        stations_loc.append([station_id, station_location])


                bikes_loc =[]
                for bike in bss.bikes:
                        bike_location = bike.location
                        bike_location = list(bike_location)
                        bike_id = bike.id
                        bikes_loc.append([bike_id, bike_location])
                        
                # msg with the stations and bikes data to be streamed to the browsers
                msg = {
                        'data_control': 'start',
                        'stations' : stations_loc,
                        'bikes' : bikes_loc
                }
                return msg

        def get_now():
                today= datetime.datetime.now()
                y = today.year
                m = today.month
                d = today.day
                h = today.hour
                min = today.minute
                s = today.second
                dt = datetime.datetime(y, m, d, h, min, s) 
                return dt

        # method controling the simulation
        def run_simulation(sim):
                def rs():
                        # run for the specified period of time
                        if sim.dt < sim.timeout:
                                print('Simulation started...')
                                # counter used to create new trips every 10 iterations
                                counter=10
                                while sim.dt<sim.timeout:
                                        if counter == 10:
                                                sim.new_rentals()
                                                counter = 0
                                        # update all current trips (move a bike or return)
                                        for r in sim.current_trips:
                                                e = Bss_Events(sim.bss, dt, True)
                                                e.update_trip(r)
                                                bike_location = r.bike.location
                                                bl=list(bike_location)
                                                # stream updated bikes locations to the browsers
                                                set_up_data = get_set_up_data(sim.bss)
                                                text_data = {'m': bl, 'bike_id':r.bike.id, 'data_control':'update', 'setup':set_up_data}
                                                send_event('simulation', 'message', text_data)
                                                if r.trip_finished == True:
                                                        sim.current_trips.remove(r)
                                                        break
                                        # update time
                                        sim.time_point += 1
                                        # update every 10 sec
                                        sleep(10)
                                        sim.dt = get_now()
                                        counter += 1
                                        schedul.enter(2,1,rs)
                                print('Timeout. Cannot rent more bikes. Wait for bikes on the move to be parked')
                                sim.dt = get_now()
                                # schedule.enter(delay,priority,method)
                                schedul.enter(10,1,rs)
                        # if the time passed wait until all bikes that were rented are parked
                        else:
                                if len(sim.current_trips) > 0:
                                        print(len(sim.current_trips))
                                        while len(sim.current_trips) > 0:
                                                # update unfinished trips
                                                for r in sim.current_trips:
                                                        e = Bss_Events(sim.bss, dt, True)
                                                        e.update_trip(r)
                                                        bike_location = r.bike.location
                                                        bl=list(bike_location)
                                                        # steam bikes locations to browsers
                                                        set_up_data = get_set_up_data(sim.bss)
                                                        text_data = {'m': bl, 'bike_id':r.bike.id, 'data_control':'update', 'setup':set_up_data}
                                                        send_event('simulation', 'message', text_data)
                                                        if r.trip_finished == True:
                                                                sim.current_trips.remove(r)
                                                # update every 10 sec
                                                sleep(10)
                                                sim.dt = get_now()
                                                schedul.enter(2,1,rs)
                                                sim.time_point += 1
                                                print('Timepoint: ' + str(sim.time_point))
                                        print('Simulation finished')
                # set up the simulation scheduler
                schedul = sched.scheduler(time.time, time.sleep)
                schedul.enter(2,1,rs)
                schedul.run()
                # delta controls how much time is added with each simulation step (itteration)
                

        # API key
        client = openrouteservice.Client(key='5b3ce3597851110001cf6248361bdec0c0b94c0dbcc8c0d4b07fd4f6')


        # map
        map = folium.Map(location=[57.15, -2.10], zoom_start=11)
        bike_loc = []

        # set up the date for which the data will be simulated
        # datetime.now returns current date and time
        # format current datetime data to get consistent format

        dt = get_now()

        # keeps track of the simulation step
        time_point = 0
        # set the time for how the simulation should be run
        delta_out = datetime.timedelta(weeks=40)
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
        sim = Simulation(timeout, bss, dt)

        run_simulation(sim)


        

    