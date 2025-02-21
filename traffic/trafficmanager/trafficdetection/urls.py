from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('violations/', views.violations, name='violations'),

    path('driver_behavior/', views.driver_behavior, name='driver_behavior'),
    path('alerts/', views.alerts, name='alerts'),
    path('uploadimage/',views.ui, name='ui'),
    path('objecttracking/',views.ot, name='ob'),
    path('upload/', views.upload_view, name='upload'),


   
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)