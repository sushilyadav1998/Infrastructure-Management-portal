from django.urls import path

from detail import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
        path('serverdetails/', views.detail_list),
        path('newproject/', views.project_list),
        path('deleteproject/', views.delete_projectdirectory),
        path('listproject/', views.list_projectdirectory),
        path('upload/', FileUploadView.as_view())
        ]
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

