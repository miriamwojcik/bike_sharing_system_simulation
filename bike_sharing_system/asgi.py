"""
ASGI config for bike_sharing_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from .routing import ws_urlpatterns
import django_eventstream
from . import consumers


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bike_sharing_system.settings')


application = ProtocolTypeRouter({
    'http': URLRouter([
        url(r'^events/', AuthMiddlewareStack(
            URLRouter(django_eventstream.routing.urlpatterns)
        ), { 'channels': ['simulation'] }),
        url(r'', get_asgi_application()),
    ]),
    "websocket": AuthMiddlewareStack(URLRouter(ws_urlpatterns)),
    "channel": ChannelNameRouter({
        "simulation":consumers.Simulation_Consumer.as_asgi(),
    })
    
})

