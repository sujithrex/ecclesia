from django.urls import path
from . import views

app_name = 'congregation'

urlpatterns = [
    # Pastorate URLs
    path('pastorate/', views.pastorate_list, name='pastorate_list'),
    path('pastorate/add/', views.pastorate_add, name='pastorate_add'),
    path('pastorate/<int:pk>/', views.pastorate_detail, name='pastorate_detail'),
    path('pastorate/<int:pk>/edit/', views.pastorate_edit, name='pastorate_edit'),
    path('pastorate/<int:pk>/delete/', views.pastorate_delete, name='pastorate_delete'),
    
    # Church URLs
    path('pastorate/<int:pastorate_id>/church/', views.church_list, name='church_list'),
    path('pastorate/<int:pastorate_id>/church/add/', views.church_add, name='church_add'),
    path('church/<int:pk>/', views.church_detail, name='church_detail'),
    path('church/<int:pk>/edit/', views.church_edit, name='church_edit'),
    path('church/<int:pk>/delete/', views.church_delete, name='church_delete'),

    # Area URLs
    path('church/<int:church_id>/area/', views.area_list, name='area_list'),
    path('church/<int:church_id>/area/add/', views.area_add, name='area_add'),
    path('area/<int:pk>/', views.area_detail, name='area_detail'),
    path('area/<int:pk>/edit/', views.area_edit, name='area_edit'),
    path('area/<int:pk>/delete/', views.area_delete, name='area_delete'),

    # Fellowship URLs
    path('church/<int:church_id>/fellowship/', views.fellowship_list, name='fellowship_list'),
    path('church/<int:church_id>/fellowship/add/', views.fellowship_add, name='fellowship_add'),
    path('fellowship/<int:pk>/', views.fellowship_detail, name='fellowship_detail'),
    path('fellowship/<int:pk>/edit/', views.fellowship_edit, name='fellowship_edit'),
    path('fellowship/<int:pk>/delete/', views.fellowship_delete, name='fellowship_delete'),

    # Family URLs
    path('area/<int:area_id>/family/', views.family_list, name='family_list'),
    path('area/<int:area_id>/family/add/', views.family_add, name='family_add'),
    path('family/<int:pk>/', views.family_detail, name='family_detail'),
    path('family/<int:pk>/edit/', views.family_edit, name='family_edit'),
    path('family/<int:pk>/delete/', views.family_delete, name='family_delete'),
    path('family/search/', views.family_search, name='family_search'),

    # Member URLs
    path('family/<int:family_id>/member/', views.member_list, name='member_list'),
    path('family/<int:family_id>/member/add/', views.member_add, name='member_add'),
    path('member/<int:pk>/', views.member_detail, name='member_detail'),
    path('member/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('member/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('member/search/', views.member_search, name='member_search'),

    # Settings URLs
    path('respect/', views.respect_list, name='respect_list'),
    path('respect/add/', views.respect_add, name='respect_add'),
    path('respect/<int:pk>/edit/', views.respect_edit, name='respect_edit'),
    path('respect/<int:pk>/delete/', views.respect_delete, name='respect_delete'),

    path('relation/add/', views.relation_add, name='relation_add'),
    path('relation/<int:pk>/edit/', views.relation_edit, name='relation_edit'),
    path('relation/<int:pk>/delete/', views.relation_delete, name='relation_delete'),
] 