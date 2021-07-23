from django.urls import path
from . import views


urlpatterns = [
    path('vehicle_routing', views.vehicle_routing,name='vehicle_routing'),
    path('driver_instructions', views.driver_instructions,name='driver_instructions'),
    path('route_map', views.route_map,name='route_map'),
]