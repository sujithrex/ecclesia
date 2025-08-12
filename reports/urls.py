from django.urls import path
from . import views
from .views.family_report import family_report_form
from .views.birthday_report import generate_birthday_report, get_churches
from .views.wedding_report import generate_wedding_report

app_name = 'reports'

urlpatterns = [
    path('essentials/', views.essentials, name='essentials'),
    path('baptism-record/', views.baptism_record_form, name='baptism_record_form'),
    path('ripper-years/', views.ripper_years_form, name='ripper_years_form'),
    path('family-report/', family_report_form, name='family_report_form'),
    
    # Birthday report endpoints
    path('birthday-report/', generate_birthday_report, name='birthday_report'),
    path('api/churches/', get_churches, name='api_churches'),
    
    # Wedding report endpoints
    path('wedding-report/', generate_wedding_report, name='wedding_report'),
    
    # Audit report endpoints
    path('audit/', views.audit, name='audit'),
    path('audit/income-statement/', views.income_statement, name='income_statement'),
    path('audit/balance-sheet/', views.balance_sheet, name='balance_sheet'),
    path('audit/cash-flow/', views.cash_flow, name='cash_flow'),
    path('audit/donation-summary/', views.donation_summary, name='donation_summary'),
    path('audit/expense-analysis/', views.expense_analysis, name='expense_analysis'),
    path('audit/budget-vs-actual/', views.budget_vs_actual, name='budget_vs_actual'),
] 