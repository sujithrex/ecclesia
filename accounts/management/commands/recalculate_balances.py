from django.core.management.base import BaseCommand
from django.db import models
from accounts.models import Account, Transaction

class Command(BaseCommand):
    help = 'Recalculates all account balances'

    def handle(self, *args, **options):
        accounts = Account.objects.all()
        self.stdout.write('Starting balance recalculation...')
        
        for account in accounts:
            self.stdout.write(f"\nCalculating for {account.name}:")
            # Reset balance
            account.balance = 0
            
            # Calculate credits (receipts, offerings, custom credits, contra credits)
            credit_transactions = Transaction.objects.filter(
                account=account,
                transaction_type__in=['receipt', 'offering', 'custom_credit', 'contra_credit']
            )
            credits = credit_transactions.aggregate(total=models.Sum('amount'))['total'] or 0
            
            self.stdout.write("Credit transactions:")
            for t in credit_transactions:
                self.stdout.write(f"  {t.transaction_type}: +{t.amount} ({t.description})")
            
            # Calculate debits (bills, custom debits, aqudence, contra debits)
            debit_transactions = Transaction.objects.filter(
                account=account,
                transaction_type__in=['bill', 'custom_debit', 'aqudence', 'contra']
            )
            debits = debit_transactions.aggregate(total=models.Sum('amount'))['total'] or 0
            
            self.stdout.write("Debit transactions:")
            for t in debit_transactions:
                self.stdout.write(f"  {t.transaction_type}: -{t.amount} ({t.description})")
            
            # Update balance
            account.balance = credits - debits
            account.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSummary for {account.name}:'
                    f'\n  Credits: +{credits}'
                    f'\n  Debits: -{debits}'
                    f'\n  Final Balance: {account.balance}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('All account balances have been recalculated'))