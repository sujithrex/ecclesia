from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from congregation.models import Church
from ..models import Account, AccountType

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
    return render(request, 'accounts/church/church_detail.html', context)

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
    return render(request, 'accounts/church/church_account_add.html', context) 