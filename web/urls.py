from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('essentials/', views.essentials, name='essentials'),
    path('logout/', LogoutView.as_view(next_page='web:login'), name='logout'),
] 