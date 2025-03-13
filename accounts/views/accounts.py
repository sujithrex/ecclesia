from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Account, AccountType, Transaction, PrimaryCategory, SecondaryCategory

@login_required
def account_list(request):
    accounts = Account.objects.select_related('pastorate', 'church', 'account_type').all()
    return render(request, 'accounts/account/list.html', {'accounts': accounts})

@login_required
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    
    # Recalculate account balance on every page load
    # Calculate credits
    credits = Transaction.objects.filter(
        account=account,
        transaction_type__in=['receipt', 'offering', 'custom_credit', 'contra_credit', 'intra_credit']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate debits
    debits = Transaction.objects.filter(
        account=account,
        transaction_type__in=['bill', 'custom_debit', 'aqudence', 'contra', 'intra']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Update balance
    account.balance = credits - debits
    account.save()
    
    print(f"\n=== Auto-recalculated balance for {account.name} ===")
    print(f"Credits: {credits}")
    print(f"Debits: {debits}")
    print(f"Current Balance: {account.balance}")
    
    # Get all transactions for this account
    transactions = Transaction.objects.select_related(
        'account',
        'account__church',
        'account__account_type',
        'to_account',
        'to_account__church',
        'to_account__account_type',
        'from_account',
        'from_account__church',
        'from_account__account_type',
        'church',
        'primary_category',
        'secondary_category',
        'created_by'
    ).filter(
        # For sending account: show regular transactions and outgoing transfers (debit entries)
        (Q(account=account, transaction_type__in=['receipt', 'bill', 'aqudence', 'offering', 'custom_credit', 'custom_debit', 'contra']) |
        # For sending account: show only outgoing intra transfers
        Q(account=account, transaction_type='intra', to_account__isnull=False) |
        # For receiving account: show only incoming transfers (credit entries)
        Q(account=account, transaction_type__in=['contra_credit', 'intra_credit'], from_account__isnull=False))
    ).order_by('-date', '-created_at')
    
    # Apply filters
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = transactions.filter(
            Q(description__icontains=search_query) |
            Q(receipt_number__icontains=search_query) |
            Q(reference_number__icontains=search_query) |
            Q(family_name__icontains=search_query) |
            Q(member_name__icontains=search_query) |
            Q(church__church_name__icontains=search_query)
        )

    # Category filters
    primary_category_id = request.GET.get('primary_category')
    secondary_category_id = request.GET.get('secondary_category')
    if primary_category_id:
        transactions = transactions.filter(primary_category_id=primary_category_id)
    if secondary_category_id:
        transactions = transactions.filter(secondary_category_id=secondary_category_id)

    # Transaction type filter
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    # Calculate monthly statistics
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Regular credits (money received)
    regular_credits = transactions.filter(
        account=account,
        transaction_type__in=['receipt', 'offering', 'custom_credit'],
        date__range=[start_of_month, end_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Regular debits (money spent)
    regular_debits = transactions.filter(
        account=account,
        transaction_type__in=['bill', 'custom_debit', 'aqudence'],
        date__range=[start_of_month, end_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Contra debits (money sent)
    contra_debits = transactions.filter(
        account=account,
        transaction_type__in=['contra', 'intra'],
        date__range=[start_of_month, end_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Contra credits (money received)
    contra_credits = transactions.filter(
        account=account,
        transaction_type__in=['contra_credit', 'intra_credit'],
        date__range=[start_of_month, end_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate totals
    total_credits = regular_credits + contra_credits
    total_debits = regular_debits + contra_debits
    net_change = total_credits - total_debits
    
    context = {
        'account': account,
        'transactions': transactions,
        'monthly_stats': {
            'regular_credits': regular_credits,
            'regular_debits': regular_debits,
            'contra_credits': contra_credits,
            'contra_debits': contra_debits,
            'total_credits': total_credits,
            'total_debits': total_debits,
            'net_change': net_change,
            'start_date': start_of_month,
            'end_date': end_of_month,
        },
        'search_query': search_query,
        'selected_type': transaction_type,
        'selected_primary_category': primary_category_id,
        'selected_secondary_category': secondary_category_id,
        'primary_categories': PrimaryCategory.objects.all(),
        'secondary_categories': SecondaryCategory.objects.all(),
        'transaction_types': [
            ('receipt', 'Receipt'),
            ('bill', 'Bill'),
            ('aqudence', 'Aqudence'),
            ('offering', 'Church Offering'),
            ('custom_credit', 'Custom Credit'),
            ('custom_debit', 'Custom Debit'),
            ('contra', 'Contra Debit'),
            ('contra_credit', 'Contra Credit'),
            ('intra', 'Intra Debit'),
            ('intra_credit', 'Intra Credit'),
        ]
    }
    return render(request, 'accounts/account/detail.html', context)

@login_required
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk)
    
    if request.method == 'POST':
        try:
            account.name = request.POST.get('name')
            account.account_type = AccountType.objects.get(id=request.POST.get('account_type'))
            account.account_number = request.POST.get('account_number')
            account.description = request.POST.get('description')
            account.save()
            
            messages.success(request, 'Account updated successfully.')
            if account.level == 'pastorate':
                return redirect('accounts:pastorate_detail', pk=account.pastorate.id)
            else:
                return redirect('accounts:church_detail', pk=account.church.id)
        except Exception as e:
            messages.error(request, f'Error updating account: {str(e)}')
    
    account_types = AccountType.objects.all().order_by('name')
    context = {
        'account': account,
        'account_types': account_types,
    }
    return render(request, 'accounts/account/edit.html', context)

@login_required
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    
    if request.method == 'POST':
        try:
            # Store the redirect information before deleting
            level = account.level
            pastorate_id = account.pastorate.id if level == 'pastorate' else None
            church_id = account.church.id if level == 'church' else None
            
            account.delete()
            messages.success(request, 'Account deleted successfully.')
            
            # Redirect based on the account level
            if level == 'pastorate':
                return redirect('accounts:pastorate_detail', pk=pastorate_id)
            else:
                return redirect('accounts:church_detail', pk=church_id)
        except Exception as e:
            messages.error(request, f'Error deleting account: {str(e)}')
            return redirect('accounts:dashboard')
    
    context = {
        'account': account,
    }
    return render(request, 'accounts/account/delete.html', context)

@login_required
def account_report(request, pk):
    account = get_object_or_404(Account.objects.select_related(
        'pastorate', 'church', 'account_type'
    ), pk=pk)
    
    # Get date range from request
    try:
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    except (TypeError, ValueError):
        messages.error(request, 'Invalid date range provided')
        return redirect('accounts:account_detail', pk=pk)
    
    # Get all transactions within date range
    transactions = Transaction.objects.filter(
        account=account,
        date__range=[start_date, end_date]
    ).select_related(
        'account',
        'to_account',
        'from_account',
        'church',
        'primary_category',
        'secondary_category'
    ).order_by('date')

    # Initialize categories
    income_categories = {}
    expense_categories = {}
    
    # Process income transactions
    for trans in transactions.filter(transaction_type__in=['receipt', 'offering', 'custom_credit', 'contra_credit']):
        category_name = "Other Income"
        if trans.primary_category:
            category_name = trans.primary_category.name
        
        if category_name not in income_categories:
            income_categories[category_name] = []
        
        description = ""
        if trans.transaction_type == 'receipt':
            description = f"Receipt #{trans.receipt_number}"
            if trans.member_name:
                description += f" - {trans.member_name}"
                if trans.family_name:
                    description += f" ({trans.family_name})"
            elif trans.family_name:
                description += f" - {trans.family_name}"
        elif trans.transaction_type == 'offering':
            description = f"Church Offering"
            if trans.church:
                description += f" - {trans.church.church_name}"
        elif trans.transaction_type == 'contra_credit':
            description = f"Transfer from {trans.from_account.name}"
        else:  # custom_credit
            description = trans.description or "Custom Credit"
        
        if trans.secondary_category:
            description += f" ({trans.secondary_category.name})"
        
        income_categories[category_name].append({
            'description': description,
            'amount': trans.amount
        })
    
    # Process expense transactions
    for trans in transactions.filter(transaction_type__in=['bill', 'aqudence', 'custom_debit', 'contra']):
        category_name = "Other Expenses"
        if trans.primary_category:
            category_name = trans.primary_category.name
        
        if category_name not in expense_categories:
            expense_categories[category_name] = []
        
        description = ""
        if trans.transaction_type == 'bill':
            description = f"Bill #{trans.reference_number}"
            if trans.description:
                description += f" - {trans.description}"
        elif trans.transaction_type == 'aqudence':
            description = f"Aqudence #{trans.aqudence_number}"
            if trans.aqudence_ref:
                description += f" - {trans.aqudence_ref}"
        elif trans.transaction_type == 'contra':
            description = f"Transfer to {trans.to_account.name}"
        else:  # custom_debit
            description = trans.description or "Custom Debit"
        
        if trans.secondary_category:
            description += f" ({trans.secondary_category.name})"
        
        expense_categories[category_name].append({
            'description': description,
            'amount': trans.amount
        })

    # Calculate category totals
    income_totals = {
        category: sum(item['amount'] for item in items)
        for category, items in income_categories.items()
    }
    expense_totals = {
        category: sum(item['amount'] for item in items)
        for category, items in expense_categories.items()
    }

    # Calculate grand totals
    total_income = sum(income_totals.values())
    total_expenses = sum(expense_totals.values())
    net_balance = total_income - total_expenses

    context = {
        'account': account,
        'start_date': start_date,
        'end_date': end_date,
        'income_categories': income_categories,
        'expense_categories': expense_categories,
        'income_totals': income_totals,
        'expense_totals': expense_totals,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
    }
    return render(request, 'accounts/account/report.html', context) 