from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from congregation.models import Pastorate, Church, Family, Member
from datetime import date
from django.db.models import Count, F

User = get_user_model()

@login_required
def dashboard(request):
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

def login_view(request):
    return render(request, 'web/login.html')
