from django.urls import path

from jartoexec import views
from .views import *
from django.conf import settings

urlpatterns = [
        path('exec',views.jartoexec_list)
        ]
