from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import AccountType

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