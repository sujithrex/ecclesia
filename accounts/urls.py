from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Pastorate Level URLs
    path('pastorate/', views.pastorate_list, name='pastorate_list'),
    path('pastorate/<int:pk>/', views.pastorate_detail, name='pastorate_detail'),
    path('pastorate/<int:pastorate_id>/account/add/', views.pastorate_account_add, name='pastorate_account_add'),
    
    # Church Level URLs
    path('church/<int:pk>/', views.church_detail, name='church_detail'),
    path('church/<int:church_id>/account/add/', views.church_account_add, name='church_account_add'),
    
    # Account Management URLs
    path('account/<int:pk>/', views.account_detail, name='account_detail'),
    path('account/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('account/<int:pk>/delete/', views.account_delete, name='account_delete'),
    
    # Transaction URLs
    path('account/<int:account_id>/transaction/add/', views.transaction_add, name='transaction_add'),
    path('transaction/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transaction/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('transaction/<int:pk>/history/', views.transaction_history, name='transaction_history'),
    
    # Account Type URLs
    path('account-type/add/', views.account_type_add, name='account_type_add'),
    path('account-type/<int:pk>/edit/', views.account_type_edit, name='account_type_edit'),
    path('account-type/<int:pk>/delete/', views.account_type_delete, name='account_type_delete'),
    
    # Category Management URLs
    path('category/add/', views.category_add, name='category_add'),
    path('category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
] 