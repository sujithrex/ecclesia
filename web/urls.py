from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'web'

urlpatterns = [
    path('', LoginView.as_view(template_name='web/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='web:login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
] 