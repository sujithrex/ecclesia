from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return redirect('accounts:pastorate_list') 