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
    path('account/<int:account_id>/transaction/add/receipt/', views.transaction_add_receipt, name='transaction_add_receipt'),
    path('account/<int:account_id>/transaction/add/offertory/', views.transaction_add_offertory, name='transaction_add_offertory'),
    path('account/<int:account_id>/transaction/add/bill/', views.transaction_add_bill, name='transaction_add_bill'),
    path('account/<int:account_id>/transaction/add/acquittance/', views.transaction_add_acquittance, name='transaction_add_acquittance'),
    path('account/<int:account_id>/transaction/add/', views.transaction_add, name='transaction_add'),
    
    # Transaction Edit URLs
    path('transaction/<int:pk>/edit/receipt/', views.transaction_edit_receipt, name='transaction_edit_receipt'),
    path('transaction/<int:pk>/edit/offertory/', views.transaction_edit_offertory, name='transaction_edit_offertory'),
    path('transaction/<int:pk>/edit/bill/', views.transaction_edit_bill, name='transaction_edit_bill'),
    path('transaction/<int:pk>/edit/acquittance/', views.transaction_edit_acquittance, name='transaction_edit_acquittance'),
    path('transaction/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    
    path('transaction/<int:pk>/', views.transaction_view, name='transaction_view'),
    path('transaction/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('transaction/<int:pk>/history/', views.transaction_history, name='transaction_history'),
    
    # Account Type URLs
    path('account-types/add/', views.account_type_add, name='account_type_add'),
    path('account-types/<int:pk>/edit/', views.account_type_edit, name='account_type_edit'),
    path('account-types/<int:pk>/delete/', views.account_type_delete, name='account_type_delete'),
    
    # Category Management URLs
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Member Search API
    path('api/search-members/', views.search_members, name='search_members'),
    
    # Diocese Transaction URLs
    path('diocese/<int:account_id>/transaction/add/', views.diocese_transaction_add, name='diocese_transaction_add'),
    path('diocese/<int:account_id>/transaction/contra/add/', views.diocese_transaction_add_contra, name='diocese_contra_add'),
    path('diocese/transaction/<int:pk>/', views.diocese_transaction_view, name='diocese_transaction_view'),
    path('diocese/transaction/<int:pk>/edit/', views.diocese_transaction_edit, name='diocese_transaction_edit'),
    path('diocese/transaction/<int:pk>/delete/', views.diocese_transaction_delete, name='diocese_transaction_delete'),
    
    # Diocese Category URLs
    path('diocese/categories/add/', views.diocese_category_add, name='diocese_category_add'),
    path('diocese/categories/<int:pk>/edit/', views.diocese_category_edit, name='diocese_category_edit'),
    path('diocese/categories/<int:pk>/delete/', views.diocese_category_delete, name='diocese_category_delete'),
    
    # Diocese Contra Category URLs
    path('diocese/contra-categories/add/', views.diocese_contra_category_add, name='diocese_contra_category_add'),
    path('diocese/contra-categories/<int:pk>/edit/', views.diocese_contra_category_edit, name='diocese_contra_category_edit'),
    path('diocese/contra-categories/<int:pk>/delete/', views.diocese_contra_category_delete, name='diocese_contra_category_delete'),
    
    # Diocese Contra Transaction URLs
    path('diocese/<int:account_id>/transaction/contra/add/', views.diocese_transaction_add_contra, name='diocese_contra_add'),
    path('diocese/transaction/contra/<int:pk>/edit/', views.diocese_transaction_edit_contra, name='diocese_contra_edit'),
] 