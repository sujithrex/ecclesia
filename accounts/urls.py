from django.urls import path
from .views import transactions, categories
from .views.dashboard import dashboard
from .views.pastorates import pastorate_list, pastorate_detail, pastorate_account_add
from .views.churches import church_detail, church_account_add
from .views.accounts import account_detail, account_edit, account_delete, account_report
from .views.account_types import account_type_add, account_type_edit, account_type_delete

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    
    # Pastorate Level URLs
    path('pastorate/', pastorate_list, name='pastorate_list'),
    path('pastorate/<int:pk>/', pastorate_detail, name='pastorate_detail'),
    path('pastorate/<int:pastorate_id>/account/add/', pastorate_account_add, name='pastorate_account_add'),
    
    # Church Level URLs
    path('church/<int:pk>/', church_detail, name='church_detail'),
    path('church/<int:church_id>/account/add/', church_account_add, name='church_account_add'),
    
    # Account Management URLs
    path('account/<int:pk>/', account_detail, name='account_detail'),
    path('account/<int:pk>/edit/', account_edit, name='account_edit'),
    path('account/<int:pk>/delete/', account_delete, name='account_delete'),
    path('account/<int:pk>/report/', account_report, name='account_report'),
    
    # Account Type URLs
    path('account-type/add/', account_type_add, name='account_type_add'),
    path('account-type/<int:pk>/edit/', account_type_edit, name='account_type_edit'),
    path('account-type/<int:pk>/delete/', account_type_delete, name='account_type_delete'),
    
    # Category Management URLs
    path('categories/', categories.category_list, name='category_list'),
    path('categories/primary/add/', categories.primary_category_add, name='primary_category_add'),
    path('categories/primary/<int:pk>/edit/', categories.primary_category_edit, name='primary_category_edit'),
    path('categories/primary/<int:pk>/delete/', categories.primary_category_delete, name='primary_category_delete'),
    path('categories/secondary/add/', categories.secondary_category_add, name='secondary_category_add'),
    path('categories/secondary/<int:pk>/edit/', categories.secondary_category_edit, name='secondary_category_edit'),
    path('categories/secondary/<int:pk>/delete/', categories.secondary_category_delete, name='secondary_category_delete'),
    
    # Transaction URLs
    path('pastorate/<int:pastorate_id>/receipts/', transactions.receipt_list, name='receipt_list'),
    path('pastorate/<int:pastorate_id>/receipts/add/', transactions.receipt_add, name='receipt_add'),
    path('pastorate/<int:pastorate_id>/receipts/<int:pk>/', transactions.receipt_detail, name='receipt_detail'),
    path('pastorate/<int:pastorate_id>/receipts/<int:pk>/edit/', transactions.receipt_edit, name='receipt_edit'),
    path('pastorate/<int:pastorate_id>/receipts/<int:pk>/delete/', transactions.receipt_delete, name='receipt_delete'),
    
    path('pastorate/<int:pastorate_id>/bills/', transactions.bill_list, name='bill_list'),
    path('pastorate/<int:pastorate_id>/bills/add/', transactions.bill_add, name='bill_add'),
    path('pastorate/<int:pastorate_id>/bills/<int:pk>/', transactions.bill_detail, name='bill_detail'),
    path('pastorate/<int:pastorate_id>/bills/<int:pk>/edit/', transactions.bill_edit, name='bill_edit'),
    path('pastorate/<int:pastorate_id>/bills/<int:pk>/delete/', transactions.bill_delete, name='bill_delete'),
    
    path('pastorate/<int:pastorate_id>/aqudence/', transactions.aqudence_list, name='aqudence_list'),
    path('pastorate/<int:pastorate_id>/aqudence/add/', transactions.aqudence_add, name='aqudence_add'),
    path('pastorate/<int:pastorate_id>/aqudence/<int:pk>/', transactions.aqudence_detail, name='aqudence_detail'),
    path('pastorate/<int:pastorate_id>/aqudence/<int:pk>/edit/', transactions.aqudence_edit, name='aqudence_edit'),
    path('pastorate/<int:pastorate_id>/aqudence/<int:pk>/delete/', transactions.aqudence_delete, name='aqudence_delete'),
    
    path('pastorate/<int:pastorate_id>/offerings/', transactions.offering_list, name='offering_list'),
    path('pastorate/<int:pastorate_id>/offerings/add/', transactions.offering_add, name='offering_add'),
    path('pastorate/<int:pastorate_id>/offerings/<int:pk>/', transactions.offering_detail, name='offering_detail'),
    path('pastorate/<int:pastorate_id>/offerings/<int:pk>/edit/', transactions.offering_edit, name='offering_edit'),
    path('pastorate/<int:pastorate_id>/offerings/<int:pk>/delete/', transactions.offering_delete, name='offering_delete'),
    
    path('pastorate/<int:pastorate_id>/custom-debit/', transactions.custom_debit_list, name='custom_debit_list'),
    path('pastorate/<int:pastorate_id>/custom-debit/add/', transactions.custom_debit_add, name='custom_debit_add'),
    path('pastorate/<int:pastorate_id>/custom-debit/<int:pk>/', transactions.custom_debit_detail, name='custom_debit_detail'),
    path('pastorate/<int:pastorate_id>/custom-debit/<int:pk>/edit/', transactions.custom_debit_edit, name='custom_debit_edit'),
    path('pastorate/<int:pastorate_id>/custom-debit/<int:pk>/delete/', transactions.custom_debit_delete, name='custom_debit_delete'),
    
    path('pastorate/<int:pastorate_id>/custom-credit/', transactions.custom_credit_list, name='custom_credit_list'),
    path('pastorate/<int:pastorate_id>/custom-credit/add/', transactions.custom_credit_add, name='custom_credit_add'),
    path('pastorate/<int:pastorate_id>/custom-credit/<int:pk>/', transactions.custom_credit_detail, name='custom_credit_detail'),
    path('pastorate/<int:pastorate_id>/custom-credit/<int:pk>/edit/', transactions.custom_credit_edit, name='custom_credit_edit'),
    path('pastorate/<int:pastorate_id>/custom-credit/<int:pk>/delete/', transactions.custom_credit_delete, name='custom_credit_delete'),
    
    path('pastorate/<int:pastorate_id>/contra/', transactions.contra_list, name='contra_list'),
    path('pastorate/<int:pastorate_id>/contra/add/', transactions.contra_add, name='contra_add'),
    path('pastorate/<int:pastorate_id>/contra/<int:pk>/', transactions.contra_detail, name='contra_detail'),
    path('pastorate/<int:pastorate_id>/contra/<int:pk>/edit/', transactions.contra_edit, name='contra_edit'),
    path('pastorate/<int:pastorate_id>/contra/<int:pk>/delete/', transactions.contra_delete, name='contra_delete'),
    
    # Intra Transfer URLs
    path('pastorate/<int:pastorate_id>/intra/', transactions.intra_list, name='intra_list'),
    path('pastorate/<int:pastorate_id>/intra/add/', transactions.intra_add, name='intra_add'),
    path('pastorate/<int:pastorate_id>/intra/<int:pk>/', transactions.intra_detail, name='intra_detail'),
    path('pastorate/<int:pastorate_id>/intra/<int:pk>/edit/', transactions.intra_edit, name='intra_edit'),
    path('pastorate/<int:pastorate_id>/intra/<int:pk>/delete/', transactions.intra_delete, name='intra_delete'),
] 