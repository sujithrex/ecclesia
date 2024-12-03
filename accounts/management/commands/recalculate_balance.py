from django.core.management.base import BaseCommand
from accounts.models import Account, Transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Recalculates account balances based on transactions'

    def handle(self, *args, **options):
        accounts = Account.objects.all()
        for account in accounts:
            # Reset balance to 0
            account.balance = Decimal('0')
            
            # Calculate balance from all transactions
            transactions = Transaction.objects.filter(account=account).order_by('transaction_date', 'created_at')
            for transaction in transactions:
                if transaction.transaction_type == 'credit':
                    account.balance += transaction.amount
                else:
                    account.balance -= transaction.amount
            
            account.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully recalculated balance for account {account.name}: ₹{account.balance}'
                )
            ) 