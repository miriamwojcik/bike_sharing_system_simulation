# import packages
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import SyncConsumer
from django_eventstream import send_event
from time import sleep
from simulation.sim_db_methods import get_all_stations
from simulation.sim_db_methods import get_all_bikes
import json


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()   
        
         # # READ DATA FROM DATABASE
        # # get bikes from database
        
        b = get_all_bikes()

        # get stations data from database 
        s = get_all_stations()

        stations_loc = []
        for station in s:
                station_location = reversed(station.location)
                station_location = list(station_location)
                station_id = station.id
                stations_loc.append([station_id, station_location])


        bikes_loc =[]
        for bike in b:
                bike_location = bike.location
                bike_location = list(bike_location)
                bike_id = bike.id
                bikes_loc.append([bike_id, bike_location])
                
            # msg to by passed through the socket
        msg = {
                'data_control': 'start',
                'stations' : stations_loc,
                'bikes' : bikes_loc
        }

        # self.send(text_data=json.dumps(msg))
        self.send(text_data=json.dumps(msg))

    
        

        

class Simulation_Consumer(SyncConsumer):
        channel_layer_alias = "simulation"
        
        
        
        
        