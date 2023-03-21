from monitoring import views
from .views import *
from django.urls import path, include

urlpatterns = [
        path('urlonboard', views.urlonboard_list),
        path('monitorurls',views.monitorurls_list)
        ]

