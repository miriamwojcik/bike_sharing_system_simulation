#Routing working
#Drawing a map working
#Solution for one vehicle only

from optimization.distance_matrix import Distance_Matrix
from optimization.routing_optimization import Optimization

# Change to station data from Database
from simulation.station import Station

#Import Folium
import folium
from folium.features import DivIcon
from folium import plugins as pg

#Import openrouteservice
import openrouteservice
from openrouteservice import convert
from openrouteservice.directions import directions
import openrouteservice.optimization as op

# Import Open Street Map python tools
from OSMPythonTools.nominatim import Nominatim

#Import other libraries
import webbrowser
import json
from matplotlib import colors as mcolors
import math
from time import sleep

# Import station model
from simulation.models import Station_Model



    # Check which bikes need to be moved
    # station target vs current station level
    # get surplus and - stations

def optimize_truck_route(vehicle_capacity):

    global instr_html
    # [-2.095718,57.148764]
    stations = {}
    # The OT-Tools CVRP Solver provides the route from and to the same point
    # Set depo as a starting point (station0)
    stations[0] = {"id": 0,
                "coordinates": [-2.13988,57.1196],
                "demand": 0,
                "type": "depo"}

    # Get user input for capacity
    vehicle_capacities = [vehicle_capacity]
    warehouse = []
    # balanced stations holds info about stations that do not need to be visited by a track
    balanced_stations = []

    # get station demands
    stations_data = Station_Model.objects.filter().all()

    
    # the sum of demands must be equal to 0, if not reduce, increase accordingly making sure not to exceed capacity
    demand_sum = 0
    for station in stations_data:
        demand_sum = demand_sum -(station.station_demand-len(json.loads(station.bikes_parked)))
    
    # For some reason the or-tool does not work well for single vehicle problems
    # Despite changing parameters, the solution was not found, uless a sum of deliveries and pickups ==0
    # if demand_sum different than 0 amend the demands (could be a result of not all bikes being parked at stations when calculating the route)
    if demand_sum != 0:
        # how many bikes should be added/reduced
        print('Amending the number of bikes to be delivered')
        update_value = int(abs(demand_sum)/len(stations_data))
        rem = abs(demand_sum)%len(stations_data)
        i=0
        counter = abs(demand_sum)
        if demand_sum >0:
            while counter>0 and i<len(stations_data):
                if(stations_data[i].station_demand +update_value)<=stations_data[i].station_capacity:
                    stations_data[i].station_demand = stations_data[i].station_demand +update_value
                    counter-=update_value
                i+=1
            stations_data[i-1].station_demand += rem
        if demand_sum <0:
            while counter>0 and i<len(stations_data):
                if(stations_data[i].station_demand -update_value)>=stations_data[i].minimum_bikes:
                    stations_data[i].station_demand = stations_data[i].station_demand - update_value
                    counter-=update_value
                i+=1
            stations_data[i-1].station_demand -= rem

    # conver tdemand to a difference between the target and number of bikes currently parked at the station
    for station in stations_data:
        station.station_demand = station.station_demand-len(json.loads(station.bikes_parked))
    
    # remove from the list stations that are already balanced 
    stations_data = list(stations_data)
    for station in stations_data:
        if (station.station_demand) == 0:
            balanced_stations.append(station)
            stations_data.remove(station)
    
    # set counter i to 1 as depo at index 0
    i = 1
    # negative demand means oversupply
    for station in stations_data:
        stations[i] = {"id": int(station.station_id),
                "coordinates": json.loads(station.station_location),
                "demand": -(station.station_demand),
                "type": "station"}
        i+=1

    # an array to store the coordinates of the stations to be balanced
    coordinates = []
    # an array to store demands for stations to be rebalanced
    demands = []

    # In the future allow the user to specify the number of vehicles
    vehicles_no = 1

    
    for station in stations:
        coordinates.append(stations[station]['coordinates'])
        demands.append(stations[station]['demand'])
        try:
            if(stations[station]['type']=='depo'):
                warehouse = stations[station]['coordinates']
        except:
            pass
    
    # Generate distance matrix using the openrouting
    dm = Distance_Matrix(coordinates).get_distance_matrix()

    # sleep to avoid API limit error
    # sleep(10)

    #GET OPTIMIZED ORDER OF VISITS
    order = Optimization(dm, demands, vehicles_no, vehicle_capacities).get_optimized_order()
    ordered_locations = []
    priority = 0
    count=0

    print(order)

    for i in order:
        ordered_locations.append(stations.get(i))

    ordered_coordinates = []
    for i in ordered_locations:
        ordered_coordinates.append(i['coordinates'])

    client = openrouteservice.Client(key='5b3ce3597851110001cf6248aa422718516246e08bf63377485a1e13')


    map_dir = folium.Map(location=[57.15,-2.10], zoom_start=11)
    instr_html = '<p style="color:SlateBlue;" class="depo"><b>Start from Depo: '

    # Get depo address
    nominatim = Nominatim()
    try:
        warehouse_address = nominatim.query(warehouse[1], warehouse[0], reverse=True).address()
    except:
        warehouse_address = {'road':'', 'city':'', 'postcode':''}
    instr_html +=  warehouse_address['road'] + ' ' + warehouse_address['city'] + ' ' + warehouse_address['postcode'] + '</b></p>'

    def is_warehouse(i):
        try:
            if i['type']=='depo':
                return True
            else:
                return False
        except:
            return False

    def draw_directions(color, i):
        global instr_html
        color = color
        start= ordered_locations[i]['coordinates']
        try:
            end = ordered_locations[i+1]['coordinates']
            if ordered_locations[i+1]['type'] == 'depo':
                color='navy'

            coords = [start, end]
            sub_route = client.directions(coordinates=coords, format= 'geojson', geometry=True, instructions_format='html', units='km')
            sg = sub_route['features'][0]['geometry']
            instructions = sub_route['features'][0]['properties']['segments']
            count = 0
            for step in range (len(instructions)):
                segs = instructions[step]['steps']
                count +=1
                for ins in segs:
                    dist = ins['distance']
                    inst = ins['instruction']
                    instr_html += '<p>' + inst + '. Distance: ' + str(dist) + 'km</p>'
            if(ordered_locations[i+1]['id']!=0):
                if(ordered_locations[i+1]['demand'])<=0:
                    instr_html += '<p style="color:SlateBlue; text-decoration: underline;" class="stop"><b>Stop ' + str(i+1) + '/ Station id: ' + str(ordered_locations[i+1]['id']) +'. Drop off: ' + str(abs(ordered_locations[i+1]['demand'])) + ' bikes</b></p>'

                if(ordered_locations[i+1]['demand'])>0:
                    instr_html += '<p style="color:SlateBlue; text-decoration: underline;" class="stop"><b>Stop ' + str(i+1) + '/ Station id: ' + str(ordered_locations[i+1]['id']) +'. Pick up: ' + str(ordered_locations[i+1]['demand']) + ' bikes</b></p>'

            gj = folium.GeoJson(name='{}'.format(color),
                                data={"type": "FeatureCollection", "features": [{
                                    "type": "Feature",
                                    "geometry":sg,
                                    "properties": {"color": color}
                                }]},
                                style_function=lambda x: {"color": x['properties']['color']})
            gj.add_to(map_dir)
        except:
            pass


    def add_markers(loc_id, coord, is_warehouse, job_id, color):
        if is_warehouse is True:
            point=list(reversed(coord))
            map_dir.add_child(folium.Marker(point, icon=folium.Icon(icon='plain', color='lightgray')))
            folium.Marker(point, tooltip='warehouse', icon=folium.DivIcon(icon_size=(150,36),
                                                                        icon_anchor=(4,34), html=f"""<div style="color: 'black'; z-index: -1;">W</div>""")).add_to(map_dir)
        else:
            point=list(reversed(coord))
            step_no = job_id
            deliver = 0
            pickup = 0
            if ordered_locations[job_id]['demand']<0:
                deliver = abs(ordered_locations[job_id]['demand'])
            else:
                pickup = abs(ordered_locations[job_id]['demand'])

            details = 'Station ID: '+ str(loc_id) + '<br>Stop no: ' + str(job_id) + '<br>Drop off: ' + str(deliver) + ' Pick up: ' + str(pickup)
            folium.Marker(point, tooltip=details, icon=pg.BeautifyIcon(border_width =0, text_color='white', background_color=color, number=step_no, icon_shape='marker')).add_to(map_dir)

    

    # add markers for the balanced stations
    def add_balanced_markers():
        for station in balanced_stations:
            station_location = json.loads(station.station_location)
            point=(station_location[1], station_location[0])
            st_icon =  folium.features.CustomIcon('static/bike_sharing_system/img/station_icon.png')
            balanced_details = 'Station ID: ' + str(station.station_id) + ' is balanced'
            folium.Marker(point, tooltip=balanced_details, popup=balanced_details, icon=st_icon, shape='circle-dot',).add_to(map_dir)


    colors = mcolors.CSS4_COLORS
    i = 0
    for location in ordered_locations:
        is_depo = is_warehouse(location)
        color = colors['navy']
        add_markers(location['id'], location['coordinates'], is_depo, i, colors['orange'])
        draw_directions(color, i)
        i+=1

    add_balanced_markers()
    instr_html += '<p style="color:SlateBlue;" class="depo"><b>Back at Depo: '  + warehouse_address['road'] + ' ' + warehouse_address['city'] + ' ' + warehouse_address['postcode'] + '</b></p>'
    instr_file = open('optimization/templates/vehicle_route_planner/driver_instructions.html', 'w')
    instr_file.write(instr_html)
    map_dir
    map_dir.save('optimization/templates/vehicle_route_planner/route_map.html')