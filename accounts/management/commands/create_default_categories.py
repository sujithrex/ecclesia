from django.core.management.base import BaseCommand
from accounts.models import TransactionCategory, AccountType, LedgerGroup, DioceseCategory, DioceseContraCategory

class Command(BaseCommand):
    help = 'Creates default transaction categories, account types, ledger groups, and diocese categories'

    def handle(self, *args, **kwargs):
        # Create default account types
        account_types = [
            {
                'name': 'Cash Account',
                'description': 'For managing cash transactions',
            },
            {
                'name': 'Bank Account',
                'description': 'For managing bank account transactions',
            },
        ]
        
        for account_type in account_types:
            AccountType.objects.get_or_create(**account_type)
            self.stdout.write(f'Created account type: {account_type["name"]}')
        
        # Create categories available to all accounts
        common_categories = [
            {
                'name': 'Receipts',
                'category_type': 'receipts',
                'transaction_type': 'credit',
                'requires_number': True,
                'requires_church': False,
                'is_active': True,
                'pastorate_only': False,
            },
            {
                'name': 'Bills and Vouchers',
                'category_type': 'bills',
                'transaction_type': 'debit',
                'requires_number': True,
                'requires_church': False,
                'is_active': True,
                'pastorate_only': False,
            },
        ]
        
        # Create pastorate-only categories
        pastorate_categories = [
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
                'name': 'Acquittance',
                'category_type': 'acquittance',
                'transaction_type': 'debit',
                'requires_number': False,
                'requires_church': False,
                'is_active': True,
                'pastorate_only': True,
            },
        ]
        
        # Create common categories (available to all)
        for category in common_categories:
            TransactionCategory.objects.get_or_create(**category)
            self.stdout.write(f'Created common category: {category["name"]}')
            
        # Create pastorate-only categories
        for category in pastorate_categories:
            TransactionCategory.objects.get_or_create(**category)
            self.stdout.write(f'Created pastorate category: {category["name"]}')
        
        # Create default diocese contra categories
        contra_categories = [
            {
                'name': 'Cash to Bank',
                'transaction_type': 'debit',
                'is_active': True,
            },
            {
                'name': 'Bank to Cash',
                'transaction_type': 'credit',
                'is_active': True,
            },
        ]
        
        for category in contra_categories:
            DioceseContraCategory.objects.get_or_create(**category)
            self.stdout.write(f'Created diocese contra category: {category["name"]}')

        