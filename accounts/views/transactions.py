from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from ..models import Transaction, Account, PrimaryCategory, SecondaryCategory
from congregation.models import Pastorate, Church, Family, Member
from decimal import Decimal
from django.http import Http404

# Receipt Views
@login_required
def receipt_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all receipt transactions for this pastorate and its churches
    receipts = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='receipt'
    ).select_related(
        'account',
        'created_by',
        'primary_category',
        'secondary_category'
    ).order_by('-date')

    # Print debug information
    print("\nDEBUG - Receipt List:")
    print(f"Pastorate: {pastorate.pastorate_name}")
    print(f"Total receipts found: {receipts.count()}")
    print("Receipt details:")
    for receipt in receipts:
        print(f"- {receipt.date}: {receipt.amount} ({receipt.account.name})")

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        receipts = receipts.filter(
            Q(receipt_number__icontains=search_query) |
            Q(family_name__icontains=search_query) |
            Q(member_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(primary_category__name__icontains=search_query) |
            Q(secondary_category__name__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        receipts = receipts.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        receipts = receipts.filter(account_id=account_id)

    # Category filters
    primary_category_id = request.GET.get('primary_category')
    secondary_category_id = request.GET.get('secondary_category')
    if primary_category_id:
        receipts = receipts.filter(primary_category_id=primary_category_id)
    if secondary_category_id:
        receipts = receipts.filter(secondary_category_id=secondary_category_id)

    # Pagination
    paginator = Paginator(receipts, 10)  # Show 10 receipts per page
    page = request.GET.get('page')
    receipts = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'receipts': receipts,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='credit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='credit'),
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id,
        'selected_primary_category': primary_category_id,
        'selected_secondary_category': secondary_category_id,
    }
    return render(request, 'accounts/transaction/receipts/list.html', context)

@login_required
def receipt_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    primary_categories = PrimaryCategory.objects.filter(transaction_type='credit')
    secondary_categories = SecondaryCategory.objects.filter(primary_category__transaction_type='credit')
    
    # Get all families from churches in this pastorate
    families = Family.objects.filter(area__church__pastorate=pastorate).select_related('area', 'area__church')
    # Get all members from these families
    members = Member.objects.filter(family__area__church__pastorate=pastorate).select_related('family')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            receipt_number = request.POST.get('receipt_number')
            family_name = request.POST.get('family_name')
            member_name = request.POST.get('member_name')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Create the transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                date=date,
                receipt_number=receipt_number,
                family_name=family_name,
                member_name=member_name,
                description=description,
                transaction_type='receipt',
                primary_category=primary_category,
                secondary_category=secondary_category,
                created_by=request.user
            )

            messages.success(request, 'Receipt created successfully.')
            return redirect('accounts:receipt_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating receipt: {str(e)}')

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
        'families': families,
        'members': members,
        'today': timezone.now()
    }
    return render(request, 'accounts/transaction/receipts/add.html', context)

@login_required
def receipt_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'created_by',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='receipt'
    )
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/receipts/detail.html', context)

@login_required
def receipt_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='receipt'
    )
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    # Get all families from churches in this pastorate
    families = Family.objects.filter(area__church__pastorate=pastorate).select_related('area', 'area__church', 'respect')
    # Get all members from these families
    members = Member.objects.filter(family__area__church__pastorate=pastorate).select_related('family', 'respect')
    
    # Get categories
    primary_categories = PrimaryCategory.objects.filter(transaction_type='credit')
    secondary_categories = SecondaryCategory.objects.filter(
        Q(primary_category=transaction.primary_category) |
        Q(primary_category__transaction_type='credit')
    ).select_related('primary_category').distinct()

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            receipt_number = request.POST.get('receipt_number')
            family_name = request.POST.get('family_name')
            member_name = request.POST.get('member_name')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Update the transaction
            transaction.account = account
            transaction.amount = amount
            transaction.date = date
            transaction.receipt_number = receipt_number
            transaction.family_name = family_name
            transaction.member_name = member_name
            transaction.description = description
            transaction.primary_category = primary_category
            transaction.secondary_category = secondary_category
            transaction.save()

            messages.success(request, 'Receipt updated successfully.')
            return redirect('accounts:receipt_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating receipt: {str(e)}')

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'accounts': accounts,
        'families': families,
        'members': members,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/transaction/receipts/edit.html', context)

@login_required
def receipt_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction.objects.select_related('account'), pk=pk)
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Receipt deleted successfully.')
            return redirect('accounts:receipt_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting receipt: {str(e)}')
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/receipts/delete.html', context)

@login_required
def bill_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all bill transactions for this pastorate and its churches
    bills = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='bill'
    ).select_related(
        'account',
        'created_by',
        'primary_category',
        'secondary_category'
    ).order_by('-date')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        bills = bills.filter(
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(primary_category__name__icontains=search_query) |
            Q(secondary_category__name__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        bills = bills.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        bills = bills.filter(account_id=account_id)

    # Category filters
    primary_category_id = request.GET.get('primary_category')
    secondary_category_id = request.GET.get('secondary_category')
    if primary_category_id:
        bills = bills.filter(primary_category_id=primary_category_id)
    if secondary_category_id:
        bills = bills.filter(secondary_category_id=secondary_category_id)

    # Pagination
    paginator = Paginator(bills, 10)  # Show 10 bills per page
    page = request.GET.get('page')
    bills = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'bills': bills,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='debit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='debit'),
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id,
        'selected_primary_category': primary_category_id,
        'selected_secondary_category': secondary_category_id,
    }
    return render(request, 'accounts/transaction/bills/list.html', context)

@login_required
def bill_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    primary_categories = PrimaryCategory.objects.filter(transaction_type='debit')
    secondary_categories = SecondaryCategory.objects.filter(primary_category__transaction_type='debit')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Create the transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=description,
                transaction_type='bill',
                primary_category=primary_category,
                secondary_category=secondary_category,
                created_by=request.user
            )

            messages.success(request, 'Bill created successfully.')
            return redirect('accounts:bill_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating bill: {str(e)}')

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
        'today': timezone.now()
    }
    return render(request, 'accounts/transaction/bills/add.html', context)

@login_required
def bill_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'church',
            'created_by'
        ),
        pk=pk,
        transaction_type='bill'
    )
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/bills/detail.html', context)

@login_required
def bill_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='bill'
    )
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    # Get categories
    primary_categories = PrimaryCategory.objects.filter(transaction_type='debit')
    # Get all secondary categories for the current primary category and other debit categories
    secondary_categories = SecondaryCategory.objects.filter(
        Q(primary_category=transaction.primary_category) |
        Q(primary_category__transaction_type='debit')
    ).select_related('primary_category').distinct()

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Update the transaction
            transaction.account = account
            transaction.amount = amount
            transaction.date = date
            transaction.reference_number = reference_number
            transaction.description = description
            transaction.primary_category = primary_category
            transaction.secondary_category = secondary_category
            transaction.save()

            messages.success(request, 'Bill updated successfully.')
            return redirect('accounts:bill_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating bill: {str(e)}')

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/transaction/bills/edit.html', context)

@login_required
def bill_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction.objects.select_related('account'), pk=pk)
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Bill deleted successfully.')
            return redirect('accounts:bill_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting bill: {str(e)}')
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/bills/delete.html', context)

# Aqudence Views
@login_required
def aqudence_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all aqudence transactions for this pastorate and its churches
    aqudences = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='aqudence'
    ).select_related(
        'account',
        'created_by',
        'primary_category',
        'secondary_category'
    ).order_by('-date')

    # Print debug information
    print("\nDEBUG - Aqudence List:")
    print(f"Pastorate: {pastorate.pastorate_name}")
    print(f"Total aqudence entries found: {aqudences.count()}")
    print("Aqudence details:")
    for entry in aqudences:
        print(f"- {entry.date}: {entry.amount} ({entry.account.name})")

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        aqudences = aqudences.filter(
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(primary_category__name__icontains=search_query) |
            Q(secondary_category__name__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        aqudences = aqudences.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        aqudences = aqudences.filter(account_id=account_id)

    # Category filters
    primary_category_id = request.GET.get('primary_category')
    secondary_category_id = request.GET.get('secondary_category')
    if primary_category_id:
        aqudences = aqudences.filter(primary_category_id=primary_category_id)
    if secondary_category_id:
        aqudences = aqudences.filter(secondary_category_id=secondary_category_id)

    # Pagination
    paginator = Paginator(aqudences, 10)  # Show 10 aqudence entries per page
    page = request.GET.get('page')
    aqudences = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'aqudences': aqudences,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='debit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='debit'),
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id,
        'selected_primary_category': primary_category_id,
        'selected_secondary_category': secondary_category_id,
    }
    return render(request, 'accounts/transaction/aqudence/list.html', context)

@login_required
def aqudence_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    primary_categories = PrimaryCategory.objects.filter(transaction_type='debit')
    secondary_categories = SecondaryCategory.objects.filter(primary_category__transaction_type='debit')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Create the transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=description,
                transaction_type='aqudence',
                primary_category=primary_category,
                secondary_category=secondary_category,
                created_by=request.user
            )

            messages.success(request, 'Aqudence created successfully.')
            return redirect('accounts:aqudence_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating aqudence: {str(e)}')

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
        'today': timezone.now()
    }
    return render(request, 'accounts/transaction/aqudence/add.html', context)

@login_required
def aqudence_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'church',
            'created_by'
        ),
        pk=pk,
        transaction_type='aqudence'
    )
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/aqudence/detail.html', context)

@login_required
def aqudence_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='aqudence'
    )
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    # Get categories
    primary_categories = PrimaryCategory.objects.filter(transaction_type='debit')
    # Get all secondary categories for the current primary category and other debit categories
    secondary_categories = SecondaryCategory.objects.filter(
        Q(primary_category=transaction.primary_category) |
        Q(primary_category__transaction_type='debit')
    ).select_related('primary_category').distinct()

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Update the transaction
            transaction.account = account
            transaction.amount = amount
            transaction.date = date
            transaction.reference_number = reference_number
            transaction.description = description
            transaction.primary_category = primary_category
            transaction.secondary_category = secondary_category
            transaction.save()

            messages.success(request, 'Aqudence updated successfully.')
            return redirect('accounts:aqudence_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating aqudence: {str(e)}')

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/transaction/aqudence/edit.html', context)

@login_required
def aqudence_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction.objects.select_related('account'), pk=pk)
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Aqudence deleted successfully.')
            return redirect('accounts:aqudence_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting aqudence: {str(e)}')
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/aqudence/delete.html', context)

# Offering Views
@login_required
def offering_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all offering transactions for this pastorate and its churches
    offerings = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='offering'
    ).select_related(
        'account',
        'church',
        'created_by',
        'primary_category',
        'secondary_category'
    ).order_by('-date')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        offerings = offerings.filter(
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(primary_category__name__icontains=search_query) |
            Q(secondary_category__name__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        offerings = offerings.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        offerings = offerings.filter(account_id=account_id)

    # Category filters
    primary_category_id = request.GET.get('primary_category')
    secondary_category_id = request.GET.get('secondary_category')
    if primary_category_id:
        offerings = offerings.filter(primary_category_id=primary_category_id)
    if secondary_category_id:
        offerings = offerings.filter(secondary_category_id=secondary_category_id)

    # Pagination
    paginator = Paginator(offerings, 10)  # Show 10 offerings per page
    page = request.GET.get('page')
    offerings = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'offerings': offerings,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='credit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='credit'),
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id,
        'selected_primary_category': primary_category_id,
        'selected_secondary_category': secondary_category_id,
    }
    return render(request, 'accounts/transaction/offerings/list.html', context)

@login_required
def offering_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    # Get churches in this pastorate
    churches = Church.objects.filter(pastorate=pastorate).order_by('church_name')
    
    primary_categories = PrimaryCategory.objects.filter(transaction_type='credit')
    secondary_categories = SecondaryCategory.objects.filter(primary_category__transaction_type='credit')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))
            church = get_object_or_404(Church, pk=request.POST.get('church'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Create the transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=description,
                transaction_type='offering',
                primary_category=primary_category,
                secondary_category=secondary_category,
                church=church,
                created_by=request.user
            )

            messages.success(request, 'Offering created successfully.')
            return redirect('accounts:offering_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating offering: {str(e)}')

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'churches': churches,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
        'today': timezone.now()
    }
    return render(request, 'accounts/transaction/offerings/add.html', context)

@login_required
def offering_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'church',
            'created_by'
        ),
        pk=pk,
        transaction_type='offering'
    )
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/offerings/detail.html', context)

@login_required
def offering_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='offering'
    )
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')
    
    # Get categories
    primary_categories = PrimaryCategory.objects.filter(transaction_type='credit')
    # Get all secondary categories for the current primary category and other credit categories
    secondary_categories = SecondaryCategory.objects.filter(
        Q(primary_category=transaction.primary_category) |
        Q(primary_category__transaction_type='credit')
    ).select_related('primary_category').distinct()

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Update the transaction
            transaction.account = account
            transaction.amount = amount
            transaction.date = date
            transaction.reference_number = reference_number
            transaction.description = description
            transaction.primary_category = primary_category
            transaction.secondary_category = secondary_category
            transaction.save()

            messages.success(request, 'Offering updated successfully.')
            return redirect('accounts:offering_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating offering: {str(e)}')

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/transaction/offerings/edit.html', context)

@login_required
def offering_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction.objects.select_related('account'), pk=pk)
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Offering deleted successfully.')
            return redirect('accounts:offering_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting offering: {str(e)}')
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/offerings/delete.html', context)

@login_required
def custom_debit_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all custom debit transactions for this pastorate and its churches
    debits = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='custom_debit'
    ).select_related(
        'account',
        'created_by',
        'primary_category',
        'secondary_category'
    ).order_by('-date')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        debits = debits.filter(
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(primary_category__name__icontains=search_query) |
            Q(secondary_category__name__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        debits = debits.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        debits = debits.filter(account_id=account_id)

    # Category filters
    primary_category_id = request.GET.get('primary_category')
    secondary_category_id = request.GET.get('secondary_category')
    if primary_category_id:
        debits = debits.filter(primary_category_id=primary_category_id)
    if secondary_category_id:
        debits = debits.filter(secondary_category_id=secondary_category_id)

    # Pagination
    paginator = Paginator(debits, 10)  # Show 10 debits per page
    page = request.GET.get('page')
    debits = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'debits': debits,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='debit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='debit'),
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id,
        'selected_primary_category': primary_category_id,
        'selected_secondary_category': secondary_category_id,
    }
    return render(request, 'accounts/transaction/custom/debit/list.html', context)

@login_required
def custom_debit_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Create the transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=description,
                transaction_type='custom_debit',
                primary_category=primary_category,
                secondary_category=secondary_category,
                created_by=request.user
            )

            messages.success(request, 'Custom debit created successfully.')
            return redirect('accounts:custom_debit_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating custom debit: {str(e)}')

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='debit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='debit'),
        'today': timezone.now()
    }
    return render(request, 'accounts/transaction/custom/debit/add.html', context)

@login_required
def custom_debit_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'created_by',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='custom_debit'
    )
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/custom/debit/detail.html', context)

@login_required
def custom_debit_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='custom_debit'
    )
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Update the transaction
            transaction.account = account
            transaction.amount = amount
            transaction.date = date
            transaction.reference_number = reference_number
            transaction.description = description
            transaction.primary_category = primary_category
            transaction.secondary_category = secondary_category
            transaction.save()

            messages.success(request, 'Custom debit updated successfully.')
            return redirect('accounts:custom_debit_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating custom debit: {str(e)}')

    # Get categories
    primary_categories = PrimaryCategory.objects.filter(transaction_type='debit')
    # Get all secondary categories for the current primary category and other debit categories
    secondary_categories = SecondaryCategory.objects.filter(
        Q(primary_category=transaction.primary_category) |
        Q(primary_category__transaction_type='debit')
    ).select_related('primary_category').distinct()

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/transaction/custom/debit/edit.html', context)

@login_required
def custom_debit_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction, pk=pk, transaction_type='custom_debit')
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Custom debit deleted successfully.')
            return redirect('accounts:custom_debit_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting custom debit: {str(e)}')
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/custom/debit/delete.html', context)

@login_required
def custom_credit_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all custom credit transactions for this pastorate and its churches
    credits = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='custom_credit'
    ).select_related(
        'account',
        'created_by',
        'primary_category',
        'secondary_category'
    ).order_by('-date')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        credits = credits.filter(
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(primary_category__name__icontains=search_query) |
            Q(secondary_category__name__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        credits = credits.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        credits = credits.filter(account_id=account_id)

    # Category filters
    primary_category_id = request.GET.get('primary_category')
    secondary_category_id = request.GET.get('secondary_category')
    if primary_category_id:
        credits = credits.filter(primary_category_id=primary_category_id)
    if secondary_category_id:
        credits = credits.filter(secondary_category_id=secondary_category_id)

    # Pagination
    paginator = Paginator(credits, 10)  # Show 10 credits per page
    page = request.GET.get('page')
    credits = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'credits': credits,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='credit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='credit'),
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id,
        'selected_primary_category': primary_category_id,
        'selected_secondary_category': secondary_category_id,
    }
    return render(request, 'accounts/transaction/custom/credit/list.html', context)

@login_required
def custom_credit_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Create the transaction
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=description,
                transaction_type='custom_credit',
                primary_category=primary_category,
                secondary_category=secondary_category,
                created_by=request.user
            )

            messages.success(request, 'Custom credit created successfully.')
            return redirect('accounts:custom_credit_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating custom credit: {str(e)}')

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'primary_categories': PrimaryCategory.objects.filter(transaction_type='credit'),
        'secondary_categories': SecondaryCategory.objects.filter(primary_category__transaction_type='credit'),
        'today': timezone.now()
    }
    return render(request, 'accounts/transaction/custom/credit/add.html', context)

@login_required
def custom_credit_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'created_by',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='custom_credit'
    )
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/custom/credit/detail.html', context)

@login_required
def custom_credit_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='custom_credit'
    )
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    if request.method == 'POST':
        try:
            # Get form data
            account = get_object_or_404(Account, pk=request.POST.get('account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Validate categories
            if secondary_category.primary_category != primary_category:
                raise ValueError("Selected secondary category does not belong to the selected primary category")

            # Update the transaction
            transaction.account = account
            transaction.amount = amount
            transaction.date = date
            transaction.reference_number = reference_number
            transaction.description = description
            transaction.primary_category = primary_category
            transaction.secondary_category = secondary_category
            transaction.save()

            messages.success(request, 'Custom credit updated successfully.')
            return redirect('accounts:custom_credit_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating custom credit: {str(e)}')

    # Get categories
    primary_categories = PrimaryCategory.objects.filter(transaction_type='credit')
    # Get all secondary categories for the current primary category and other credit categories
    secondary_categories = SecondaryCategory.objects.filter(
        Q(primary_category=transaction.primary_category) |
        Q(primary_category__transaction_type='credit')
    ).select_related('primary_category').distinct()

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/transaction/custom/credit/edit.html', context)

@login_required
def custom_credit_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction, pk=pk, transaction_type='custom_credit')
    
    if request.method == 'POST':
        try:
            transaction.delete()
            messages.success(request, 'Custom credit deleted successfully.')
            return redirect('accounts:custom_credit_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting custom credit: {str(e)}')
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
    }
    return render(request, 'accounts/transaction/custom/credit/delete.html', context)

@login_required
def contra_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get only contra debit transactions for this pastorate and its churches
    transactions = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='contra'  # Only get debit entries
    ).select_related(
        'account',
        'to_account',
        'created_by'
    ).order_by('-date')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = transactions.filter(
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        transactions = transactions.filter(
            Q(account_id=account_id) | Q(to_account_id=account_id)
        )

    # Pagination
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page = request.GET.get('page')
    transactions = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'transactions': transactions,
        'accounts': accounts,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id
    }
    return render(request, 'accounts/transaction/contra/list.html', context)

@login_required
def contra_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    if request.method == 'POST':
        try:
            # Get form data
            from_account = get_object_or_404(Account, pk=request.POST.get('from_account'))
            to_account = get_object_or_404(Account, pk=request.POST.get('to_account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')

            print("\n=== Creating New Contra Entry ===")
            print(f"From Account: {from_account.id} - {from_account.name}")
            print(f"To Account: {to_account.id} - {to_account.name}")
            print(f"Amount: {amount}")
            print(f"Date: {date}")
            print(f"Reference: {reference_number}")
            print(f"Description: {description}")

            # Create the contra transaction (debit entry)
            debit_transaction = Transaction.objects.create(
                account=from_account,
                to_account=to_account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=f"Contra Entry (Debit) - {description}",
                transaction_type='contra',
                created_by=request.user
            )
            print(f"\nCreated DEBIT entry:")
            print(f"ID: {debit_transaction.id}")
            print(f"Type: {debit_transaction.transaction_type}")
            print(f"From: {debit_transaction.account.id} - {debit_transaction.account.name}")
            print(f"To: {debit_transaction.to_account.id} - {debit_transaction.to_account.name}")
            print(f"Reference: {debit_transaction.reference_number}")

            # Create the corresponding credit entry
            credit_transaction = Transaction.objects.create(
                account=to_account,
                from_account=from_account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=f"Contra Entry (Credit) - {description}",
                transaction_type='contra_credit',
                created_by=request.user
            )
            print(f"\nCreated CREDIT entry:")
            print(f"ID: {credit_transaction.id}")
            print(f"Type: {credit_transaction.transaction_type}")
            print(f"Account: {credit_transaction.account.id} - {credit_transaction.account.name}")
            print(f"From: {credit_transaction.from_account.id} - {credit_transaction.from_account.name}")
            print(f"Reference: {credit_transaction.reference_number}")
            print("=== Contra Entry Creation Complete ===\n")

            messages.success(request, 'Contra entry created successfully.')
            return redirect('accounts:contra_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating contra entry: {str(e)}')
            print(f"Error in contra creation: {str(e)}")  # Debug log

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'today': timezone.now()
    }
    return render(request, 'accounts/transaction/contra/add.html', context)

@login_required
def contra_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Try to get either the debit or credit entry
    try:
        transaction = Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account',
            'created_by'
        ).get(
            pk=pk,
            transaction_type__in=['contra', 'contra_credit']
        )
    except Transaction.DoesNotExist:
        raise Http404("Transaction not found")
    
    # If this is a credit entry, get the corresponding debit entry
    if transaction.transaction_type == 'contra_credit':
        credit_entry = transaction
        debit_entry = Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account'
        ).filter(
            transaction_type='contra',
            account=transaction.from_account,
            to_account=transaction.account,
            date=transaction.date,
            amount=transaction.amount
        ).first()
        if debit_entry:
            transaction = debit_entry
        else:
            raise Http404("Corresponding debit entry not found")
    # If this is a debit entry, get the corresponding credit entry
    else:
        credit_entry = Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account'
        ).filter(
            transaction_type='contra_credit',
            from_account=transaction.account,
            to_account=transaction.to_account,
            date=transaction.date,
            amount=transaction.amount
        ).first()
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'credit_entry': credit_entry,
    }
    return render(request, 'accounts/transaction/contra/detail.html', context)

@login_required
def contra_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account'
        ),
        pk=pk,
        transaction_type='contra'
    )
    
    # Get the corresponding credit entry
    credit_entry = Transaction.objects.select_related(
        'account',
        'to_account',
        'from_account'
    ).filter(
        transaction_type='contra_credit',
        from_account=transaction.account,
        to_account=transaction.to_account,
        date=transaction.date,
        amount=transaction.amount
    ).first()
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    if request.method == 'POST':
        try:
            # Get form data
            from_account = get_object_or_404(Account, pk=request.POST.get('from_account'))
            to_account = get_object_or_404(Account, pk=request.POST.get('to_account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')

            # Update the debit transaction
            transaction.account = from_account
            transaction.to_account = to_account
            transaction.amount = amount
            transaction.date = date
            transaction.reference_number = reference_number
            transaction.description = f"Contra Entry (Debit) - {description}"
            transaction.save()

            # Update the credit transaction
            if credit_entry:
                credit_entry.account = to_account
                credit_entry.from_account = from_account
                credit_entry.amount = amount
                credit_entry.date = date
                credit_entry.reference_number = reference_number
                credit_entry.description = f"Contra Entry (Credit) - {description}"
                credit_entry.save()

            messages.success(request, 'Contra entry updated successfully.')
            return redirect('accounts:contra_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating contra entry: {str(e)}')

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'credit_entry': credit_entry,
        'accounts': accounts,
    }
    return render(request, 'accounts/transaction/contra/edit.html', context)

@login_required
def contra_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction, pk=pk, transaction_type='contra')
    
    print(f"\n=== Deleting Contra Entry ===")
    print(f"Found debit entry ID: {transaction.id}")
    print(f"From Account: {transaction.account.id} - {transaction.account.name}")
    print(f"To Account: {transaction.to_account.id} - {transaction.to_account.name}")
    print(f"Amount: {transaction.amount}")
    print(f"Date: {transaction.date}")
    print(f"Reference: {transaction.reference_number}")
    
    # First try to find by reference number and amount
    credit_entry = Transaction.objects.filter(
        transaction_type='contra_credit',
        reference_number=transaction.reference_number,
        amount=transaction.amount
    ).first()
    
    if credit_entry:
        print(f"\nFound credit entry by reference and amount:")
        print(f"ID: {credit_entry.id}")
        print(f"From: {credit_entry.from_account.id} - {credit_entry.from_account.name}")
        print(f"To: {credit_entry.account.id} - {credit_entry.account.name}")
    else:
        print("\nTrying to find by accounts and amount...")
        # Try to find by accounts and amount
        credit_entry = Transaction.objects.filter(
            transaction_type='contra_credit',
            from_account=transaction.account,
            account=transaction.to_account,  # Note: credit entry's account is debit entry's to_account
            amount=transaction.amount
        ).first()
        
        if credit_entry:
            print(f"Found credit entry by accounts and amount:")
            print(f"ID: {credit_entry.id}")
            print(f"From: {credit_entry.from_account.id} - {credit_entry.from_account.name}")
            print(f"To: {credit_entry.account.id} - {credit_entry.account.name}")
        else:
            print("No matching credit entry found")
            # Show all contra_credit entries for debugging
            all_credits = Transaction.objects.filter(transaction_type='contra_credit')
            print(f"\nAll contra_credit entries in system:")
            for entry in all_credits:
                print(f"ID: {entry.id}, From: {entry.from_account.id}, To: {entry.account.id}, Amount: {entry.amount}, Ref: {entry.reference_number}")

    if request.method == 'POST':
        try:
            # Start by deleting credit entry if it exists
            if credit_entry:
                print(f"\nDeleting credit entry: {credit_entry.id}")
                Transaction.objects.filter(id=credit_entry.id).delete()
            else:
                print("\nWarning: No credit entry found to delete")
            
            # Then delete the debit entry
            print(f"Deleting debit entry: {transaction.id}")
            Transaction.objects.filter(id=transaction.id).delete()
            print("=== Deletion Complete ===\n")
            
            messages.success(request, 'Contra entry deleted successfully.')
            return redirect('accounts:contra_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting contra entry: {str(e)}')
            print(f"Error in deletion: {str(e)}")
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'credit_entry': credit_entry,
    }
    return render(request, 'accounts/transaction/contra/delete.html', context)

@login_required
def intra_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get only intra debit transactions for this pastorate and its churches
    transactions = Transaction.objects.filter(
        Q(account__pastorate=pastorate) | Q(account__church__pastorate=pastorate),
        transaction_type='intra'  # Only get debit entries
    ).select_related(
        'account',
        'to_account',
        'primary_category',
        'secondary_category',
        'created_by'
    ).order_by('-date')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = transactions.filter(
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Date filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])

    # Account filter
    account_id = request.GET.get('account')
    if account_id:
        transactions = transactions.filter(
            Q(account_id=account_id) | Q(to_account_id=account_id)
        )

    # Pagination
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page = request.GET.get('page')
    transactions = paginator.get_page(page)

    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    context = {
        'pastorate': pastorate,
        'transactions': transactions,
        'accounts': accounts,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'selected_account': account_id
    }
    return render(request, 'accounts/transaction/intra/list.html', context)

@login_required
def intra_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    # Get all categories regardless of type
    primary_categories = PrimaryCategory.objects.filter(
        is_active=True
    ).order_by('name')
    
    # Print for debugging
    print(f"Found {primary_categories.count()} primary categories")
    for cat in primary_categories:
        print(f"Category: {cat.name} (Type: {cat.transaction_type})")

    # Get all secondary categories
    secondary_categories = SecondaryCategory.objects.filter(
        is_active=True
    ).select_related('primary_category').order_by('name')
    
    # Print for debugging
    print(f"Found {secondary_categories.count()} secondary categories")

    if request.method == 'POST':
        try:
            # Get form data
            from_account = get_object_or_404(Account, pk=request.POST.get('from_account'))
            to_account = get_object_or_404(Account, pk=request.POST.get('to_account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Create the intra transaction (debit entry)
            debit_transaction = Transaction.objects.create(
                account=from_account,
                to_account=to_account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=f"Intra Transfer (Debit) - {description}",
                transaction_type='intra',
                primary_category=primary_category,
                secondary_category=secondary_category,
                created_by=request.user
            )

            # Create the corresponding credit entry
            credit_transaction = Transaction.objects.create(
                account=to_account,
                from_account=from_account,
                amount=amount,
                date=date,
                reference_number=reference_number,
                description=f"Intra Transfer (Credit) - {description}",
                transaction_type='intra_credit',
                primary_category=primary_category,
                secondary_category=secondary_category,
                created_by=request.user
            )

            messages.success(request, 'Intra transfer created successfully.')
            return redirect('accounts:intra_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error creating intra transfer: {str(e)}')

    context = {
        'pastorate': pastorate,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
        'today': timezone.now()
    }
    
    # Add debug info to context
    context['debug_primary_count'] = primary_categories.count()
    context['debug_secondary_count'] = secondary_categories.count()
    
    return render(request, 'accounts/transaction/intra/add.html', context)

@login_required
def intra_detail(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    
    # Try to get either the debit or credit entry
    try:
        transaction = Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account',
            'primary_category',
            'secondary_category',
            'created_by'
        ).get(
            pk=pk,
            transaction_type__in=['intra', 'intra_credit']
        )
    except Transaction.DoesNotExist:
        raise Http404("Transaction not found")
    
    # If this is a credit entry, get the corresponding debit entry
    if transaction.transaction_type == 'intra_credit':
        credit_entry = transaction
        debit_entry = Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account',
            'primary_category',
            'secondary_category'
        ).filter(
            transaction_type='intra',
            account=transaction.from_account,
            to_account=transaction.account,
            date=transaction.date,
            amount=transaction.amount
        ).first()
        if debit_entry:
            transaction = debit_entry
        else:
            raise Http404("Corresponding debit entry not found")
    # If this is a debit entry, get the corresponding credit entry
    else:
        credit_entry = Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account',
            'primary_category',
            'secondary_category'
        ).filter(
            transaction_type='intra_credit',
            from_account=transaction.account,
            to_account=transaction.to_account,
            date=transaction.date,
            amount=transaction.amount
        ).first()

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'credit_entry': credit_entry,
    }
    return render(request, 'accounts/transaction/intra/detail.html', context)

@login_required
def intra_edit(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'account',
            'to_account',
            'from_account',
            'primary_category',
            'secondary_category'
        ),
        pk=pk,
        transaction_type='intra'
    )
    
    # Get the corresponding credit entry
    credit_entry = Transaction.objects.select_related(
        'account',
        'to_account',
        'from_account',
        'primary_category',
        'secondary_category'
    ).filter(
        transaction_type='intra_credit',
        from_account=transaction.account,
        to_account=transaction.to_account,
        date=transaction.date,
        amount=transaction.amount
    ).first()
    
    # Get all accounts from pastorate and its churches
    accounts = Account.objects.filter(
        Q(pastorate=pastorate) | Q(church__pastorate=pastorate)
    ).select_related('church').order_by('name')

    # Get contra categories
    primary_categories = PrimaryCategory.objects.filter(
        transaction_type='contra',
        is_active=True
    ).order_by('name')

    # Get all secondary categories for contra primary categories
    secondary_categories = SecondaryCategory.objects.filter(
        primary_category__transaction_type='contra',
        is_active=True
    ).select_related('primary_category').order_by('name')

    if request.method == 'POST':
        try:
            # Get form data
            from_account = get_object_or_404(Account, pk=request.POST.get('from_account'))
            to_account = get_object_or_404(Account, pk=request.POST.get('to_account'))
            amount = Decimal(request.POST.get('amount'))
            date = request.POST.get('date')
            reference_number = request.POST.get('reference_number')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            secondary_category = get_object_or_404(SecondaryCategory, pk=request.POST.get('secondary_category'))

            # Update the debit transaction
            transaction.account = from_account
            transaction.to_account = to_account
            transaction.amount = amount
            transaction.date = date
            transaction.reference_number = reference_number
            transaction.description = f"Intra Transfer (Debit) - {description}"
            transaction.primary_category = primary_category
            transaction.secondary_category = secondary_category
            transaction.save()

            # Update the credit transaction
            if credit_entry:
                credit_entry.account = to_account
                credit_entry.from_account = from_account
                credit_entry.amount = amount
                credit_entry.date = date
                credit_entry.reference_number = reference_number
                credit_entry.description = f"Intra Transfer (Credit) - {description}"
                credit_entry.primary_category = primary_category
                credit_entry.secondary_category = secondary_category
                credit_entry.save()

            messages.success(request, 'Intra transfer updated successfully.')
            return redirect('accounts:intra_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error updating intra transfer: {str(e)}')

    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'credit_entry': credit_entry,
        'accounts': accounts,
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/transaction/intra/edit.html', context)

@login_required
def intra_delete(request, pastorate_id, pk):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    transaction = get_object_or_404(Transaction, pk=pk, transaction_type='intra')
    
    print(f"\n=== Deleting Intra Entry ===")
    print(f"Found debit entry ID: {transaction.id}")
    print(f"From Account: {transaction.account.id} - {transaction.account.name}")
    print(f"To Account: {transaction.to_account.id} - {transaction.to_account.name}")
    print(f"Amount: {transaction.amount}")
    print(f"Date: {transaction.date}")
    print(f"Reference: {transaction.reference_number}")
    
    # First try to find by reference number and amount
    credit_entry = Transaction.objects.filter(
        transaction_type='intra_credit',
        reference_number=transaction.reference_number,
        amount=transaction.amount
    ).first()
    
    if credit_entry:
        print(f"\nFound credit entry by reference and amount:")
        print(f"ID: {credit_entry.id}")
        print(f"From: {credit_entry.from_account.id} - {credit_entry.from_account.name}")
        print(f"To: {credit_entry.account.id} - {credit_entry.account.name}")
    else:
        print("\nTrying to find by accounts and amount...")
        # Try to find by accounts and amount
        credit_entry = Transaction.objects.filter(
            transaction_type='intra_credit',
            from_account=transaction.account,
            account=transaction.to_account,  # Note: credit entry's account is debit entry's to_account
            amount=transaction.amount
        ).first()
        
        if credit_entry:
            print(f"Found credit entry by accounts and amount:")
            print(f"ID: {credit_entry.id}")
            print(f"From: {credit_entry.from_account.id} - {credit_entry.from_account.name}")
            print(f"To: {credit_entry.account.id} - {credit_entry.account.name}")
        else:
            print("No matching credit entry found")
            # Show all intra_credit entries for debugging
            all_credits = Transaction.objects.filter(transaction_type='intra_credit')
            print(f"\nAll intra_credit entries in system:")
            for entry in all_credits:
                print(f"ID: {entry.id}, From: {entry.from_account.id}, To: {entry.account.id}, Amount: {entry.amount}, Ref: {entry.reference_number}")

    if request.method == 'POST':
        try:
            # Start by deleting credit entry if it exists
            if credit_entry:
                print(f"\nDeleting credit entry: {credit_entry.id}")
                Transaction.objects.filter(id=credit_entry.id).delete()
            else:
                print("\nWarning: No credit entry found to delete")
            
            # Then delete the debit entry
            print(f"Deleting debit entry: {transaction.id}")
            Transaction.objects.filter(id=transaction.id).delete()
            print("=== Deletion Complete ===\n")
            
            messages.success(request, 'Intra transfer deleted successfully.')
            return redirect('accounts:intra_list', pastorate_id=pastorate_id)
        except Exception as e:
            messages.error(request, f'Error deleting intra transfer: {str(e)}')
            print(f"Error in deletion: {str(e)}")
    
    context = {
        'pastorate': pastorate,
        'transaction': transaction,
        'credit_entry': credit_entry,
    }
    return render(request, 'accounts/transaction/intra/delete.html', context)