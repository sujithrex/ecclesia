from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from congregation.models import Pastorate, Church
from .models import (
    Account, 
    AccountType, 
    Transaction, 
    TransactionCategory, 
    TransactionDetail,
    TransactionHistory,
    LedgerGroup
)
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

@login_required
def dashboard(request):
    return redirect('accounts:pastorate_list')

@login_required
def pastorate_list(request):
    pastorates = Pastorate.objects.prefetch_related(
        'accounts',
        'church_set'
    ).order_by('pastorate_name')
    
    context = {
        'pastorates': pastorates,
    }
    return render(request, 'accounts/pastorate_list.html', context)

@login_required
def pastorate_detail(request, pk):
    pastorate = get_object_or_404(
        Pastorate.objects.prefetch_related(
            'accounts__account_type',
            'church_set__accounts'
        ),
        pk=pk
    )
    
    context = {
        'pastorate': pastorate,
    }
    return render(request, 'accounts/pastorate_detail.html', context)

@login_required
def pastorate_account_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        account_type = request.POST.get('account_type')
        account_number = request.POST.get('account_number')
        description = request.POST.get('description')
        
        try:
            account = Account()
            account.name = name
            account.account_type = AccountType.objects.get(id=account_type)
            account.account_number = account_number
            account.description = description
            account.level = 'pastorate'
            account.pastorate = pastorate
            account.save()
            
            messages.success(request, 'Pastorate account created successfully.')
            return redirect('accounts:pastorate_detail', pk=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    account_types = AccountType.objects.all().order_by('name')
    context = {
        'pastorate': pastorate,
        'account_types': account_types,
    }
    return render(request, 'accounts/pastorate_account_add.html', context)

@login_required
def church_detail(request, pk):
    church = get_object_or_404(
        Church.objects.select_related('pastorate').prefetch_related(
            'accounts__account_type'
        ),
        pk=pk
    )
    
    context = {
        'church': church,
    }
    return render(request, 'accounts/church_detail.html', context)

@login_required
def church_account_add(request, church_id):
    church = get_object_or_404(Church.objects.select_related('pastorate'), pk=church_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        account_type = request.POST.get('account_type')
        account_number = request.POST.get('account_number')
        description = request.POST.get('description')
        
        try:
            account = Account()
            account.name = name
            account.account_type = AccountType.objects.get(id=account_type)
            account.account_number = account_number
            account.description = description
            account.level = 'church'
            account.church = church
            account.save()
            
            messages.success(request, 'Church account created successfully.')
            return redirect('accounts:church_detail', pk=church_id)
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    account_types = AccountType.objects.all().order_by('name')
    context = {
        'church': church,
        'account_types': account_types,
    }
    return render(request, 'accounts/church_account_add.html', context)

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
    return render(request, 'accounts/account_edit.html', context)

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
    return render(request, 'accounts/account_delete.html', context)

# Account Type Views
@login_required
def account_type_list(request):
    account_types = AccountType.objects.all().order_by('name')
    return render(request, 'accounts/account_type/list.html', {'account_types': account_types})

@login_required
def account_type_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        try:
            account_type = AccountType.objects.create(
                name=name,
                description=description
            )
            messages.success(request, 'Account type created successfully.')
            return redirect('congregation:essentials')
        except Exception as e:
            messages.error(request, f'Error creating account type: {str(e)}')
    
    return render(request, 'accounts/account_type/add.html')

@login_required
def account_type_edit(request, pk):
    account_type = get_object_or_404(AccountType, pk=pk)
    
    if request.method == 'POST':
        try:
            account_type.name = request.POST.get('name')
            account_type.description = request.POST.get('description')
            account_type.save()
            
            messages.success(request, 'Account type updated successfully.')
            return redirect('congregation:essentials')
        except Exception as e:
            messages.error(request, f'Error updating account type: {str(e)}')
    
    return render(request, 'accounts/account_type/edit.html', {'account_type': account_type})

@login_required
def account_type_delete(request, pk):
    account_type = get_object_or_404(AccountType, pk=pk)
    
    if request.method == 'POST':
        try:
            account_type.delete()
            messages.success(request, 'Account type deleted successfully.')
            return redirect('congregation:essentials')
        except Exception as e:
            messages.error(request, f'Error deleting account type: {str(e)}')
    
    return render(request, 'accounts/account_type/delete.html', {'account_type': account_type})

# Account Views
@login_required
def account_list(request):
    accounts = Account.objects.select_related('pastorate', 'church', 'account_type').all()
    return render(request, 'accounts/account/list.html', {'accounts': accounts})

@login_required
def account_add(request):
    # Get level from URL parameter
    level = request.GET.get('level', 'pastorate')
    pastorate_id = request.GET.get('pastorate_id')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        account_type = request.POST.get('account_type')
        account_number = request.POST.get('account_number')
        description = request.POST.get('description')
        entity_id = request.POST.get('entity_id')
        
        try:
            account = Account()
            account.name = name
            account.account_type = AccountType.objects.get(id=account_type)
            account.account_number = account_number
            account.description = description
            account.level = level
            
            if level == 'pastorate':
                account.pastorate = Pastorate.objects.get(id=entity_id)
            else:
                account.church = Church.objects.get(id=entity_id)
                
            account.save()
            messages.success(request, 'Account created successfully.')
            return redirect('accounts:dashboard')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    # Get all pastorates and churches
    if level == 'pastorate':
        pastorates = Pastorate.objects.all().order_by('pastorate_name')
        context = {
            'level': level,
            'pastorates': pastorates,
        }
    else:
        # If pastorate_id is provided, get only churches from that pastorate
        if pastorate_id:
            pastorate = get_object_or_404(Pastorate, id=pastorate_id)
            churches = Church.objects.filter(pastorate=pastorate).order_by('church_name')
            context = {
                'level': level,
                'pastorate': pastorate,
                'churches': churches,
            }
        else:
            # If no pastorate_id, show pastorate selection first
            pastorates = Pastorate.objects.all().order_by('pastorate_name')
            context = {
                'level': level,
                'pastorates': pastorates,
                'select_pastorate': True,
            }
    
    account_types = AccountType.objects.all().order_by('name')
    context['account_types'] = account_types
    
    return render(request, 'accounts/account_add.html', context)

@login_required
def account_detail(request, pk):
    account = get_object_or_404(Account.objects.select_related(
        'pastorate', 'church', 'account_type'
    ), pk=pk)
    
    # Get monthly statistics
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    monthly_transactions = Transaction.objects.filter(
        account=account,
        transaction_date__range=(start_of_month, end_of_month)
    )
    
    total_credits = monthly_transactions.filter(transaction_type='credit').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    total_debits = monthly_transactions.filter(transaction_type='debit').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    monthly_stats = {
        'total_credits': total_credits,
        'total_debits': total_debits,
        'net_change': total_credits - total_debits,
        'transaction_count': monthly_transactions.count()
    }
    
    # Get paginated transactions
    transactions = Transaction.objects.select_related(
        'details', 'details__category', 'details__church'
    ).filter(account=account).order_by('-transaction_date')
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    context = {
        'account': account,
        'monthly_stats': monthly_stats,
        'transactions': transactions,
    }
    return render(request, 'accounts/account_detail.html', context)

# Transaction Views
@login_required
def transaction_list(request):
    transactions = Transaction.objects.select_related('account').order_by('-transaction_date')
    return render(request, 'accounts/transaction/list.html', {'transactions': transactions})

@login_required
def transaction_add(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    
    # Get churches for offertory if this is a pastorate account
    churches = []
    if account.level == 'pastorate':
        churches = account.pastorate.church_set.all()
    
    # Get transaction categories based on account level
    if account.level == 'pastorate':
        # For pastorate accounts, show all active categories
        categories = TransactionCategory.objects.filter(is_active=True).order_by('name')
    else:
        # For other accounts, exclude pastorate-only categories
        categories = TransactionCategory.objects.filter(
            is_active=True,
            pastorate_only=False
        ).order_by('name')
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            # Parse the transaction date
            transaction_date = request.POST.get('transaction_date')
            # Convert the date string to a date object
            transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            # Start a transaction to ensure data consistency
            from django.db import transaction as db_transaction
            with db_transaction.atomic():
                # Create the main transaction
                transaction = Transaction()
                transaction.account = account
                
                # Get the category and set transaction type from it
                category = TransactionCategory.objects.get(id=request.POST.get('category'))
                transaction.transaction_type = category.transaction_type
                
                transaction.amount = Decimal(request.POST.get('amount', '0'))
                transaction.transaction_date = transaction_date
                transaction.description = request.POST.get('description')
                transaction.created_by = request.user
                transaction.save()
                
                # Create transaction details
                details = TransactionDetail(transaction=transaction, category=category)
                
                # Add reference number if required
                if category.requires_number:
                    details.reference_number = request.POST.get('reference_number')
                
                # Add church reference if this is an offertory
                if category.requires_church:
                    church_id = request.POST.get('church')
                    if church_id:
                        details.church_id = church_id
                
                details.save()
            
            messages.success(request, 'Transaction created successfully.')
            return redirect('accounts:account_detail', pk=account_id)
        except ValueError as e:
            messages.error(request, f'Invalid data format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error creating transaction: {str(e)}')
    
    context = {
        'account': account,
        'categories': categories,
        'churches': churches,
    }
    return render(request, 'accounts/transaction_add.html', context)

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction.objects.select_related(
        'account',
        'details',
        'details__category',
        'details__church'
    ), pk=pk)
    
    # Get churches for offertory if this is a pastorate account
    churches = []
    if transaction.account.level == 'pastorate':
        churches = transaction.account.pastorate.church_set.all()
    
    # Get transaction categories based on account level
    if transaction.account.level == 'pastorate':
        # For pastorate accounts, show all active categories
        categories = TransactionCategory.objects.filter(is_active=True).order_by('name')
    else:
        # For other accounts, exclude pastorate-only categories
        categories = TransactionCategory.objects.filter(
            is_active=True,
            pastorate_only=False
        ).order_by('name')
    
    if request.method == 'POST':
        try:
            # Parse the transaction date
            transaction_date = request.POST.get('transaction_date')
            # Convert the date string to a datetime object at start of day
            aware_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d')
            aware_datetime = timezone.make_aware(aware_date)
            
            # Start a transaction to ensure data consistency
            from django.db import transaction as db_transaction
            with db_transaction.atomic():
                # Create history record before updating
                TransactionHistory.objects.create(
                    transaction=transaction,
                    amount=transaction.amount,
                    description=transaction.description,
                    transaction_type=transaction.transaction_type,
                    transaction_date=transaction.transaction_date,
                    modified_by=request.user
                )
                
                # Update the transaction
                if transaction.account.level == 'pastorate':
                    # Get the category and set transaction type from it
                    category = TransactionCategory.objects.get(id=request.POST.get('category'))
                    transaction.transaction_type = category.transaction_type
                    
                    # Update or create transaction details
                    details, created = TransactionDetail.objects.get_or_create(
                        transaction=transaction,
                        defaults={'category': category}
                    )
                    
                    if not created:
                        details.category = category
                    
                    # Update reference number if required
                    if category.requires_number:
                        details.reference_number = request.POST.get('reference_number')
                    else:
                        details.reference_number = None
                    
                    # Update church reference if this is an offertory
                    if category.requires_church:
                        church_id = request.POST.get('church')
                        details.church_id = church_id if church_id else None
                    else:
                        details.church = None
                    
                    details.save()
                else:
                    transaction.transaction_type = request.POST.get('transaction_type')
                
                transaction.amount = Decimal(request.POST.get('amount', '0'))
                transaction.transaction_date = aware_datetime
                transaction.description = request.POST.get('description')
                transaction.save()
            
            messages.success(request, 'Transaction updated successfully.')
            return redirect('accounts:account_detail', pk=transaction.account.id)
        except ValueError as e:
            messages.error(request, f'Invalid data format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error updating transaction: {str(e)}')
    
    context = {
        'transaction': transaction,
        'categories': categories,
        'churches': churches,
    }
    return render(request, 'accounts/transaction/edit.html', context)

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    account_id = transaction.account.id
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Transaction deleted successfully.')
            return redirect('accounts:account_detail', pk=account_id)
        except Exception as e:
            messages.error(request, f'Error deleting transaction: {str(e)}')
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction_delete.html', context)

@login_required
def transaction_history(request, pk):
    transaction = get_object_or_404(Transaction.objects.select_related('account'), pk=pk)
    history = transaction.history.select_related('modified_by').order_by('-modified_at')
    
    context = {
        'transaction': transaction,
        'history': history,
    }
    return render(request, 'accounts/transaction_history.html', context)

@login_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        transaction_type = request.POST.get('transaction_type')
        is_active = request.POST.get('is_active') == 'on'
        
        TransactionCategory.objects.create(
            name=name,
            category_type='custom',  # Custom category type for user-created categories
            transaction_type=transaction_type,
            is_active=is_active
        )
        
        messages.success(request, 'Transaction category created successfully.')
        return redirect('congregation:essentials')
    
    return render(request, 'accounts/category/add.html')

@login_required
def category_edit(request, pk):
    category = get_object_or_404(TransactionCategory, pk=pk)
    
    # Don't allow editing default categories
    if category.category_type != 'custom':
        messages.error(request, 'Default categories cannot be edited.')
        return redirect('congregation:essentials')
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.transaction_type = request.POST.get('transaction_type')
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        
        messages.success(request, 'Transaction category updated successfully.')
        return redirect('congregation:essentials')
    
    return render(request, 'accounts/category/edit.html', {'category': category})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(TransactionCategory, pk=pk)
    
    # Don't allow deleting default categories
    if category.category_type != 'custom':
        messages.error(request, 'Default categories cannot be deleted.')
        return redirect('congregation:essentials')
    
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Transaction category deleted successfully.')
        except ProtectedError:
            messages.error(request, 'This category cannot be deleted because it is being used by transactions.')
        return redirect('congregation:essentials')
    
    return render(request, 'accounts/category/delete.html', {'category': category})

@login_required
def essentials(request):
    account_types = AccountType.objects.all().order_by('name')
    categories = TransactionCategory.objects.all().order_by('name')
    transaction_history = TransactionHistory.objects.select_related(
        'transaction', 
        'modified_by'
    ).order_by('-modified_at')[:10]  # Get last 10 changes
    
    context = {
        'account_types': account_types,
        'categories': categories,
        'transaction_history': transaction_history,
    }
    return render(request, 'congregation/settings/essentials.html', context)
