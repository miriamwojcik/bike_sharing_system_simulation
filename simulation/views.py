from django.shortcuts import render
from django.http import HttpResponse
import time
import folium
from django_eventstream import send_event

# display the simulation page
def index(request):
    return render(request, 'simulation/simulation.html')

# return the map 
def display_map(request):
    return render(request, 'simulation/display_map.html')
