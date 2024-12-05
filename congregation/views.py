from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pastorate, Church, Area, Fellowship, Family, Respect, Relation, Member
from django.db.models import Count, F, Q
from datetime import date
from django.core.paginator import Paginator
from accounts.models import AccountType, TransactionHistory, LedgerGroup

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
        pastorate.delete()
        messages.success(request, 'Pastorate deleted successfully.')
        return redirect('congregation:pastorate_list')
    return render(request, 'congregation/pastorate/delete.html', {
        'pastorate': pastorate
    })

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
        'ledger_groups': LedgerGroup.objects.all().order_by('name'),
        'transaction_history': TransactionHistory.objects.select_related(
            'transaction', 
            'modified_by'
        ).order_by('-modified_at')[:10]  # Get last 10 changes
    }
    return render(request, 'congregation/settings/essentials.html', context)
