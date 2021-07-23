from django.shortcuts import render
from django.http import HttpResponse
from .vehicle_routing import optimize_truck_route
from .optimizing_resource_allocation import optimize_resource_allocation
import datetime
from datetime import timedelta
import pandas as pd
import threading

def vehicle_routing(request):
    global instr_html
    if request.method == 'GET':
        return render(request, 'vehicle_route_planner/vehicle_routing.html')
    # optimize_truck_route()
    else:
        d = request.POST['date']
        date = datetime.datetime.strptime(d, '%Y-%m-%d')
        vehicle_capacity = int(request.POST['vehicle_capacity'])
        current_date = datetime.date.today()
        check_delta = timedelta(days=7)
        if date.date() > current_date + check_delta or date.date() < current_date:
            msg = 'Data for the date selected are not available. Please select the date within the next 7 days.'
            return render(request, 'vehicle_route_planner/vehicle_routing.html', {'msg':msg })
        else:
            # try:
            def run_optimization():
                # get starting bike allocation
                print('optimizing resource alocation')
                optimize_resource_allocation(date)
                # generate the route
                print('optimizing resource alocation')
                optimize_truck_route(vehicle_capacity)
                status = True
                return status


            status = run_optimization()
            
            return render(request, 'vehicle_route_planner/vehicle_routing.html', {'status': status})
            # except:
            #     msg = 'Optimization Failed'
            #     return render(request, 'vehicle_route_planner/vehicle_routing.html', {'msg':msg })
            
            
def driver_instructions(request):
    return render(request, 'vehicle_route_planner/driver_instructions.html')

def route_map(request):
    return render(request, 'vehicle_route_planner/route_map.html')