from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('essentials/', views.essentials, name='essentials'),
    path('baptism-record/', views.baptism_record_form, name='baptism_record_form'),
] 