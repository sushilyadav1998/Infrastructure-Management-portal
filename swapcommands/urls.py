from django.urls import path

from swapcommands import views
from .views import *

urlpatterns = [
        path('swapstatus',views.swapstatus_list),
        path('swapcreate',views.swapcreate_list),
        path('swapmonitor',views.swapmonitor_list)
        ]
