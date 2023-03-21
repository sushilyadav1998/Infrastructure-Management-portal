from django.urls import path

from ca import views
from .views import *

urlpatterns = [
        path('ca', views.ca_list)
        ]
