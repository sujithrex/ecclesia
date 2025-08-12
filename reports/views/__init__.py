# This file makes the views directory a Python package
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .baptism_record import baptism_record_form
from .ripper_years import ripper_years_form
from .birthday_report import generate_birthday_report, get_churches
from .wedding_report import generate_wedding_report
from .audit import audit, income_statement, balance_sheet, cash_flow, donation_summary, expense_analysis, budget_vs_actual

@login_required
def essentials(request):
    context = {
        'title': 'Reports',
        'subtitle': 'Generate various reports and certificates'
    }
    return render(request, 'reports/essentials.html', context)

__all__ = [
    'essentials', 
    'baptism_record_form', 
    'ripper_years_form', 
    'generate_birthday_report', 
    'get_churches', 
    'generate_wedding_report',
    'audit',
    'income_statement',
    'balance_sheet',
    'cash_flow',
    'donation_summary',
    'expense_analysis',
    'budget_vs_actual'
] 