from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Transaction, TransactionHistory

@login_required
def transaction_history(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    history = TransactionHistory.objects.filter(
        transaction=transaction
    ).select_related(
        'modified_by'
    ).order_by('-modified_at')
    
    context = {
        'transaction': transaction,
        'history': history,
    }
    return render(request, 'accounts/transaction/history.html', context) 