from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import models, transaction
from .models import Pastorate, Church, Area, Fellowship, Family, Respect, Relation, Member
from django.db.models import Count, F, Q
from datetime import date, datetime
from django.core.paginator import Paginator
from accounts.models import AccountType, PrimaryCategory, Account
import csv
import io
from django.urls import reverse
from django.core.files.uploadedfile import UploadedFile

@login_required
def pastorate_list(request):
    pastorates = Pastorate.objects.annotate(
        church_count=Count('church')
    ).order_by('pastorate_name')
    return render(request, 'congregation/pastorate/list.html', {
        'pastorates': pastorates
    })

@login_required
def pastorate_add(request):
    if request.method == 'POST':
        pastorate = Pastorate(
            pastorate_name=request.POST['pastorate_name'],
            pastorate_short_name=request.POST['pastorate_short_name'],
            user=request.user
        )
        pastorate.save()
        messages.success(request, 'Pastorate added successfully.')
        return redirect('congregation:pastorate_list')
    return render(request, 'congregation/pastorate/add.html')

@login_required
def pastorate_detail(request, pk):
    pastorate = get_object_or_404(Pastorate, pk=pk)
    churches = Church.objects.filter(pastorate=pastorate)
    return render(request, 'congregation/pastorate/detail.html', {
        'pastorate': pastorate,
        'churches': churches
    })

@login_required
def pastorate_edit(request, pk):
    pastorate = get_object_or_404(Pastorate, pk=pk)
    if request.method == 'POST':
        pastorate.pastorate_name = request.POST['pastorate_name']
        pastorate.pastorate_short_name = request.POST['pastorate_short_name']
        pastorate.save()
        messages.success(request, 'Pastorate updated successfully.')
        return redirect('congregation:pastorate_detail', pk=pk)
    return render(request, 'congregation/pastorate/edit.html', {
        'pastorate': pastorate
    })

@login_required
def pastorate_delete(request, pk):
    pastorate = get_object_or_404(Pastorate, pk=pk)
    
    if request.method == 'POST':
        try:
            # Check if this is a force delete
            if request.POST.get('force_delete') == 'true':
                # Get all related records for deletion
                related_churches = Church.objects.filter(pastorate=pastorate)
                related_accounts = Account.objects.filter(pastorate=pastorate)
                
                # Use transaction to ensure all deletions succeed or none do
                with transaction.atomic():
                    # First delete all transactions
                    from accounts.models import Transaction
                    for church in related_churches:
                        Transaction.objects.filter(church=church).delete()
                        Transaction.objects.filter(account__church=church).delete()
                    
                    # Delete all transactions related to pastorate accounts
                    for account in related_accounts:
                        Transaction.objects.filter(account=account).delete()
                        Transaction.objects.filter(to_account=account).delete()
                    
                    # Now delete the accounts
                    for account in related_accounts:
                        account.delete()
                    
                    # Finally delete churches (this will cascade delete areas, fellowships, families, and members)
                    for church in related_churches:
                        church.delete()
                    
                    # Delete the pastorate
                    pastorate.delete()
                
                messages.success(request, f'Pastorate "{pastorate.pastorate_name}" and all its related records have been deleted.')
                return redirect('congregation:pastorate_list')
            else:
                # Regular delete - check for related records
                related_churches = Church.objects.filter(pastorate=pastorate)
                related_accounts = Account.objects.filter(pastorate=pastorate)
                
                if related_churches.exists() or related_accounts.exists():
                    error_message = "Cannot delete this pastorate because it has:"
                    if related_churches.exists():
                        error_message += f"\n- {related_churches.count()} connected churches"
                    if related_accounts.exists():
                        error_message += f"\n- {related_accounts.count()} connected accounts"
                    error_message += "\n\nPlease delete or reassign these records before deleting the pastorate."
                    messages.error(request, error_message)
                else:
                    pastorate.delete()
                    messages.success(request, 'Pastorate deleted successfully.')
                    return redirect('congregation:pastorate_list')
        except Exception as e:
            messages.error(request, f'An error occurred while deleting: {str(e)}')
        return redirect('congregation:pastorate_detail', pk=pk)
    
    # Get counts of related records for the confirmation page
    context = {
        'pastorate': pastorate,
        'related_churches': Church.objects.filter(pastorate=pastorate),
        'related_accounts': Account.objects.filter(pastorate=pastorate),
    }
    return render(request, 'congregation/pastorate/delete.html', context)

@login_required
def church_list(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    churches = Church.objects.filter(pastorate=pastorate).annotate(
        fellowship_count=Count('area__fellowship', distinct=True)
    )
    return render(request, 'congregation/church/list.html', {
        'pastorate': pastorate,
        'churches': churches
    })

@login_required
def church_add(request, pastorate_id):
    pastorate = get_object_or_404(Pastorate, pk=pastorate_id)
    if request.method == 'POST':
        church = Church(
            pastorate=pastorate,
            church_name=request.POST['church_name'],
            abode=request.POST['abode'],
            short_name=request.POST['short_name']
        )
        church.save()
        messages.success(request, 'Church added successfully.')
        return redirect('congregation:church_list', pastorate_id=pastorate_id)
    return render(request, 'congregation/church/add.html', {
        'pastorate': pastorate
    })

@login_required
def church_detail(request, pk):
    church = get_object_or_404(Church, pk=pk)
    areas = Area.objects.filter(church=church)
    fellowships = Fellowship.objects.filter(area__church=church).distinct()
    families = Family.objects.filter(area__church=church)
    
    # Pagination
    area_paginator = Paginator(areas, 10)  # 10 areas per page
    fellowship_paginator = Paginator(fellowships, 10)  # 10 fellowships per page
    family_paginator = Paginator(families, 10)  # 10 families per page
    
    area_page = request.GET.get('area_page')
    fellowship_page = request.GET.get('fellowship_page')
    family_page = request.GET.get('family_page')
    
    areas = area_paginator.get_page(area_page)
    fellowships = fellowship_paginator.get_page(fellowship_page)
    families = family_paginator.get_page(family_page)
    
    # Get today's date
    today = date.today()
    
    # Get all members from this church's areas
    members = Member.objects.filter(
        family__area__church=church,
        death=False  # Exclude deceased members
    ).select_related('family', 'respect', 'spouse', 'spouse__respect', 'family__area')
    
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
    
    context = {
        'church': church,
        'areas': areas,
        'fellowships': fellowships,
        'families': families,
        'members': members,
        'birthdays': birthdays,
        'anniversaries': anniversaries,
    }
    return render(request, 'congregation/church/detail.html', context)

@login_required
def church_edit(request, pk):
    church = get_object_or_404(Church, pk=pk)
    if request.method == 'POST':
        church.church_name = request.POST['church_name']
        church.abode = request.POST['abode']
        church.short_name = request.POST['short_name']
        church.save()
        messages.success(request, 'Church updated successfully.')
        return redirect('congregation:church_detail', pk=pk)
    return render(request, 'congregation/church/edit.html', {
        'church': church
    })

@login_required
def church_delete(request, pk):
    church = get_object_or_404(Church, pk=pk)
    pastorate_id = church.pastorate.id
    if request.method == 'POST':
        church.delete()
        messages.success(request, 'Church deleted successfully.')
        return redirect('congregation:church_list', pastorate_id=pastorate_id)
    return render(request, 'congregation/church/delete.html', {
        'church': church
    })

# Area Views
@login_required
def area_list(request, church_id):
    church = get_object_or_404(Church, pk=church_id)
    areas = Area.objects.filter(church=church)
    context = {
        'church': church,
        'areas': areas,
    }
    return render(request, 'congregation/area/list.html', context)

@login_required
def area_add(request, church_id):
    church = get_object_or_404(Church, pk=church_id)
    
    if request.method == 'POST':
        area_name = request.POST.get('area_name')
        area_id = f"{church.short_name}-{request.POST.get('area_id')}"
        
        area = Area.objects.create(
            church=church,
            area_name=area_name,
            area_id=area_id
        )
        return redirect('congregation:area_detail', pk=area.pk)
    
    context = {
        'church': church,
    }
    return render(request, 'congregation/area/add.html', context)

@login_required
def area_detail(request, pk):
    area = get_object_or_404(Area, pk=pk)
    
    # Get all data
    fellowships = Fellowship.objects.filter(area=area)
    families = Family.objects.filter(area=area)
    members = Member.objects.filter(family__area=area, death=False).select_related(
        'family', 'respect', 'spouse', 'spouse__respect'
    )
    
    # Pagination
    fellowship_paginator = Paginator(fellowships, 10)  # Show 10 fellowships per page
    family_paginator = Paginator(families, 10)  # Show 10 families per page
    
    fellowship_page = request.GET.get('fellowship_page', 1)
    family_page = request.GET.get('family_page', 1)
    
    fellowships = fellowship_paginator.get_page(fellowship_page)
    families = family_paginator.get_page(family_page)
    
    # Get today's date
    today = date.today()
    
    # Get birthdays
    birthdays = members.filter(
        dob__month=today.month,
        dob__day=today.day
    )
    
    # Get anniversaries
    anniversaries = members.filter(
        dom__month=today.month,
        dom__day=today.day,
        spouse__isnull=False,
        member_id__lt=F('spouse__member_id')
    )
    
    context = {
        'area': area,
        'fellowships': fellowships,
        'families': families,
        'total_members': members.count(),
        'birthdays': birthdays,
        'anniversaries': anniversaries,
    }
    return render(request, 'congregation/area/detail.html', context)

@login_required
def area_edit(request, pk):
    area = get_object_or_404(Area, pk=pk)
    
    if request.method == 'POST':
        area.area_name = request.POST.get('area_name')
        area.area_id = f"{area.church.short_name}-{request.POST.get('area_id')}"
        area.save()
        return redirect('congregation:area_detail', pk=area.pk)
    
    context = {
        'area': area,
    }
    return render(request, 'congregation/area/edit.html', context)

@login_required
def area_delete(request, pk):
    area = get_object_or_404(Area, pk=pk)
    church = area.church
    
    if request.method == 'POST':
        area.delete()
        return redirect('congregation:area_list', church_id=church.pk)
    
    context = {
        'area': area,
    }
    return render(request, 'congregation/area/delete.html', context)

@login_required
def area_position_edit(request, pk):
    area = get_object_or_404(Area.objects.select_related('church__pastorate'), pk=pk)
    
    if request.method == 'POST':
        try:
            # Handle position updates from AJAX request
            positions = request.POST.getlist('positions[]')
            
            # Update all positions in a transaction
            with transaction.atomic():
                # First, validate all family IDs belong to this area
                family_count = Family.objects.filter(
                    id__in=positions,
                    area=area
                ).count()
                
                if family_count != len(positions):
                    raise ValueError("Invalid family IDs detected")
                
                # Update positions
                for index, family_id in enumerate(positions, 1):
                    Family.objects.filter(
                        id=family_id,
                        area=area
                    ).update(position_no=index)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    # Get families ordered by position_no, then by family_id for those without position
    families = Family.objects.filter(area=area).order_by(
        F('position_no').asc(nulls_last=True),
        'family_id'
    ).select_related('respect')
    
    context = {
        'area': area,
        'families': families,
    }
    return render(request, 'congregation/area/position_edit.html', context)

# Fellowship Views
@login_required
def fellowship_list(request, church_id):
    church = get_object_or_404(Church, pk=church_id)
    fellowships = Fellowship.objects.filter(area__church=church)
    context = {
        'church': church,
        'fellowships': fellowships,
    }
    return render(request, 'congregation/fellowship/list.html', context)

@login_required
def fellowship_add(request, church_id):
    church = get_object_or_404(Church, pk=church_id)
    areas = Area.objects.filter(church=church)
    
    if request.method == 'POST':
        area = get_object_or_404(Area, pk=request.POST.get('area'))
        fellowship_name = request.POST.get('fellowship_name')
        fellowship_id = f"{area.area_id}-{request.POST.get('fellowship_id')}"
        address = request.POST.get('address', '')
        
        fellowship = Fellowship.objects.create(
            area=area,
            fellowship_name=fellowship_name,
            fellowship_id=fellowship_id,
            address=address
        )
        return redirect('congregation:fellowship_detail', pk=fellowship.pk)
    
    context = {
        'church': church,
        'areas': areas,
    }
    return render(request, 'congregation/fellowship/add.html', context)

@login_required
def fellowship_detail(request, pk):
    fellowship = get_object_or_404(Fellowship, pk=pk)
    families = Family.objects.filter(fellowship=fellowship)
    members = Member.objects.filter(family__fellowship=fellowship, death=False)
    
    # Pagination
    family_paginator = Paginator(families, 10)
    member_paginator = Paginator(members, 10)
    
    family_page = request.GET.get('family_page')
    member_page = request.GET.get('member_page')
    
    families = family_paginator.get_page(family_page)
    paginated_members = member_paginator.get_page(member_page)
    
    # Get today's date
    today = date.today()
    
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
    
    context = {
        'fellowship': fellowship,
        'families': families,
        'members': paginated_members,
        'total_members': members.count(),
        'birthdays': birthdays,
        'anniversaries': anniversaries,
    }
    return render(request, 'congregation/fellowship/detail.html', context)

@login_required
def fellowship_edit(request, pk):
    fellowship = get_object_or_404(Fellowship, pk=pk)
    
    if request.method == 'POST':
        fellowship.fellowship_name = request.POST.get('fellowship_name')
        fellowship.fellowship_id = f"{fellowship.area.area_id}-{request.POST.get('fellowship_id')}"
        fellowship.address = request.POST.get('address', '')
        fellowship.save()
        return redirect('congregation:fellowship_detail', pk=fellowship.pk)
    
    context = {
        'fellowship': fellowship,
    }
    return render(request, 'congregation/fellowship/edit.html', context)

@login_required
def fellowship_delete(request, pk):
    fellowship = get_object_or_404(Fellowship, pk=pk)
    church = fellowship.area.church
    
    if request.method == 'POST':
        fellowship.delete()
        return redirect('congregation:fellowship_list', church_id=church.pk)
    
    context = {
        'fellowship': fellowship,
    }
    return render(request, 'congregation/fellowship/delete.html', context)

# Family Views
@login_required
def family_list(request, area_id):
    area = get_object_or_404(Area, pk=area_id)
    families = Family.objects.filter(area=area)
    context = {
        'area': area,
        'families': families,
    }
    return render(request, 'congregation/family/list.html', context)

@login_required
def family_add(request, area_id):
    area = get_object_or_404(Area, pk=area_id)
    fellowships = Fellowship.objects.filter(area=area)
    respects = Respect.objects.all()
    
    # Get the next available number for the family ID
    next_number = Family.get_next_number(area)
    suggested_family_id = f"{next_number:03d}"  # Just the number part
    
    if request.method == 'POST':
        fellowship = get_object_or_404(Fellowship, pk=request.POST.get('fellowship'))
        respect = get_object_or_404(Respect, pk=request.POST.get('respect'))
        
        # Get Family Head relation
        try:
            relation = Relation.objects.filter(name='Family Head').first()
            if not relation:
                messages.error(request, 'Family Head relation not found. Please run migrations.')
                return redirect('congregation:family_list', area_id=area.pk)
        except Exception as e:
            messages.error(request, f'Error getting Family Head relation: {str(e)}')
            return redirect('congregation:family_list', area_id=area.pk)
        
        # Get the submitted family number and create the full family ID
        family_number = request.POST.get('family_id', '').zfill(3)
        family_id = f"{area.area_id}-{family_number}"
        
        try:
            # Create the family record
            family = Family.objects.create(
                area=area,
                fellowship=fellowship,
                respect=respect,
                initial=request.POST.get('initial', ''),
                family_head=request.POST.get('family_head'),
                family_id=family_id,
                mobile=request.POST.get('mobile'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                prayer_points=request.POST.get('prayer_points', '')
            )

            # Create member record for family head with consistent ID format
            member_id = f"{family_id}-01"  # Always use 01 for family head

            Member.objects.create(
                family=family,
                member_id=member_id,
                respect=respect,
                initial=request.POST.get('initial', ''),
                name=request.POST.get('family_head'),
                relation=relation,
                sex=request.POST.get('head_sex'),
                dob=request.POST.get('head_dob') or None,
                working='',
                working_place=''
            )
            
            messages.success(request, 'Family and family head member added successfully.')
            return redirect('congregation:family_detail', pk=family.pk)
        except Exception as e:
            messages.error(request, f'Error creating family: {str(e)}')
    
    context = {
        'area': area,
        'fellowships': fellowships,
        'respects': respects,
        'suggested_family_id': suggested_family_id,
    }
    return render(request, 'congregation/family/add.html', context)

@login_required
def family_detail(request, pk):
    family = get_object_or_404(Family, pk=pk)
    members = Member.objects.filter(family=family)
    
    # Calculate stats
    baptised_count = members.filter(baptised=True).count()
    confirmed_count = members.filter(conformed=True).count()
    active_count = members.filter(death=False).count()
    
    context = {
        'family': family,
        'members': members,
        'baptised_count': baptised_count,
        'confirmed_count': confirmed_count,
        'active_count': active_count,
    }
    return render(request, 'congregation/family/detail.html', context)

@login_required
def family_edit(request, pk):
    family = get_object_or_404(Family, pk=pk)
    fellowships = Fellowship.objects.filter(area=family.area)
    respects = Respect.objects.all()
    
    if request.method == 'POST':
        fellowship = get_object_or_404(Fellowship, pk=request.POST.get('fellowship'))
        respect = get_object_or_404(Respect, pk=request.POST.get('respect'))
        
        family.fellowship = fellowship
        family.respect = respect
        family.initial = request.POST.get('initial', '')
        family.family_head = request.POST.get('family_head')
        family.family_id = f"{fellowship.fellowship_id}-{request.POST.get('family_id')}"
        family.mobile = request.POST.get('mobile')
        family.email = request.POST.get('email', '')
        family.save()
        
        messages.success(request, 'Family updated successfully.')
        return redirect('congregation:family_detail', pk=family.pk)
    
    context = {
        'family': family,
        'fellowships': fellowships,
        'respects': respects,
    }
    return render(request, 'congregation/family/edit.html', context)

@login_required
def family_delete(request, pk):
    family = get_object_or_404(Family, pk=pk)
    area = family.area
    
    if request.method == 'POST':
        family.delete()
        messages.success(request, 'Family deleted successfully.')
        return redirect('congregation:family_list', area_id=area.pk)
    
    context = {
        'family': family,
    }
    return render(request, 'congregation/family/delete.html', context)

# Settings Views - Respect
@login_required
def respect_list(request):
    respects = Respect.objects.all()
    context = {
        'respects': respects,
    }
    return render(request, 'congregation/settings/respect/list.html', context)

@login_required
def respect_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        respect = Respect.objects.create(name=name)
        messages.success(request, 'Respect title added successfully.')
        return redirect('congregation:respect_list')
    return render(request, 'congregation/settings/respect/add.html')

@login_required
def respect_edit(request, pk):
    respect = get_object_or_404(Respect, pk=pk)
    if request.method == 'POST':
        respect.name = request.POST.get('name')
        respect.save()
        messages.success(request, 'Respect title updated successfully.')
        return redirect('congregation:respect_list')
    context = {
        'respect': respect,
    }
    return render(request, 'congregation/settings/respect/edit.html', context)

@login_required
def respect_delete(request, pk):
    respect = get_object_or_404(Respect, pk=pk)
    if request.method == 'POST':
        try:
            respect.delete()
            messages.success(request, 'Respect title deleted successfully.')
        except models.ProtectedError:
            messages.error(request, 'Cannot delete this respect title as it is being used by families/members.')
        return redirect('congregation:respect_list')
    context = {
        'respect': respect,
    }
    return render(request, 'congregation/settings/respect/delete.html', context)

# Settings Views - Relation
@login_required
def relation_list(request):
    relations = Relation.objects.all()
    context = {
        'relations': relations,
    }
    return render(request, 'congregation/settings/relation/list.html', context)

@login_required
def relation_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        relation = Relation.objects.create(name=name)
        messages.success(request, 'Relation added successfully.')
        return redirect('congregation:relation_list')
    return render(request, 'congregation/settings/relation/add.html')

@login_required
def relation_edit(request, pk):
    relation = get_object_or_404(Relation, pk=pk)
    if request.method == 'POST':
        relation.name = request.POST.get('name')
        relation.save()
        messages.success(request, 'Relation updated successfully.')
        return redirect('congregation:relation_list')
    context = {
        'relation': relation,
    }
    return render(request, 'congregation/settings/relation/edit.html', context)

@login_required
def relation_delete(request, pk):
    relation = get_object_or_404(Relation, pk=pk)
    if request.method == 'POST':
        try:
            relation.delete()
            messages.success(request, 'Relation deleted successfully.')
        except models.ProtectedError:
            messages.error(request, 'Cannot delete this relation as it is being used by members.')
        return redirect('congregation:relation_list')
    context = {
        'relation': relation,
    }
    return render(request, 'congregation/settings/relation/delete.html', context)

# Member Views
@login_required
def member_list(request, family_id):
    family = get_object_or_404(Family, pk=family_id)
    members = Member.objects.filter(family=family)
    context = {
        'family': family,
        'members': members,
    }
    return render(request, 'congregation/member/list.html', context)

@login_required
def member_add(request, family_id):
    family = get_object_or_404(Family, pk=family_id)
    respects = Respect.objects.all()
    relations = Relation.objects.all()
    
    # Get next member number
    next_member_number = Member.get_next_number(family)
    
    if request.method == 'POST':
        respect = get_object_or_404(Respect, pk=request.POST.get('respect'))
        relation = get_object_or_404(Relation, pk=request.POST.get('relation'))
        
        # Get the member number from the form and ensure it's 2 digits
        member_number = request.POST.get('member_id', '').zfill(2)
        # Create member ID in format AREA-FAMILYNUM-MEMBERNUM
        member_id = f"{family.family_id}-{member_number}"
        
        member = Member.objects.create(
            family=family,
            member_id=member_id,
            aadhar_number=request.POST.get('aadhar_number'),
            respect=respect,
            initial=request.POST.get('initial', ''),
            name=request.POST.get('name'),
            relation=relation,
            sex=request.POST.get('sex'),
            dob=request.POST.get('dob'),
            dom=request.POST.get('dom') if request.POST.get('dom') else None,
            working=request.POST.get('working', ''),
            working_place=request.POST.get('working_place', ''),
            baptised=request.POST.get('baptised', '') == 'on',
            date_of_bap=request.POST.get('date_of_bap') if request.POST.get('date_of_bap') else None,
            conformed=request.POST.get('conformed', '') == 'on',
            date_of_conf=request.POST.get('date_of_conf') if request.POST.get('date_of_conf') else None,
            death=request.POST.get('death', '') == 'on',
            date_of_death=request.POST.get('date_of_death') if request.POST.get('date_of_death') else None
        )
        
        if 'image' in request.FILES:
            member.image = request.FILES['image']
            member.save()
        
        messages.success(request, 'Member added successfully.')
        return redirect('congregation:member_detail', pk=member.pk)
    
    context = {
        'family': family,
        'respects': respects,
        'relations': relations,
        'next_member_number': next_member_number,
    }
    return render(request, 'congregation/member/add.html', context)

@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    context = {
        'member': member,
    }
    return render(request, 'congregation/member/detail.html', context)

@login_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    respects = Respect.objects.all()
    relations = Relation.objects.all()
    family_members = Member.objects.filter(family=member.family).exclude(death=True)
    
    if request.method == 'POST':
        respect = get_object_or_404(Respect, pk=request.POST.get('respect'))
        relation = get_object_or_404(Relation, pk=request.POST.get('relation'))
        
        # Handle member ID change
        new_member_id = f"{member.family.family_id}-{request.POST.get('member_id', '').zfill(2)}"
        if new_member_id != member.member_id:
            # Check if the new member ID is unique
            if Member.objects.filter(member_id=new_member_id).exists():
                messages.error(request, 'This member ID is already in use. Please choose a different number.')
                context = {
                    'member': member,
                    'respects': respects,
                    'relations': relations,
                    'family_members': family_members,
                }
                return render(request, 'congregation/member/edit.html', context)
            member.member_id = new_member_id

        # Handle spouse relationship and marriage date
        spouse_id = request.POST.get('spouse')
        old_spouse = member.spouse
        new_spouse = None
        marriage_date = request.POST.get('dom') if request.POST.get('dom') else None
        
        if spouse_id:
            new_spouse = get_object_or_404(Member, pk=spouse_id)
            # Remove old spouse relationships if any
            if old_spouse and old_spouse != new_spouse:
                old_spouse.spouse = None
                old_spouse.dom = None
                old_spouse.save()
            # Set new spouse relationship both ways
            member.spouse = new_spouse
            member.dom = marriage_date
            new_spouse.spouse = member
            new_spouse.dom = marriage_date  # Sync marriage date
            new_spouse.save()
        else:
            # If no spouse selected, remove existing spouse relationship if any
            if old_spouse:
                old_spouse.spouse = None
                old_spouse.dom = None
                old_spouse.save()
            member.spouse = None
            member.dom = None
        
        member.respect = respect
        member.initial = request.POST.get('initial', '')
        member.name = request.POST.get('name')
        member.relation = relation
        member.sex = request.POST.get('sex')
        member.dob = request.POST.get('dob') if request.POST.get('dob') else None
        member.working = request.POST.get('working', '')
        member.working_place = request.POST.get('working_place', '')
        member.baptised = request.POST.get('baptised', '') == 'on'
        member.date_of_bap = request.POST.get('date_of_bap') if request.POST.get('date_of_bap') else None
        member.conformed = request.POST.get('conformed', '') == 'on'
        member.date_of_conf = request.POST.get('date_of_conf') if request.POST.get('date_of_conf') else None
        member.death = request.POST.get('death', '') == 'on'
        member.date_of_death = request.POST.get('date_of_death') if request.POST.get('date_of_death') else None
        
        if 'image' in request.FILES:
            member.image = request.FILES['image']
        
        member.save()
        messages.success(request, 'Member updated successfully.')
        return redirect('congregation:member_detail', pk=member.pk)
    
    context = {
        'member': member,
        'respects': respects,
        'relations': relations,
        'family_members': family_members,
    }
    return render(request, 'congregation/member/edit.html', context)

@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    family = member.family
    
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Member deleted successfully.')
        return redirect('congregation:member_list', family_id=family.pk)
    
    context = {
        'member': member,
    }
    return render(request, 'congregation/member/delete.html', context)

@login_required
def family_search(request):
    query = request.GET.get('q', '')
    church_id = request.GET.get('church')
    area_id = request.GET.get('area')
    fellowship_id = request.GET.get('fellowship')
    
    families = Family.objects.all()
    
    if church_id:
        families = families.filter(area__church_id=church_id)
    
    if area_id:
        families = families.filter(area_id=area_id)
    
    if fellowship_id:
        families = families.filter(fellowship_id=fellowship_id)
    
    if query:
        families = families.filter(
            Q(family_id__icontains=query) |
            Q(family_head__icontains=query) |
            Q(mobile__icontains=query) |
            Q(email__icontains=query) |
            Q(address__icontains=query)
        ).select_related('area', 'fellowship', 'respect')
    
    context = {
        'families': families,
        'query': query,
        'church_id': church_id,
        'area_id': area_id,
        'fellowship_id': fellowship_id
    }
    return render(request, 'congregation/search/family_results.html', context)

@login_required
def member_search(request):
    query = request.GET.get('q', '')
    church_id = request.GET.get('church')
    
    members = Member.objects.all()
    
    if church_id:
        members = members.filter(family__area__church_id=church_id)
    
    if query:
        members = members.filter(
            Q(member_id__icontains=query) |
            Q(name__icontains=query) |
            Q(aadhar_number__icontains=query) |
            Q(working__icontains=query) |
            Q(working_place__icontains=query)
        ).select_related('family', 'family__area', 'respect', 'relation')
    
    context = {
        'members': members,
        'query': query,
        'church_id': church_id
    }
    return render(request, 'congregation/search/member_results.html', context)

@login_required
def essentials(request):
    context = {
        'respects': Respect.objects.all().order_by('name'),
        'relations': Relation.objects.all().order_by('name'),
        'account_types': AccountType.objects.all().order_by('name'),
        'categories': PrimaryCategory.objects.all().order_by('name'),
    }
    return render(request, 'congregation/settings/essentials.html', context)

@login_required
def backup_restore(request):
    """View for database backup and restore operations"""
    return render(request, 'congregation/settings/backup_restore.html')

@login_required
def generate_backup(request):
    """Generate CSV backup of all members with their relationships"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="church_backup_{timestamp}.csv"'

    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    
    # Write CSV Header
    headers = [
        'Pastorate Name', 'Pastorate Short Name',
        'Church Name', 'Church Abode', 'Church Short Name',
        'Area Name', 'Area ID',
        'Fellowship Name', 'Fellowship ID', 'Fellowship Address',
        'Family ID', 'Family Position No',
        'Family Head Name', 'Family Respect', 'Family Initial',
        'Family Mobile', 'Family Email', 'Family Address', 'Family Prayer Points',
        'Member ID', 'Member Respect', 'Member Initial', 'Member Name',
        'Member Relation', 'Sex', 'DOB', 'DOM', 'Working', 'Working Place',
        'Baptised', 'Date of Baptism', 'Confirmed', 'Date of Confirmation',
        'Death', 'Date of Death', 'Aadhar Number', 'Spouse Member ID'
    ]
    writer.writerow(headers)

    # Get all members with related data
    members = Member.objects.select_related(
        'family',
        'family__area',
        'family__area__church',
        'family__area__church__pastorate',
        'family__fellowship',
        'respect',
        'relation',
        'spouse'
    ).all()

    for member in members:
        # Format dates to dd.mm.yyyy
        dob = member.dob.strftime('%d.%m.%Y') if member.dob else ''
        dom = member.dom.strftime('%d.%m.%Y') if member.dom else ''
        date_of_bap = member.date_of_bap.strftime('%d.%m.%Y') if member.date_of_bap else ''
        date_of_conf = member.date_of_conf.strftime('%d.%m.%Y') if member.date_of_conf else ''
        date_of_death = member.date_of_death.strftime('%d.%m.%Y') if member.date_of_death else ''

        # Create row data
        row = [
            member.family.area.church.pastorate.pastorate_name,
            member.family.area.church.pastorate.pastorate_short_name,
            member.family.area.church.church_name,
            member.family.area.church.abode,
            member.family.area.church.short_name,
            member.family.area.area_name,
            member.family.area.area_id,
            member.family.fellowship.fellowship_name,
            member.family.fellowship.fellowship_id,
            member.family.fellowship.address,
            member.family.family_id,
            member.family.position_no or '',
            member.family.family_head,
            member.family.respect.name,
            member.family.initial,
            member.family.mobile,
            member.family.email,
            member.family.address,
            member.family.prayer_points,
            member.member_id,
            member.respect.name,
            member.initial,
            member.name,
            member.relation.name,
            member.sex,
            dob,
            dom,
            member.working,
            member.working_place,
            'Yes' if member.baptised else 'No',
            date_of_bap,
            'Yes' if member.conformed else 'No',
            date_of_conf,
            'Yes' if member.death else 'No',
            date_of_death,
            member.aadhar_number,
            member.spouse.member_id if member.spouse else ''
        ]
        writer.writerow(row)

    return response

@login_required
def validate_restore(request):
    """Validate uploaded CSV file and show validation results"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=400)
    
    if 'csv_file' not in request.FILES:
        return JsonResponse({'error': 'No file was uploaded'}, status=400)

    try:
        csv_file: UploadedFile = request.FILES['csv_file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'Invalid file type. Please upload a CSV file'}, status=400)
        
        # Read and decode the file
        try:
            file_content = csv_file.read().decode('utf-8')
        except UnicodeDecodeError:
            return JsonResponse({'error': 'Invalid file encoding. Please ensure the file is UTF-8 encoded'}, status=400)
        
        # Store the file in session
        request.session['restore_file'] = file_content
        
        # Create CSV reader
        csv_data = io.StringIO(file_content)
        reader = csv.reader(csv_data)
        
        # Read headers
        try:
            headers = next(reader)
        except StopIteration:
            return JsonResponse({'error': 'The CSV file is empty'}, status=400)
            
        expected_headers = [
            'Pastorate Name', 'Pastorate Short Name',
            'Church Name', 'Church Abode', 'Church Short Name',
            'Area Name', 'Area ID',
            'Fellowship Name', 'Fellowship ID', 'Fellowship Address',
            'Family ID', 'Family Position No',
            'Family Head Name', 'Family Respect', 'Family Initial',
            'Family Mobile', 'Family Email', 'Family Address', 'Family Prayer Points',
            'Member ID', 'Member Respect', 'Member Initial', 'Member Name',
            'Member Relation', 'Sex', 'DOB', 'DOM', 'Working', 'Working Place',
            'Baptised', 'Date of Baptism', 'Confirmed', 'Date of Confirmation',
            'Death', 'Date of Death', 'Aadhar Number', 'Spouse Member ID'
        ]

        format_errors = []
        consistency_errors = []
        
        # Validate headers
        if headers != expected_headers:
            missing = set(expected_headers) - set(headers)
            extra = set(headers) - set(expected_headers)
            if missing:
                format_errors.append({
                    'line': 1,
                    'column': '',
                    'error': f'Missing columns: {", ".join(missing)}',
                    'solution': 'Add the missing columns to your CSV file'
                })
            if extra:
                format_errors.append({
                    'line': 1,
                    'column': '',
                    'error': f'Extra columns found: {", ".join(extra)}',
                    'solution': 'Remove the extra columns from your CSV file'
                })

        # Read all rows for validation
        try:
            rows = list(reader)
        except csv.Error as e:
            return JsonResponse({'error': f'Error reading CSV file: {str(e)}'}, status=400)
        
        if not rows:
            return JsonResponse({'error': 'The CSV file contains no data rows'}, status=400)
        
        # Statistics
        stats = {
            'total_records': len(rows),
            'members': len(rows),  # Each row is a member
            'families': len(set(row[10] for row in rows)),  # Unique Family IDs
            'fellowships': len(set(row[8] for row in rows)),  # Unique Fellowship IDs
        }

        # Store validation results in session
        request.session['validation_results'] = {
            'has_errors': bool(format_errors or consistency_errors),
            'format_errors': format_errors,
            'consistency_errors': consistency_errors,
            'stats': stats,
            'headers': headers,
            'preview_data': rows[:5] if rows else []  # First 5 rows for preview
        }

        return JsonResponse({
            'redirect_url': reverse('congregation:restore_validation')
        })

    except Exception as e:
        import traceback
        print('Error in validate_restore:', str(e))
        print(traceback.format_exc())
        return JsonResponse({
            'error': f'Error processing file: {str(e)}'
        }, status=400)

@login_required
def restore_validation(request):
    """Show validation results page"""
    # Get validation results from session
    results = request.session.get('validation_results', {
        'has_errors': True,
        'format_errors': [{'line': 1, 'column': '', 'error': 'No file uploaded', 'solution': 'Upload a file'}],
        'consistency_errors': [],
        'stats': {'total_records': 0, 'members': 0, 'families': 0, 'fellowships': 0},
        'headers': [],
        'preview_data': []
    })
    
    return render(request, 'congregation/settings/restore_validation.html', results)

@login_required
def perform_restore(request):
    """Perform the actual restore operation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    # Get the stored file content from session
    file_content = request.session.get('restore_file')
    if not file_content:
        return JsonResponse({'error': 'No file data found'}, status=400)

    try:
        # Create CSV reader
        csv_data = io.StringIO(file_content)
        reader = csv.reader(csv_data)
        headers = next(reader)  # Skip header row
        rows = list(reader)

        # Dictionary to store restore statistics and track created/updated entities
        stats = {
            'created': {
                'pastorates': 0,
                'churches': 0,
                'areas': 0,
                'fellowships': 0,
                'families': 0,
                'members': 0,
            },
            'updated': {
                'pastorates': 0,
                'churches': 0,
                'areas': 0,
                'fellowships': 0,
                'families': 0,
                'members': 0,
            },
            'errors': []
        }

        # Dictionaries to track entities by their unique identifiers
        pastorates = {}
        churches = {}
        areas = {}
        fellowships = {}
        families = {}
        members = {}

        # Process all rows within a transaction
        with transaction.atomic():
            # First pass: Create/update hierarchical entities
            for row in rows:
                try:
                    # Extract data from row
                    pastorate_data = {
                        'pastorate_name': row[0],
                        'pastorate_short_name': row[1],
                        'user': request.user
                    }
                    church_data = {
                        'church_name': row[2],
                        'abode': row[3],
                        'short_name': row[4]
                    }
                    area_data = {
                        'area_name': row[5],
                        'area_id': row[6]
                    }
                    fellowship_data = {
                        'fellowship_name': row[7],
                        'fellowship_id': row[8],
                        'address': row[9]
                    }
                    family_data = {
                        'family_id': row[10],
                        'position_no': int(row[11]) if row[11].strip() else None,
                        'family_head': row[12],
                        'initial': row[14],
                        'mobile': row[15],
                        'email': row[16],
                        'address': row[17],
                        'prayer_points': row[18]
                    }
                    member_data = {
                        'member_id': row[19],
                        'initial': row[21],
                        'name': row[22],
                        'sex': row[24],
                        'dob': datetime.strptime(row[25], '%d.%m.%Y').date() if row[25] else None,
                        'dom': datetime.strptime(row[26], '%d.%m.%Y').date() if row[26] else None,
                        'working': row[27],
                        'working_place': row[28],
                        'baptised': row[29] == 'Yes',
                        'date_of_bap': datetime.strptime(row[30], '%d.%m.%Y').date() if row[30] else None,
                        'conformed': row[31] == 'Yes',
                        'date_of_conf': datetime.strptime(row[32], '%d.%m.%Y').date() if row[32] else None,
                        'death': row[33] == 'Yes',
                        'date_of_death': datetime.strptime(row[34], '%d.%m.%Y').date() if row[34] else None,
                        'aadhar_number': row[35]
                    }

                    # Create or update Pastorate
                    pastorate, pastorate_created = Pastorate.objects.update_or_create(
                        pastorate_short_name=pastorate_data['pastorate_short_name'],
                        defaults=pastorate_data
                    )
                    stats['created' if pastorate_created else 'updated']['pastorates'] += 1
                    pastorates[pastorate_data['pastorate_short_name']] = pastorate

                    # Create or update Church
                    church, church_created = Church.objects.update_or_create(
                        short_name=church_data['short_name'],
                        pastorate=pastorate,
                        defaults=church_data
                    )
                    stats['created' if church_created else 'updated']['churches'] += 1
                    churches[church_data['short_name']] = church

                    # Create or update Area
                    area, area_created = Area.objects.update_or_create(
                        area_id=area_data['area_id'],
                        church=church,
                        defaults=area_data
                    )
                    stats['created' if area_created else 'updated']['areas'] += 1
                    areas[area_data['area_id']] = area

                    # Create or update Fellowship
                    fellowship, fellowship_created = Fellowship.objects.update_or_create(
                        fellowship_id=fellowship_data['fellowship_id'],
                        area=area,
                        defaults=fellowship_data
                    )
                    stats['created' if fellowship_created else 'updated']['fellowships'] += 1
                    fellowships[fellowship_data['fellowship_id']] = fellowship

                    # Get or create Respect and Relation
                    family_respect = Respect.objects.get_or_create(name=row[13])[0]
                    member_respect = Respect.objects.get_or_create(name=row[20])[0]
                    relation = Relation.objects.get_or_create(name=row[23])[0]

                    # Create or update Family
                    family, family_created = Family.objects.update_or_create(
                        family_id=family_data['family_id'],
                        defaults={
                            **family_data,
                            'area': area,
                            'fellowship': fellowship,
                            'respect': family_respect
                        }
                    )
                    stats['created' if family_created else 'updated']['families'] += 1
                    families[family_data['family_id']] = family

                    # Create or update Member
                    member, member_created = Member.objects.update_or_create(
                        member_id=member_data['member_id'],
                        defaults={
                            **member_data,
                            'family': family,
                            'respect': member_respect,
                            'relation': relation
                        }
                    )
                    stats['created' if member_created else 'updated']['members'] += 1
                    members[member_data['member_id']] = member

                except Exception as e:
                    stats['errors'].append({
                        'row': row[19],  # Member ID as reference
                        'error': str(e)
                    })

            # Second pass: Update spouse relationships
            for row in rows:
                member_id = row[19]
                spouse_id = row[35]
                
                if spouse_id and member_id in members and spouse_id in members:
                    member = members[member_id]
                    spouse = members[spouse_id]
                    
                    # Update spouse relationship both ways
                    member.spouse = spouse
                    member.save()
                    spouse.spouse = member
                    spouse.save()

        # Store restore report in session
        request.session['restore_report'] = {
            'stats': stats,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('congregation:restore_report')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def restore_report(request):
    """Show restore operation report"""
    report = request.session.get('restore_report', {
        'stats': {
            'created': {
                'pastorates': 0,
                'churches': 0,
                'areas': 0,
                'fellowships': 0,
                'families': 0,
                'members': 0,
            },
            'updated': {
                'pastorates': 0,
                'churches': 0,
                'areas': 0,
                'fellowships': 0,
                'families': 0,
                'members': 0,
            },
            'errors': []
        },
        'timestamp': None
    })
    return render(request, 'congregation/settings/restore_report.html', {'report': report})
