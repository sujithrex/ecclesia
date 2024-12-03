from django.core.management.base import BaseCommand
from accounts.models import TransactionCategory, AccountType, LedgerGroup

class Command(BaseCommand):
    help = 'Creates default transaction categories, account types, and ledger groups'

    def handle(self, *args, **kwargs):
        # Create default account types
        account_types = [
            {
                'name': 'Cash',
                'description': 'For managing cash transactions',
            },
            {
                'name': 'Bank',
                'description': 'For managing bank account transactions',
            },
        ]
        
        for account_type in account_types:
            AccountType.objects.get_or_create(**account_type)
            self.stdout.write(f'Created account type: {account_type["name"]}')
        
        # Create default ledger groups
        ledger_groups = [
            {
                'name': 'Income',
                'description': 'Regular income entries',
                'transaction_type': 'credit',
            },
            {
                'name': 'Expense',
                'description': 'Regular expense entries',
                'transaction_type': 'debit',
            },
            {
                'name': 'Salary',
                'description': 'Salary related transactions',
                'transaction_type': 'debit',
            },
            {
                'name': 'Utilities',
                'description': 'Utility bill payments',
                'transaction_type': 'debit',
            },
            {
                'name': 'Maintenance',
                'description': 'Maintenance and repair expenses',
                'transaction_type': 'debit',
            },
            {
                'name': 'Donations',
                'description': 'Donation receipts',
                'transaction_type': 'credit',
            },
            {
                'name': 'Special Offerings',
                'description': 'Special offering collections',
                'transaction_type': 'credit',
            },
        ]
        
        for group in ledger_groups:
            ledger_group, created = LedgerGroup.objects.get_or_create(**group)
            self.stdout.write(f'Created ledger group: {ledger_group.name}')
        
        # Create default transaction categories
        pastorate_categories = [
            {
                'name': 'Receipts',
                'category_type': 'receipts',
                'transaction_type': 'credit',
                'requires_number': True,
                'requires_church': False,
                'is_active': True,
                'pastorate_only': True,
            },
            {
                'name': 'Church Offertory',
                'category_type': 'offertory',
                'transaction_type': 'credit',
                'requires_number': False,
                'requires_church': True,
                'is_active': True,
                'pastorate_only': True,
            },
            {
                'name': 'Bills and Vouchers',
                'category_type': 'bills',
                'transaction_type': 'debit',
                'requires_number': True,
                'requires_church': False,
                'is_active': True,
                'pastorate_only': True,
            },
            {
                'name': 'Acquittance',
                'category_type': 'acquittance',
                'transaction_type': 'debit',
                'requires_number': False,
                'requires_church': False,
                'is_active': True,
                'pastorate_only': True,
            },
        ]
        
        # Create pastorate-only categories
        for category in pastorate_categories:
            TransactionCategory.objects.get_or_create(**category)
            self.stdout.write(f'Created pastorate category: {category["name"]}') 