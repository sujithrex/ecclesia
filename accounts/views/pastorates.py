from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from congregation.models import Pastorate, Church
from ..models import Account, AccountType

@login_required
def pastorate_list(request):
    pastorates = Pastorate.objects.prefetch_related(
        'accounts',
        'church_set'
    ).order_by('pastorate_name')
    
    context = {
        'pastorates': pastorates,
    }
    return render(request, 'accounts/pastorate/pastorate_list.html', context)

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
    return render(request, 'accounts/pastorate/pastorate_detail.html', context)

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
    return render(request, 'accounts/pastorate/pastorate_account_add.html', context) 