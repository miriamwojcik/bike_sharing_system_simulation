from django.shortcuts import render
from django.http import HttpResponse
from simulation.models import Station_Model
from simulation.models import Trip_Model
import datetime
from datetime import timedelta
import pandas as pd

from generating_data.generate_station_history import get_last_year_station_data
from demand_forecast.calculate_forecast import calculate_demand_forecast

def forecast(request):
    if request.method == 'GET':
        return render(request, 'demand_forecast/forecast.html')
    else:
        d = request.POST['date']
        date = datetime.datetime.strptime(d, '%Y-%m-%d')
        station = str(request.POST['docking_station'])
        hist = {}
        hist_list = []
        hist_full = []
        station_history = []
        forecast_full = []
        msg=''
        station = str(station)
        # Check is the date within 7 days 
        current_date = datetime.date.today()
        check_delta = timedelta(days=7)
        if current_date + check_delta >= date.date() and current_date < date.date():
            delta= timedelta(days=10)
            last_year = date - delta
            hist_data = get_last_year_station_data(station, last_year)
            for item in hist_data:
                hist['time'] = (item['ts'].hour)
                hist['rented'] = item['rented']
                hist['returned'] = int(item['returned'])
                hist_list.append([hist['time'],hist['rented'],hist['returned']])

            for i in range(0,24):
                found = False
                h = 0
                for item in hist_list:
                    if item[0]==i:
                        found=True
                        hist_full.append(item)
                if found == False:
                    hist_full.append([i, 0, 0])

            for item in hist_full:
                hist_named = {}
                hist_named = {
                    'time' : datetime.time(item[0]).strftime("%H:%M:%S"),
                    'rented' : item[1],
                    'returned' : item[2],
                }
                station_history.append(hist_named)

            
            f = calculate_demand_forecast(station, date)
            forecast = f.to_dict('records')

            for f in forecast:
                fork_named = {}
                time = datetime.time(f['hour']).strftime("%H:%M:%S")
                fork_named = {
                    'time' : time,
                    'rented' : f['rentals_forecast'],
                    'returns' : f['returns_forecast']
                }
                forecast_full.append(fork_named)
                data = zip(station_history, forecast_full)
            return render(request, 'demand_forecast/forecast.html', {'data' : data, 'date':date.date(), 'station_id':station})
        else:
            msg = 'Data for the date selected are not available. Please select the date within the next 7 days.'
            return render(request, 'demand_forecast/forecast.html', {'msg':msg })
    


    


