from django.urls import path

from commands import views
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
        path('mountpoints', views.command_list),
        path('portinfo', views.port_info),
        path('useradd', views.useradd_list),
        path('telnetport', views.telnet_list),
        path('telnetonboardedserver', views.telnetonboardedserver_list),
        path('portinfoonboardedserver', views.portinfoonboardedserver_list),
        path('onboard', views.onboard_list),
        path('updatecredentials', views.updatecredentials_list),
        path('runservice', views.runmultipletimes_list),
        path('getdata', views.getdata_list),
        path('executecommand', views.executecommand_list),
        path('servercredentials', views.servercredentials_list),
        path('onboardmonitorport', views.onboardportmonitoring),
        path('portlist/<str:ip>/', views.portlist),
        path('getmonitorport', views.portmonitor_list),
        path('managepassword', views.managepassword_list),
        path('javainstall', views.javainstall_list),
        path('upload',views.uploadfile_list),
        path('getallportmonitordetails', views.getportmonitor_list),
        path('monitorstatus/<str:projectname>/', views.projectportmonitor_list),
        path('deletecredentials', views.deleteonboardedserver_list),
        path('killprocess', views.deletepid_list),
        path('deletepath', views.deletepath_list),
        path('applog/<str:ip>/', views.applogdata_list),
        path('projectdata/<str:projectname>/', views.projectdata_list),

        path('credentialprojectdata/<str:projectname>/', views.credentialprojectdata_list)
        ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
