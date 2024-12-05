from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from congregation.models import Pastorate, Church, Family, Member, Respect, Relation
from accounts.models import (
    AccountType, TransactionCategory, TransactionHistory, 
    DioceseCategory, DioceseContraCategory
)
from datetime import date
from django.db.models import Count, F

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('web:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url and not next_url.startswith('/?next='):
                return redirect(next_url)
            return redirect('web:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'web/login.html')

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('web:login')
        
    # Get today's date
    today = date.today()
    
    # Get all members
    members = Member.objects.filter(death=False).select_related(
        'family', 'respect', 'spouse', 'spouse__respect', 
        'family__area', 'family__area__church'
    )
    
    # Get birthdays
    birthdays = members.filter(
        dob__month=today.month,
        dob__day=today.day
    )
    
    # Get anniversaries (only get one spouse to avoid duplicates)
    anniversaries = members.filter(
        dom__month=today.month,
        dom__day=today.day,
        spouse__isnull=False,  # Must have a spouse
        member_id__lt=F('spouse__member_id')  # Only get one spouse (the one with lower member_id)
    )
    
    # Get counts
    pastorate_count = Pastorate.objects.count()
    church_count = Church.objects.count()
    family_count = Family.objects.count()
    member_count = Member.objects.filter(death=False).count()
    
    context = {
        'birthdays': birthdays,
        'anniversaries': anniversaries,
        'pastorate_count': pastorate_count,
        'church_count': church_count,
        'family_count': family_count,
        'member_count': member_count,
    }
    return render(request, 'web/dashboard.html', context)

@login_required
def profile(request):
    return render(request, 'web/profile.html')

@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('web:profile')
    return redirect('web:profile')

@login_required
def essentials(request):
    """
    Unified essentials view that combines both congregation and financial settings
    """
    default_categories = {
        'Acquittance',
        'Bills and Vouchers',
        'Church Offertory',
        'Receipts'
    }
    
    categories = TransactionCategory.objects.all().order_by('name')
    for category in categories:
        category.is_default = category.name in default_categories
    
    # Handle transaction history search
    search_query = request.GET.get('search', '').strip()
    transaction_history = TransactionHistory.objects.select_related(
        'transaction',
        'transaction__account',
        'transaction__account__account_type'
    )
    
    if search_query:
        transaction_history = transaction_history.filter(
            transaction__description__icontains=search_query
        ) | transaction_history.filter(
            transaction__account__name__icontains=search_query
        ) | transaction_history.filter(
            transaction__reference_number__icontains=search_query
        )
    
    transaction_history = transaction_history.order_by('-modified_at')[:50]
    
    context = {
        'respects': Respect.objects.all().order_by('name'),
        'relations': Relation.objects.all().order_by('name'),
        'account_types': AccountType.objects.all().order_by('name'),
        'categories': categories,
        'diocese_categories': DioceseCategory.objects.all().order_by('name'),
        'contra_categories': DioceseContraCategory.objects.all().order_by('name'),
        'transaction_history': transaction_history,
        'search_query': search_query,
    }
    return render(request, 'web/essentials.html', context)
