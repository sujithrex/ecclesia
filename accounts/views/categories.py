from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from ..models import PrimaryCategory, SecondaryCategory

@login_required
def category_list(request):
    """List all primary and secondary categories"""
    primary_categories = PrimaryCategory.objects.filter(is_active=True).order_by('name')
    secondary_categories = SecondaryCategory.objects.filter(is_active=True).order_by('primary_category', 'name')
    
    context = {
        'primary_categories': primary_categories,
        'secondary_categories': secondary_categories,
    }
    return render(request, 'accounts/category/list.html', context)

@login_required
def primary_category_add(request):
    """Add a new primary category"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            transaction_type = request.POST.get('transaction_type')
            
            category = PrimaryCategory.objects.create(
                name=name,
                description=description,
                transaction_type=transaction_type
            )
            
            messages.success(request, f'Primary category "{name}" created successfully.')
            return redirect('accounts:category_list')
        except Exception as e:
            messages.error(request, f'Error creating primary category: {str(e)}')
    
    return render(request, 'accounts/category/primary_add.html')

@login_required
def primary_category_edit(request, pk):
    """Edit an existing primary category"""
    category = get_object_or_404(PrimaryCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.transaction_type = request.POST.get('transaction_type')
            category.save()
            
            messages.success(request, f'Primary category "{category.name}" updated successfully.')
            return redirect('accounts:category_list')
        except Exception as e:
            messages.error(request, f'Error updating primary category: {str(e)}')
    
    context = {
        'category': category,
    }
    return render(request, 'accounts/category/primary_edit.html', context)

@login_required
def primary_category_delete(request, pk):
    """Delete a primary category"""
    category = get_object_or_404(PrimaryCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            name = category.name
            category.is_active = False
            category.save()
            
            messages.success(request, f'Primary category "{name}" deleted successfully.')
            return redirect('accounts:category_list')
        except Exception as e:
            messages.error(request, f'Error deleting primary category: {str(e)}')
    
    context = {
        'category': category,
    }
    return render(request, 'accounts/category/primary_delete.html', context)

@login_required
def secondary_category_add(request):
    """Add a new secondary category"""
    primary_categories = PrimaryCategory.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            
            category = SecondaryCategory.objects.create(
                name=name,
                description=description,
                primary_category=primary_category
            )
            
            messages.success(request, f'Secondary category "{name}" created successfully.')
            return redirect('accounts:category_list')
        except Exception as e:
            messages.error(request, f'Error creating secondary category: {str(e)}')
    
    context = {
        'primary_categories': primary_categories,
    }
    return render(request, 'accounts/category/secondary_add.html', context)

@login_required
def secondary_category_edit(request, pk):
    """Edit an existing secondary category"""
    category = get_object_or_404(SecondaryCategory, pk=pk)
    primary_categories = PrimaryCategory.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.primary_category = get_object_or_404(PrimaryCategory, pk=request.POST.get('primary_category'))
            category.save()
            
            messages.success(request, f'Secondary category "{category.name}" updated successfully.')
            return redirect('accounts:category_list')
        except Exception as e:
            messages.error(request, f'Error updating secondary category: {str(e)}')
    
    context = {
        'category': category,
        'primary_categories': primary_categories,
    }
    return render(request, 'accounts/category/secondary_edit.html', context)

@login_required
def secondary_category_delete(request, pk):
    """Delete a secondary category"""
    category = get_object_or_404(SecondaryCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            name = category.name
            category.is_active = False
            category.save()
            
            messages.success(request, f'Secondary category "{name}" deleted successfully.')
            return redirect('accounts:category_list')
        except Exception as e:
            messages.error(request, f'Error deleting secondary category: {str(e)}')
    
    context = {
        'category': category,
    }
    return render(request, 'accounts/category/secondary_delete.html', context) 