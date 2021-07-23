# Methods to save, update, and delete
# Bikes, Trips, Stations, and Users data from the database

# Import models
from .models import Trip_Model
from .models import User_Model
from .models import Bike_Model
from .models import Station_Model

# Import classes
from .bike_system import Bike_System
from .bike import Bike
from .station import Station
from .trip import Trip
from .user import User

# import packages
from django.db import transaction
import json
import jsons
from typing import List
import datetime

def clear_db():
    try:
        User_Model.objects.all().delete()
        Bike_Model.objects.all().delete()
        Station_Model.objects.all().delete()
        Trip_Model.objects.all().delete()
    except:
        pass

def clear_trips():
    try:
        Trip_Model.objects.all().delete()
    except:
        pass

def delete_trips_date(date):
    try:
        d= date.date()
        dd = d.isoformat()
        Trip_Model.objects.filter(datetime_start__contains=dd).delete()
        print('deleted')
    except:
        pass

def clear_bikes():
    try: 
        Bike_Model.objects.all().delete()
    except:
        pass

def clear_stations():
    try: 
        Station_Model.objects.all().delete()
    except:
        pass

def clear_users():
    try: 
        User_Model.objects.all().delete()
    except:
        pass


def save_bikes(bikes):
    #  save bike objects to database
    for bike in bikes:
        bl = bike.location
        bike_id = bike.id
        bike_loc = json.dumps(bl)
        b = Bike_Model(bike_id= bike_id, bike_location= bike_loc)
        b.save()

def get_all_bikes():
    bikes_db = Bike_Model.objects.all()
    bikes = []
    for bike in bikes_db:
        loc = json.loads(bike.bike_location)
        b = Bike(bike.bike_id, loc)
        bikes.append(b)
    return bikes


def save_stations(stations):
    for station in stations:
        loc = json.dumps(station.location)
        bp = station.bikes_parked
        bikes_parked = jsons.dumps(bp)
        s = Station_Model(station_id= station.id, station_location = loc, station_demand = station.demand, minimum_bikes = station.minimum_bikes, station_capacity= station.capacity, docs_available = station.docs_available, bikes_parked=bikes_parked)
        s.save()


def get_all_stations():
    stations_db = Station_Model.objects.all()
    stations = []
    for station in stations_db:
        loc = json.loads(station.station_location)
        if jsons.loads(station.bikes_parked) == "[]":
            bikes_parked = []
        else:
            bikes_parked = jsons.loads(station.bikes_parked, List[Bike])
        s = Station(station.station_id, loc, 0, station.station_capacity, bikes_parked)
        stations.append(s)
    return stations

def save_users(users):
    for user in users:
        try:
            is_busy = user.is_busy
        except:
            is_busy = False
        u = User_Model(user_id = user.id, is_busy=is_busy)
        u.save()

def get_all_users():
    users_db = User_Model.objects.all()
    users = []
    for user in users_db:
        u = User(user.user_id)
        u.is_busy = user.is_busy
        users.append(u)

    return users


def get_bike():
    pass

def get_trips():
    pass

def update_user(user):
    u = User_Model.objects.get(user_id=user.id)
    u.is_busy = user.is_busy
    u.save()


def update_station(station):
    bp = station.bikes_parked
    bikes_parked = jsons.dumps(bp)
    s = Station_Model.objects.get(station_id=station.id)
    s.bikes_parked = bikes_parked
    s.station_capacity = station.capacity
    s.docs_available = station.docs_available
    s.save()


def update_bike(bike):
    bl = bike.location
    loc = json.dumps(bl)
    b = Bike_Model.objects.get(bike_id=bike.id)
    b.bike_location = loc
    b.save()

def save_trip(trip):
    b = trip.bike.id
    u = trip.user.id
    user = jsons.dumps(u)
    bike = json.dumps(b)
    ss = trip.starting_station
    starting_station = jsons.dumps(ss.id)
    dd = trip.destination_station
    destination_station = jsons.dumps(dd.id)
    t = Trip_Model(trip_id=trip.id, bike=bike, user=user, starting_station=starting_station, destination_station=destination_station, datetime_start = trip.datetime_start, datetime_end=trip.datetime_end)
    t.save()
    
