# Allocates bikes available between stations to meet the forecasted demand
# Using constraint programming
from demand_forecast.calculate_forecast import calculate_demand_forecast
import numpy as np
from scipy.optimize import minimize
from tabulate import tabulate
from constraint import *
import datetime
from datetime import timedelta

from simulation.models import Bike_Model
from simulation.models import Station_Model

def optimize_resource_allocation(date):

    def get_optimum_station_start(station, date):

        # GET MINIMUM NO OF BIKES NEEDED AT THE START OF THE DAY
        def get_optimum(hourly_forecast):
            # a variable to store minimum no of bikes required
            minimum = 0 
            # an array with hourly rental_forecast(0) and return_forecast(1)
            hourly_forecast = hourly_forecast
            # counter of bikes available at the station
            bike_counter = 0
            # loop 24 times (for every hour of the day)
            for i in range(0,24):
                hourly_diff = hourly_forecast[i][1]-hourly_forecast[i][0]
                # if within the hour more bikes were rented than returned + available at the station 
                if hourly_forecast[i][0]>(hourly_forecast[i][1]+bike_counter):
                    # count how many bikes the station was short off
                    lost =  bike_counter - hourly_diff
                    # update missing bikes by the number of bikes the station was short off
                    minimum += lost
                    # reset bike counter to 0
                    bike_counter = 0
                # otherwise update bikes available
                else:
                    bike_counter = bike_counter + hourly_diff
            return minimum

        # get the forecast for the date and station
        station_forecast = calculate_demand_forecast(station, date)
        station_forecast = station_forecast.drop(columns={'dateTime', 'station', 'hour'})
        hourly_forecast = station_forecast.to_dict('records')
        hf = []
        # convert the dataframe to array
        for item in hourly_forecast:
            rent = item['rentals_forecast']
            ret = item['returns_forecast']
            hf.append([rent,ret])
        # get the minimum number of bikes needed at the station
        minimum = get_optimum(hf)
        # return the number of bikes needed at the station 
        return minimum

    # Use the constraints programming to allocate bikes available between stations
    def solve_allocation(starting_opt, total):
        
        # constraint Problem object
        problem = Problem()

        # total number of bikes to be allocated 
        total = total

        # optimal minimum from the get_optimum_station_start method
        starting_opt = starting_opt
        st = dict(starting_opt)
        variables = []

        # set station numbers from the starting_opt as variables for constraint solving
        for key in st:
            variables.append(key)

        # variable name: station_id, solution: numbers between minimum number of bikes specified and and maximum station capacity
        for i in variables:
            # between
            # from models get station by id, minimum = bike(id).minimum, max capacity
            # i in range minimum, max+1, append solution[]
            # problem.add Variable (i[0], solutions)
            station = Station_Model.objects.get(station_id=i)
            minimum = station.minimum_bikes
            maximum = station.station_capacity
            solutions = []
            for j in range(minimum, maximum+1):
                solutions.append(j)
            problem.addVariable(i, solutions)

        def close_to_optimum(variable):
            mincheck = min(solutions, key=lambda x:abs(x-st[variable]))
            return mincheck

        # sum of all bikes allocated must equal the sum of all bikes available
        problem.addConstraint(ExactSumConstraint(total), variables)
        for v in variables:
            sol_set = []
            for i in range(close_to_optimum(v), max(solutions)+1):
                sol_set.append(i)
            # add as close to optimum as possible or greater constraint
            problem.addConstraint(InSetConstraint(sol_set), [v])

        # find solution
        solver = MinConflictsSolver()
        problem.setSolver(solver)
        solution = problem.getSolution()
        if solution is None:
            solution = {}
            return solution
        else:
            return solution

    start = datetime.datetime.now()
    date = date
    minimums = []
    # get the minimum number of bikes needed at each station
    for i in range(1,31):
        station=str(i)
        minimum = get_optimum_station_start(station, date)
        minimums.append([station, minimum])

    # test data 
    # minimums = [['1', 15], ['2', 15], ['3', 15], ['4', 15], ['5', 15], ['6', 15], ['7', 15], ['8', 15], ['9', 15], ['10', 15], ['11', 15], ['12', 15], ['13', 15], ['14', 15], ['15', 15], ['16', 15], ['17', 15], ['18', 15], ['19', 15], ['20', 15], ['21', 15], ['22', 15], ['23', 15], ['24', 15], ['25', 15], ['26', 15], ['27', 15], ['28', 15], ['29', 15], ['30', 15]]
    
    # Total number of bikes in the sysytem
    bikes_total = Bike_Model.objects.filter().all()
    bikes_total = len(bikes_total)


    print('Station_id and minimum number of bikes to meet demand')
    print(minimums)

    # get the total number of docks
    docs_total = 0
    stations = Station_Model.objects.filter().all()
    for station in stations:
        docs_total = docs_total+station.station_capacity

    # If more bikes in the system than docs available, allocate only as many as max docs
    total = 0
    if bikes_total>docs_total:
        total = docs_total
    else:
        total = bikes_total

    print('Total number of bikes in the system: ' + str(total))

    # get the bikes allocation
    solution = solve_allocation(minimums, total)
    # decrease the minimums until solution found or until minimums at 0
    print('Solving resource allocation problem...')
    if solution  =={}:
        while solution  =={} and (sum(v[1] for v in minimums)>0):
            print('Solution not found... Relaxing the problem..')
            for i in minimums:
                if i[1]>0:
                    i[1] = i[1]-1
            solution = solve_allocation(minimums, total)

    # if no solution found despite relaxing, set to default
    if solution == {}:
        print('Constraint OP failed')
        split = int(total/len(stations))
        rem = total%len(stations)
        for station in stations:
            solution[station.station_id] = split
        for i in range(1,rem+1):
            solution[str(i)] = solution[str(i)]+1
    else:
        print('Constraint OP successful')
        print('Solution found: ')
        print(solution)
            
    # save number of bikes allocated to each station in the db (station demand)
    for s in solution:
        station_id = s
        demand = solution[s]
        station = Station_Model.objects.get(station_id=station_id)
        station.station_demand = demand
        station.save()

    ex_time = datetime.datetime.now() - start
    print(ex_time)




