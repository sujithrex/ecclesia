from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Account, Transaction, DioceseTransaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Recalculates and fixes all account balances based on transaction history'

    def handle(self, *args, **options):
        self.stdout.write('Starting account balance recalculation...')
        
        try:
            with transaction.atomic():
                # Reset all account balances to zero
                Account.objects.all().update(balance=Decimal('0.00'))
                self.stdout.write('Reset all account balances to zero')
                
                # Process regular transactions
                for txn in Transaction.objects.all().order_by('transaction_date', 'created_at'):
                    account = txn.account
                    if txn.transaction_type == 'credit':
                        account.balance += txn.amount
                    else:
                        account.balance -= txn.amount
                    account.save()
                
                self.stdout.write('Processed regular transactions')
                
                # Process diocese transactions
                for txn in DioceseTransaction.objects.all().order_by('transaction_date', 'created_at'):
                    account = txn.account
                    
                    # Update main account
                    if txn.transaction_type == 'credit':
                        account.balance += txn.amount
                    else:
                        account.balance -= txn.amount
                    account.save()
                    
                    # Update contra account if it's a contra entry
                    if txn.is_contra and txn.contra_account:
                        contra_account = txn.contra_account
                        if txn.transaction_type == 'credit':
                            contra_account.balance -= txn.amount
                        else:
                            contra_account.balance += txn.amount
                        contra_account.save()
                
                self.stdout.write('Processed diocese transactions')
                
            self.stdout.write(self.style.SUCCESS('Successfully recalculated all account balances'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise 