from django.urls import path
from . import consumers

ws_urlpatterns = [
    path('ws/simulation/', consumers.WSConsumer.as_asgi()),
]