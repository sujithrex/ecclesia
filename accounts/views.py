from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, ProtectedError
from django.db import transaction as db_transaction
from congregation.models import Pastorate, Church, Member, Family
from .models import (
    Account, 
    AccountType, 
    Transaction, 
    TransactionCategory, 
    TransactionDetail,
    TransactionHistory,
    LedgerGroup,
    DioceseCategory,
    DioceseTransaction,
    DioceseContraCategory
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.http import JsonResponse
from django.db.models import Sum, Case, When, F, DecimalField, Q
from django.db.models.functions import Coalesce

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
    
    # Add pastorates or churches to context based on account level
    if account.level == 'pastorate':
        context['pastorates'] = Pastorate.objects.all().order_by('pastorate_name')
    else:
        context['churches'] = Church.objects.filter(pastorate=account.pastorate).order_by('church_name')
    
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
    account = get_object_or_404(Account, pk=pk)
    
    # Check if it's a diocese account
    is_diocese_account = 'diocese' in account.name.lower()
    
    if is_diocese_account:
        transactions = DioceseTransaction.objects.filter(
            account=account
        ).select_related(
            'category',
            'contra_account',
            'created_by',
            'updated_by'
        ).order_by('-transaction_date', '-created_at')
        
        # Get monthly stats
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        monthly_transactions = transactions.filter(
            transaction_date__month=current_month,
            transaction_date__year=current_year
        )
        
        monthly_credits = monthly_transactions.filter(
            transaction_type='credit'
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        monthly_debits = monthly_transactions.filter(
            transaction_type='debit'
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        net_change = monthly_credits - monthly_debits
        
        # Calculate current balance
        total_credits = transactions.filter(
            transaction_type='credit'
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        total_debits = transactions.filter(
            transaction_type='debit'
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        current_balance = total_credits - total_debits
        
        # Update account balance
        account.balance = current_balance
        account.save()
    else:
        # Get current month's date range
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Get all transactions for this account
        transactions = Transaction.objects.filter(
            account=account
        ).select_related(
            'details',
            'details__category',
            'details__member',
            'details__family',
            'details__church',
            'created_by'
        ).order_by('-transaction_date', '-created_at')
        
        # Calculate monthly statistics
        monthly_transactions = transactions.filter(
            transaction_date__range=(start_of_month, end_of_month)
        )
        
        # Calculate monthly credits (including regular, contra, and custom transactions)
        monthly_credits = monthly_transactions.filter(
            Q(details__category__transaction_type='credit') |
            Q(details__isnull=True, transaction_type='credit') |
            Q(transaction_type='credit')  # For custom transactions
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # Calculate monthly debits (including regular, contra, and custom transactions)
        monthly_debits = monthly_transactions.filter(
            Q(details__category__transaction_type='debit') |
            Q(details__isnull=True, transaction_type='debit') |
            Q(transaction_type='debit')  # For custom transactions
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # Calculate net change
        net_change = monthly_credits - monthly_debits
        
        # Calculate current balance (including regular, contra, and custom transactions)
        total_credits = transactions.filter(
            Q(details__category__transaction_type='credit') |
            Q(details__isnull=True, transaction_type='credit') |
            Q(transaction_type='credit')  # For custom transactions
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        total_debits = transactions.filter(
            Q(details__category__transaction_type='debit') |
            Q(details__isnull=True, transaction_type='debit') |
            Q(transaction_type='debit')  # For custom transactions
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        current_balance = total_credits - total_debits
        
        # Update account balance
        account.balance = current_balance
        account.save()
    
    # Get transaction categories for filter
    categories = TransactionCategory.objects.filter(
        pastorate_only=False
    ).order_by('name')
    
    if account.level == 'pastorate':
        categories = categories | TransactionCategory.objects.filter(
            pastorate_only=True
        ).order_by('name')
    
    # Get categories by type
    receipt_categories = categories.filter(category_type='receipts')
    offertory_categories = categories.filter(category_type='offertory')
    bill_categories = categories.filter(category_type='bills')
    acquittance_categories = categories.filter(category_type='acquittance')
    ledger_categories = categories.filter(category_type='ledger')
    
    # Pagination
    paginator = Paginator(transactions, 10)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    
    context = {
        'account': account,
        'transactions': transactions,
        'monthly_credits': monthly_credits,
        'monthly_debits': monthly_debits,
        'net_change': net_change,
        'transaction_count': transactions.paginator.count,
        'is_diocese_account': is_diocese_account,
        'categories': categories,
        'receipt_categories': receipt_categories,
        'offertory_categories': offertory_categories,
        'bill_categories': bill_categories,
        'acquittance_categories': acquittance_categories,
        'ledger_categories': ledger_categories
    }
    return render(request, 'accounts/account/detail.html', context)

# Transaction Views
@login_required
def transaction_list(request):
    transactions = Transaction.objects.select_related('account').order_by('-transaction_date')
    return render(request, 'accounts/transaction/list.html', {'transactions': transactions})

@login_required
def transaction_add(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    
    # Define default category names to exclude - using exact names from database
    default_categories = ['Receipts', 'Bills and Vouchers', 'Church Offertory', 'Acquittance']
    
    # Get transaction categories based on account level, excluding default categories
    if account.level == 'pastorate':
        # For pastorate accounts, show all active custom categories
        categories = TransactionCategory.objects.filter(
            is_active=True
        ).exclude(
            name__in=default_categories
        ).order_by('name')
    else:
        # For other accounts, exclude pastorate-only and default categories
        categories = TransactionCategory.objects.filter(
            is_active=True,
            pastorate_only=False
        ).exclude(
            name__in=default_categories
        ).order_by('name')
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            # Parse the transaction date
            transaction_date = request.POST.get('transaction_date')
            transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            # Start a transaction to ensure data consistency
            with db_transaction.atomic():
                # Get the category and set transaction type from it
                category = TransactionCategory.objects.get(id=request.POST.get('category'))
                
                # Create the main transaction
                txn = Transaction.objects.create(
                    account=account,
                    transaction_type=category.transaction_type,
                    amount=Decimal(request.POST.get('amount', '0')),
                    transaction_date=transaction_date,
                    description=request.POST.get('description'),
                    created_by=request.user
                )
                
                # Create transaction details
                details = TransactionDetail.objects.create(
                    transaction=txn,
                    category=category
                )
                
                # Handle reference number if category requires it
                if category.requires_number:
                    details.reference_number = request.POST.get('reference_number')
                    details.save()
            
            messages.success(request, 'Transaction added successfully.')
            return redirect('accounts:account_detail', pk=account_id)
        except Exception as e:
            messages.error(request, f'Error creating transaction: {str(e)}')
    
    context = {
        'account': account,
        'categories': categories,
    }
    return render(request, 'accounts/transaction/add.html', context)

@login_required
def transaction_edit(request, pk):
    txn = get_object_or_404(Transaction.objects.select_related(
        'account', 'details', 'details__category', 'details__member', 'details__family', 'details__church'
    ), pk=pk)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Update main transaction
                txn.amount = Decimal(request.POST.get('amount', '0'))
                txn.description = request.POST.get('description')
                txn.transaction_date = request.POST.get('transaction_date')
                txn.save()
                
                # Update transaction details
                details = txn.details
                
                # Handle reference number based on category requirements
                if details.category.requires_number:
                    details.reference_number = request.POST.get('reference_number')
                
                # Handle church reference for offertory
                if details.category.requires_church:
                    church_id = request.POST.get('church')
                    if church_id:
                        details.church = Church.objects.get(pk=church_id)
                    else:
                        details.church = None
                
                # Handle member and family references for receipts
                if details.category.name == 'Receipts':
                    member_id = request.POST.get('member_id')
                    if member_id:
                        details.member = Member.objects.get(pk=member_id)
                        details.family = None
                    else:
                        details.member = None
                        family_id = request.POST.get('family_id')
                        if family_id:
                            details.family = Family.objects.get(pk=family_id)
                        else:
                            details.family = None
                
                details.save()
                
                messages.success(request, 'Transaction updated successfully.')
                return redirect('accounts:account_detail', pk=txn.account.id)
                
        except Exception as e:
            messages.error(request, f'Error updating transaction: {str(e)}')
    
    # Get churches if this is a pastorate account
    churches = None
    if txn.account.level == 'pastorate':
        churches = Church.objects.filter(pastorate=txn.account.pastorate)
    
    context = {
        'transaction': txn,
        'categories': TransactionCategory.objects.filter(is_active=True),
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
        category_type = request.POST.get('category_type')
        
        category = TransactionCategory.objects.create(
            name=name,
            transaction_type=transaction_type,
            category_type=category_type,
            is_active=True
        )
        
        messages.success(request, 'Category added successfully.')
        return redirect('web:essentials')
    
    return render(request, 'accounts/category/add.html')

@login_required
def category_edit(request, pk):
    category = get_object_or_404(TransactionCategory, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.transaction_type = request.POST.get('transaction_type')
        category.description = request.POST.get('description')
        category.save()
        
        messages.success(request, 'Category updated successfully.')
        return redirect('web:essentials')
    
    context = {
        'category': category
    }
    return render(request, 'accounts/category/edit.html', context)

@login_required
def category_delete(request, pk):
    category = get_object_or_404(TransactionCategory, pk=pk)
    
    try:
        category.delete()
        messages.success(request, 'Category deleted successfully.')
    except ProtectedError:
        messages.error(request, 'Cannot delete this category as it has transactions associated with it.')
    
    return redirect('web:essentials')

@login_required
def essentials(request):
    # Get all transaction categories including default ones
    categories = TransactionCategory.objects.all().order_by('name')
    
    # Get recent transaction history with related fields
    transaction_history = TransactionHistory.objects.select_related(
        'transaction',
        'transaction__details',
        'transaction__details__category'
    ).order_by('-created_at')[:10]
    
    context = {
        'categories': categories,
        'transaction_history': transaction_history,
    }
    return render(request, 'accounts/essentials.html', context)

@login_required
def search_members(request):
    search_term = request.GET.get('term', '')
    account_id = request.GET.get('account_id')
    
    if not search_term or not account_id:
        return JsonResponse({'results': []})
    
    try:
        account = Account.objects.get(pk=account_id)
        
        # Base query with death=False to exclude deceased members
        members = Member.objects.filter(death=False)
        families = Family.objects.all()
        
        # For both pastorate and church accounts, search all churches in the pastorate
        if account.level == 'pastorate':
            members = members.filter(
                family__area__church__pastorate=account.pastorate
            )
            families = families.filter(
                area__church__pastorate=account.pastorate
            )
        else:  # church level
            members = members.filter(
                family__area__church=account.church
            )
            families = families.filter(
                area__church=account.church
            )
        
        # Select related fields for optimization
        members = members.select_related(
            'family',
            'family__area',
            'family__area__church',
            'respect'
        )
        
        families = families.select_related(
            'area',
            'area__church',
            'respect'
        )
        
        # Search in member name, family head, and family details
        members = members.filter(
            Q(name__icontains=search_term) |
            Q(family__family_head__icontains=search_term)
        )
        
        families = families.filter(
            Q(family_head__icontains=search_term) |
            Q(family_id__icontains=search_term)
        )
        
        results = []
        
        # Add member results
        for member in members[:5]:  # Limit to 5 member results
            if account.level == 'pastorate':
                label = f"{member.respect.name} {member.name} - {member.family.area.area_name} - {member.family.area.church.church_name}"
            else:
                label = f"{member.respect.name} {member.name} - {member.family.area.area_name}"
            
            results.append({
                'id': f"m_{member.id}",  # Prefix with m_ to identify as member
                'label': label,
                'value': label,
                'type': 'member'
            })
        
        # Add family results
        for family in families[:5]:  # Limit to 5 family results
            if account.level == 'pastorate':
                label = f"{family.respect.name} {family.family_head}'s Family - {family.area.area_name} - {family.area.church.church_name}"
            else:
                label = f"{family.respect.name} {family.family_head}'s Family - {family.area.area_name}"
            
            results.append({
                'id': f"f_{family.id}",  # Prefix with f_ to identify as family
                'label': label,
                'value': label,
                'type': 'family'
            })
        
        return JsonResponse({'results': results})
    except Account.DoesNotExist:
        return JsonResponse({'results': []})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def transaction_add_receipt(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    receipt_category = TransactionCategory.objects.get(name='Receipts')
    
    # Get members and families based on account level
    if account.level == 'pastorate':
        members = Member.objects.filter(
            family__area__church__pastorate=account.pastorate,
            death=False
        ).select_related('family', 'family__area', 'family__area__church', 'respect')
        
        families = Family.objects.filter(
            area__church__pastorate=account.pastorate
        ).select_related('area', 'area__church', 'respect')
    else:
        members = Member.objects.filter(
            family__area__church=account.church,
            death=False
        ).select_related('family', 'family__area', 'family__area__church', 'respect')
        
        families = Family.objects.filter(
            area__church=account.church
        ).select_related('area', 'area__church', 'respect')
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            # Parse the transaction date
            transaction_date = request.POST.get('transaction_date')
            # Convert the date string to a date object
            transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            with db_transaction.atomic():
                # Create the main transaction
                new_transaction = Transaction.objects.create(
                    account=account,
                    transaction_type='credit',
                    amount=Decimal(request.POST.get('amount', '0')),
                    description=request.POST.get('description'),
                    transaction_date=transaction_date,
                    created_by=request.user
                )
                
                # Create transaction details
                TransactionDetail.objects.create(
                    transaction=new_transaction,
                    category=receipt_category,
                    reference_number=request.POST.get('reference_number'),
                    member_id=request.POST.get('member_id') if request.POST.get('member_id') else None,
                    family_id=request.POST.get('family_id') if request.POST.get('family_id') else None
                )
                
                messages.success(request, 'Receipt added successfully.')
                return redirect('accounts:account_detail', pk=account_id)
                
        except Exception as e:
            messages.error(request, f'Error adding receipt: {str(e)}')
    
    context = {
        'account': account,
        'receipt_category': receipt_category,
        'members': members.order_by('name'),
        'families': families.order_by('family_head')
    }
    return render(request, 'accounts/transaction/add_receipt.html', context)

@login_required
def transaction_add_offertory(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    if account.level != 'pastorate':
        messages.error(request, 'Church offertory can only be added to pastorate accounts.')
        return redirect('accounts:account_detail', pk=account_id)
    
    offertory_category = get_object_or_404(TransactionCategory, name='Church Offertory', is_active=True)
    churches = account.pastorate.church_set.all()
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            # Parse the transaction date
            transaction_date = request.POST.get('transaction_date')
            transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            # Start a transaction to ensure data consistency
            with db_transaction.atomic():
                # Create the main transaction
                txn = Transaction.objects.create(
                    account=account,
                    transaction_type=offertory_category.transaction_type,
                    amount=Decimal(request.POST.get('amount', '0')),
                    transaction_date=transaction_date,
                    description=request.POST.get('description'),
                    created_by=request.user
                )
                
                # Create transaction details with church reference
                details = TransactionDetail.objects.create(
                    transaction=txn,
                    category=offertory_category,
                    church_id=request.POST.get('church')
                )
            
            messages.success(request, 'Church offertory added successfully.')
            return redirect('accounts:account_detail', pk=account_id)
        except Exception as e:
            messages.error(request, f'Error creating church offertory: {str(e)}')
    
    context = {
        'account': account,
        'offertory_category': offertory_category,
        'churches': churches,
    }
    return render(request, 'accounts/transaction/add_offertory.html', context)

@login_required
def transaction_add_bill(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    bill_category = get_object_or_404(TransactionCategory, name='Bills and Vouchers', is_active=True)
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            # Parse the transaction date
            transaction_date = request.POST.get('transaction_date')
            transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            # Start a transaction to ensure data consistency
            with db_transaction.atomic():
                # Create the main transaction
                txn = Transaction.objects.create(
                    account=account,
                    transaction_type=bill_category.transaction_type,
                    amount=Decimal(request.POST.get('amount', '0')),
                    transaction_date=transaction_date,
                    description=request.POST.get('description'),
                    created_by=request.user
                )
                
                # Create transaction details with reference number
                details = TransactionDetail.objects.create(
                    transaction=txn,
                    category=bill_category,
                    reference_number=request.POST.get('reference_number')
                )
            
            messages.success(request, 'Bill/Voucher added successfully.')
            return redirect('accounts:account_detail', pk=account_id)
        except Exception as e:
            messages.error(request, f'Error creating bill/voucher: {str(e)}')
    
    context = {
        'account': account,
        'bill_category': bill_category,
    }
    return render(request, 'accounts/transaction/add_bill.html', context)

@login_required
def transaction_add_acquittance(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    if account.level != 'pastorate':
        messages.error(request, 'Acquittance can only be added to pastorate accounts.')
        return redirect('accounts:account_detail', pk=account_id)
    
    acquittance_category = get_object_or_404(TransactionCategory, name='Acquittance', is_active=True)
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            # Parse the transaction date
            transaction_date = request.POST.get('transaction_date')
            transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            # Start a transaction to ensure data consistency
            with db_transaction.atomic():
                # Create the main transaction
                txn = Transaction.objects.create(
                    account=account,
                    transaction_type=acquittance_category.transaction_type,
                    amount=Decimal(request.POST.get('amount', '0')),
                    transaction_date=transaction_date,
                    description=request.POST.get('description'),
                    created_by=request.user
                )
                
                # Create transaction details
                details = TransactionDetail.objects.create(
                    transaction=txn,
                    category=acquittance_category
                )
            
            messages.success(request, 'Acquittance added successfully.')
            return redirect('accounts:account_detail', pk=account_id)
        except Exception as e:
            messages.error(request, f'Error creating acquittance: {str(e)}')
    
    context = {
        'account': account,
        'acquittance_category': acquittance_category,
    }
    return render(request, 'accounts/transaction/add_acquittance.html', context)

@login_required
def transaction_view(request, pk):
    transaction = get_object_or_404(Transaction.objects.select_related(
        'account',
        'details',
        'details__category',
        'details__church',
        'details__member',
        'details__member__family',
        'details__member__respect',
        'details__family',
        'details__family__respect',
        'created_by'
    ), pk=pk)
    
    context = {
        'transaction': transaction,
        'history': transaction.history.select_related('modified_by').order_by('-modified_at')
    }
    return render(request, 'accounts/transaction/view.html', context)

@login_required
def transaction_edit_offertory(request, pk):
    txn = get_object_or_404(Transaction.objects.select_related(
        'account', 'details', 'details__category', 'details__church'
    ), pk=pk)
    
    # Verify this is an offertory transaction
    if txn.details.category.name != 'Church Offertory':
        messages.error(request, 'Invalid transaction type.')
        return redirect('accounts:account_detail', pk=txn.account.id)
    
    # Get churches for this pastorate
    churches = Church.objects.filter(pastorate=txn.account.pastorate)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Update main transaction
                txn.amount = Decimal(request.POST.get('amount', '0'))
                txn.description = request.POST.get('description')
                txn.transaction_date = request.POST.get('transaction_date')
                txn.save()
                
                # Update transaction details
                details = txn.details
                # No reference number for offertory
                details.reference_number = None
                
                # Handle church reference
                church_id = request.POST.get('church_id')
                if church_id:
                    details.church = Church.objects.get(pk=church_id)
                else:
                    details.church = None
                
                details.save()
                
                messages.success(request, 'Church offertory updated successfully.')
                return redirect('accounts:account_detail', pk=txn.account.id)
                
        except Exception as e:
            messages.error(request, f'Error updating church offertory: {str(e)}')
    
    context = {
        'transaction': txn,
        'offertory_category': txn.details.category,
        'churches': churches
    }
    return render(request, 'accounts/transaction/edit_offertory.html', context)

@login_required
def transaction_edit_bill(request, pk):
    txn = get_object_or_404(Transaction.objects.select_related(
        'account', 'details', 'details__category'
    ), pk=pk)
    
    # Verify this is a bill transaction
    if txn.details.category.name != 'Bills/Vouchers':
        messages.error(request, 'Invalid transaction type.')
        return redirect('accounts:account_detail', pk=txn.account.id)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Update main transaction
                txn.amount = Decimal(request.POST.get('amount', '0'))
                txn.description = request.POST.get('description')
                txn.transaction_date = request.POST.get('transaction_date')
                txn.save()
                
                # Update transaction details
                details = txn.details
                details.reference_number = request.POST.get('reference_number')
                details.save()
                
                messages.success(request, 'Bill/Voucher updated successfully.')
                return redirect('accounts:account_detail', pk=txn.account.id)
                
        except Exception as e:
            messages.error(request, f'Error updating bill/voucher: {str(e)}')
    
    context = {
        'transaction': txn,
        'bill_category': txn.details.category
    }
    return render(request, 'accounts/transaction/edit_bill.html', context)

@login_required
def transaction_edit_acquittance(request, pk):
    txn = get_object_or_404(Transaction.objects.select_related(
        'account', 'details', 'details__category'
    ), pk=pk)
    
    # Verify this is an acquittance transaction
    if txn.details.category.name != 'Acquittance':
        messages.error(request, 'Invalid transaction type.')
        return redirect('accounts:account_detail', pk=txn.account.id)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Update main transaction
                txn.amount = Decimal(request.POST.get('amount', '0'))
                txn.description = request.POST.get('description')
                txn.transaction_date = request.POST.get('transaction_date')
                txn.save()
                
                # Update transaction details
                details = txn.details
                # No reference number for acquittance
                details.reference_number = None
                details.save()
                
                messages.success(request, 'Acquittance updated successfully.')
                return redirect('accounts:account_detail', pk=txn.account.id)
                
        except Exception as e:
            messages.error(request, f'Error updating acquittance: {str(e)}')
    
    context = {
        'transaction': txn,
        'acquittance_category': txn.details.category
    }
    return render(request, 'accounts/transaction/edit_acquittance.html', context)

@login_required
def transaction_edit_receipt(request, pk):
    txn = get_object_or_404(Transaction.objects.select_related(
        'account', 'details', 'details__category', 'details__member', 'details__family'
    ), pk=pk)
    
    # Verify this is a receipt transaction
    if txn.details.category.name != 'Receipts':
        messages.error(request, 'Invalid transaction type.')
        return redirect('accounts:account_detail', pk=txn.account.id)
    
    # Get members and families based on account level
    if txn.account.level == 'pastorate':
        members = Member.objects.filter(
            family__area__church__pastorate=txn.account.pastorate,
            death=False
        ).select_related('family', 'family__area', 'family__area__church', 'respect')
        
        families = Family.objects.filter(
            area__church__pastorate=txn.account.pastorate
        ).select_related('area', 'area__church', 'respect')
    else:
        members = Member.objects.filter(
            family__area__church=txn.account.church,
            death=False
        ).select_related('family', 'family__area', 'family__area__church', 'respect')
        
        families = Family.objects.filter(
            area__church=txn.account.church
        ).select_related('area', 'area__church', 'respect')
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Update main transaction
                txn.amount = Decimal(request.POST.get('amount', '0'))
                txn.description = request.POST.get('description')
                txn.transaction_date = request.POST.get('transaction_date')
                txn.save()
                
                # Update transaction details
                details = txn.details
                details.reference_number = request.POST.get('reference_number')
                
                # Handle member and family references
                member_id = request.POST.get('member_id')
                if member_id:
                    details.member = Member.objects.get(pk=member_id)
                    details.family = None
                else:
                    details.member = None
                    
                family_id = request.POST.get('family_id')
                if family_id:
                    details.family = Family.objects.get(pk=family_id)
                    details.member = None
                else:
                    details.family = None
                
                details.save()
                
                messages.success(request, 'Receipt updated successfully.')
                return redirect('accounts:account_detail', pk=txn.account.id)
                
        except Exception as e:
            messages.error(request, f'Error updating receipt: {str(e)}')
    
    context = {
        'transaction': txn,
        'receipt_category': txn.details.category,
        'members': members.order_by('name'),
        'families': families.order_by('family_head')
    }
    return render(request, 'accounts/transaction/edit_receipt.html', context)

# Diocese Category Views
@login_required
def diocese_category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        transaction_type = request.POST.get('transaction_type')
        
        try:
            category = DioceseCategory.objects.create(
                name=name,
                transaction_type=transaction_type,
                is_active=True
            )
            messages.success(request, 'Diocese category created successfully.')
            return redirect('web:essentials')
        except Exception as e:
            messages.error(request, f'Error creating category: {str(e)}')
    
    return render(request, 'accounts/diocese/category/add.html')

@login_required
def diocese_category_edit(request, pk):
    category = get_object_or_404(DioceseCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.transaction_type = request.POST.get('transaction_type')
            category.is_active = request.POST.get('is_active') == 'on'
            category.save()
            
            messages.success(request, 'Diocese category updated successfully.')
            return redirect('web:essentials')
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
    
    return render(request, 'accounts/diocese/category/edit.html', {'category': category})

@login_required
def diocese_category_delete(request, pk):
    category = get_object_or_404(DioceseCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Diocese category deleted successfully.')
            return redirect('web:essentials')
        except ProtectedError:
            messages.error(request, 'Cannot delete category as it is being used in transactions.')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
    
    return render(request, 'accounts/diocese/category/delete.html', {'category': category})

# Diocese Transaction Views
@login_required
def diocese_transaction_add(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    categories = DioceseCategory.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            # Parse the transaction date
            transaction_date = request.POST.get('date')
            transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            with db_transaction.atomic():
                transaction = DioceseTransaction.objects.create(
                    account=account,
                    category=DioceseCategory.objects.get(id=request.POST.get('category')),
                    transaction_type=request.POST.get('transaction_type'),
                    amount=Decimal(request.POST.get('amount', '0')),
                    description=request.POST.get('description'),
                    transaction_date=transaction_date,
                    created_by=request.user
                )
            
            messages.success(request, 'Diocese transaction added successfully.')
            return redirect('accounts:diocese_transaction_view', pk=transaction.pk)
        except Exception as e:
            messages.error(request, f'Error adding transaction: {str(e)}')
    
    context = {
        'account': account,
        'categories': categories
    }
    return render(request, 'accounts/diocese/transaction/add.html', context)

@login_required
def diocese_transaction_add_contra(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    
    # Get active contra categories
    contra_categories = DioceseContraCategory.objects.filter(is_active=True)
    
    # Get cash and bank accounts for contra entries
    cash_account = Account.objects.filter(
        pastorate=account.pastorate,
        account_type__name='Cash Account'
    ).first()
    
    bank_account = Account.objects.filter(
        pastorate=account.pastorate,
        account_type__name='Bank Account'
    ).first()
    
    if request.method == 'POST':
        try:
            # Parse the transaction date
            transaction_date = request.POST.get('date')
            if transaction_date:
                transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            else:
                transaction_date = timezone.now().date()
            
            # Get the contra category
            contra_category = DioceseContraCategory.objects.get(id=request.POST.get('category'))
            
            # Get or create corresponding diocese category
            category, _ = DioceseCategory.objects.get_or_create(
                name=contra_category.name,
                defaults={
                    'transaction_type': contra_category.transaction_type,
                    'is_active': True
                }
            )
            
            # Get the transaction type from the category
            transaction_type = contra_category.transaction_type
            
            # Get the contra account
            contra_account = Account.objects.get(id=request.POST.get('contra_account'))
            
            amount = Decimal(request.POST.get('amount'))
            description = request.POST.get('description')
            
            # Create the transaction
            with db_transaction.atomic():
                # Create main transaction
                main_transaction = DioceseTransaction.objects.create(
                    account=account,
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    transaction_date=transaction_date,
                    is_contra=True,
                    contra_account=contra_account,
                    category=category,
                    created_by=request.user
                )
                
                # Create contra transaction with opposite transaction type
                contra_transaction_type = 'credit' if transaction_type == 'debit' else 'debit'
                DioceseTransaction.objects.create(
                    account=contra_account,
                    transaction_type=contra_transaction_type,
                    amount=amount,
                    description=f"Contra Entry - {description}",
                    transaction_date=transaction_date,
                    is_contra=True,
                    contra_account=account,
                    category=category,
                    created_by=request.user
                )
                
                # Update account balances
                if transaction_type == 'debit':
                    account.balance -= amount
                    contra_account.balance += amount
                else:
                    account.balance += amount
                    contra_account.balance -= amount
                
                account.save()
                contra_account.save()
            
            messages.success(request, 'Contra entry added successfully.')
            return redirect('accounts:account_detail', pk=account_id)
            
        except Exception as e:
            messages.error(request, f'Error creating contra entry: {str(e)}')
    
    context = {
        'account': account,
        'contra_categories': contra_categories,
        'cash_account': cash_account,
        'bank_account': bank_account,
    }
    return render(request, 'accounts/diocese/transaction/add_contra.html', context)

@login_required
def diocese_transaction_view(request, pk):
    transaction = get_object_or_404(
        DioceseTransaction.objects.select_related(
            'account',
            'category',
            'contra_account',
            'created_by',
            'updated_by'
        ),
        pk=pk
    )
    
    context = {
        'transaction': transaction
    }
    return render(request, 'accounts/diocese/transaction/view.html', context)

@login_required
def diocese_transaction_edit(request, pk):
    transaction = get_object_or_404(DioceseTransaction, pk=pk)
    
    if transaction.is_contra:
        # For contra entries, use contra categories
        categories = DioceseContraCategory.objects.filter(is_active=True).order_by('name')
    else:
        # For regular entries, use diocese categories
        categories = DioceseCategory.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            # Parse the transaction date
            transaction_date = request.POST.get('date')
            if transaction_date:
                transaction_date = timezone.datetime.strptime(transaction_date, '%Y-%m-%d').date()
            else:
                transaction_date = timezone.now().date()
            
            with db_transaction.atomic():
                if transaction.is_contra:
                    # Handle contra entry update
                    contra_category = DioceseContraCategory.objects.get(id=request.POST.get('category'))
                    category, _ = DioceseCategory.objects.get_or_create(
                        name=contra_category.name,
                        defaults={
                            'transaction_type': contra_category.transaction_type,
                            'is_active': True
                        }
                    )
                    transaction_type = contra_category.transaction_type
                else:
                    # Handle regular entry update
                    category = DioceseCategory.objects.get(id=request.POST.get('category'))
                    transaction_type = request.POST.get('transaction_type')
                
                amount = Decimal(request.POST.get('amount'))
                description = request.POST.get('description')
                
                # Update the transaction
                transaction.category = category
                transaction.transaction_type = transaction_type
                transaction.amount = amount
                transaction.description = description
                transaction.transaction_date = transaction_date
                transaction.updated_by = request.user
                transaction.save()
                
                # Update account balance
                if transaction.transaction_type == 'debit':
                    transaction.account.balance -= amount
                else:
                    transaction.account.balance += amount
                transaction.account.save()
                
                messages.success(request, 'Transaction updated successfully.')
                return redirect('accounts:account_detail', pk=transaction.account.id)
                
        except Exception as e:
            messages.error(request, f'Error updating transaction: {str(e)}')
    
    # Get cash and bank accounts for contra entries if needed
    cash_account = None
    bank_account = None
    if transaction.is_contra:
        cash_account = Account.objects.filter(
            pastorate=transaction.account.pastorate,
            account_type__name='Cash'
        ).first()
        
        bank_account = Account.objects.filter(
            pastorate=transaction.account.pastorate,
            account_type__name='Bank'
        ).first()
    
    context = {
        'transaction': transaction,
        'categories': categories,
        'cash_account': cash_account,
        'bank_account': bank_account
    }
    template = 'accounts/diocese/transaction/edit_contra.html' if transaction.is_contra else 'accounts/diocese/transaction/edit.html'
    return render(request, template, context)

@login_required
def diocese_transaction_delete(request, pk):
    transaction = get_object_or_404(DioceseTransaction, pk=pk)
    account_id = transaction.account.id
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Diocese transaction deleted successfully.')
            return redirect('accounts:account_detail', pk=account_id)
        except Exception as e:
            messages.error(request, f'Error deleting transaction: {str(e)}')
            return redirect('accounts:diocese_transaction_view', pk=pk)
    
    context = {
        'transaction': transaction
    }
    return render(request, 'accounts/diocese/transaction/delete.html', context)

@login_required
def diocese_account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    
    # Get all diocese transactions
    transactions = DioceseTransaction.objects.filter(
        account=account
    ).select_related(
        'category',
        'contra_account',
        'created_by',
        'updated_by'
    ).order_by('-transaction_date', '-created_at')
    
    # Get monthly stats
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    monthly_transactions = transactions.filter(
        transaction_date__month=current_month,
        transaction_date__year=current_year
    )
    
    monthly_credits = monthly_transactions.filter(
        transaction_type='credit'
    ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
    
    monthly_debits = monthly_transactions.filter(
        transaction_type='debit'
    ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
    
    net_change = monthly_credits - monthly_debits
    
    # Pagination
    paginator = Paginator(transactions, 10)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    
    context = {
        'account': account,
        'transactions': transactions,
        'monthly_credits': monthly_credits,
        'monthly_debits': monthly_debits,
        'net_change': net_change,
        'transaction_count': transactions.paginator.count
    }
    return render(request, 'accounts/diocese/account/detail.html', context)

@login_required
def diocese_contra_category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        transaction_type = request.POST.get('transaction_type')
        
        category = DioceseContraCategory.objects.create(
            name=name,
            transaction_type=transaction_type,
            is_active=True
        )
        
        messages.success(request, 'Contra category added successfully.')
        return redirect('web:essentials')
    
    return render(request, 'accounts/diocese/category/add_contra.html')

@login_required
def diocese_contra_category_edit(request, pk):
    category = get_object_or_404(DioceseContraCategory, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.transaction_type = request.POST.get('transaction_type')
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        
        messages.success(request, 'Contra category updated successfully.')
        return redirect('web:essentials')
    
    context = {
        'category': category
    }
    return render(request, 'accounts/diocese/category/edit_contra.html', context)

@login_required
def diocese_contra_category_delete(request, pk):
    category = get_object_or_404(DioceseContraCategory, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Contra category deleted successfully.')
    
    return redirect('web:essentials')

@login_required
def diocese_transaction_edit_contra(request, pk):
    """
    Edit a diocese contra transaction.
    This is specifically for contra entries that involve transfers between accounts.
    """
    # Get the transaction with all necessary related fields
    transaction = get_object_or_404(
        DioceseTransaction.objects.select_related(
            'account',
            'category',
            'contra_account',
            'created_by',
            'updated_by'
        ),
        pk=pk,
        is_contra=True  # Ensure we're only editing contra entries
    )
    
    # Get active contra categories
    categories = DioceseContraCategory.objects.filter(is_active=True).order_by('name')
    
    # Get cash and bank accounts for contra entries
    cash_account = Account.objects.filter(
        pastorate=transaction.account.pastorate,
        account_type__name='Cash Account',
        is_active=True
    ).exclude(id=transaction.account.id).first()
    
    bank_account = Account.objects.filter(
        pastorate=transaction.account.pastorate,
        account_type__name='Bank Account',
        is_active=True
    ).exclude(id=transaction.account.id).first()
    
    # Debug prints
    print("Transaction category:", transaction.category.id if transaction.category else None)
    print("Available categories:", [(c.id, c.name) for c in categories])
    print("Cash account:", cash_account.id if cash_account else None)
    print("Bank account:", bank_account.id if bank_account else None)
    print("Selected contra account:", transaction.contra_account.id if transaction.contra_account else None)
    
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Get form data
                category = DioceseContraCategory.objects.get(id=request.POST.get('category'))
                contra_account = Account.objects.get(id=request.POST.get('contra_account'))
                amount = Decimal(request.POST.get('amount'))
                description = request.POST.get('description')
                transaction_date = timezone.datetime.strptime(
                    request.POST.get('date') or timezone.now().strftime('%Y-%m-%d'),
                    '%Y-%m-%d'
                ).date()
                
                # Get or create corresponding diocese category
                diocese_category, _ = DioceseCategory.objects.get_or_create(
                    name=category.name,
                    defaults={
                        'transaction_type': category.transaction_type,
                        'is_active': True
                    }
                )
                
                # Get the linked contra transaction
                contra_transaction = DioceseTransaction.objects.get(
                    is_contra=True,
                    transaction_date=transaction.transaction_date,
                    contra_account=transaction.account,
                    account=transaction.contra_account
                )
                
                # Reverse old balances
                if transaction.transaction_type == 'debit':
                    transaction.account.balance += transaction.amount
                    transaction.contra_account.balance -= transaction.amount
                else:
                    transaction.account.balance -= transaction.amount
                    transaction.contra_account.balance += transaction.amount
                
                # Update main transaction
                transaction.category = diocese_category
                transaction.transaction_type = category.transaction_type
                transaction.amount = amount
                transaction.description = description
                transaction.transaction_date = transaction_date
                transaction.contra_account = contra_account
                transaction.updated_by = request.user
                transaction.save()
                
                # Update contra transaction
                contra_transaction_type = 'credit' if category.transaction_type == 'debit' else 'debit'
                contra_transaction.category = diocese_category
                contra_transaction.transaction_type = contra_transaction_type
                contra_transaction.amount = amount
                contra_transaction.description = f"Contra Entry - {description}"
                contra_transaction.transaction_date = transaction_date
                contra_transaction.contra_account = transaction.account
                contra_transaction.updated_by = request.user
                contra_transaction.save()
                
                # Apply new balances
                if category.transaction_type == 'debit':
                    transaction.account.balance -= amount
                    contra_account.balance += amount
                else:
                    transaction.account.balance += amount
                    contra_account.balance -= amount
                
                transaction.account.save()
                contra_account.save()
            
            messages.success(request, 'Contra entry updated successfully.')
            return redirect('accounts:account_detail', pk=transaction.account.id)
            
        except Exception as e:
            messages.error(request, f'Error updating contra entry: {str(e)}')
    
    context = {
        'transaction': transaction,
        'categories': categories,
        'cash_account': cash_account,
        'bank_account': bank_account
    }
    return render(request, 'accounts/diocese/transaction/edit_contra.html', context)

