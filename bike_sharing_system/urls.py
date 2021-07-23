"""bike_sharing_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import include
from simulation import views
from optimization import views
from demand_forecast import views
from django.conf.urls import url, include
import django_eventstream

urlpatterns = [
    # path('', views.index),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('/bike_sharing_system/img/favicon.ico'))),
    path('', include('simulation.urls')),
    path('planner/', include('optimization.urls')),
    path('planner/', include('demand_forecast.urls')),
    url(r'^events/', include(django_eventstream.urls)),
]


