from django.core.management.base import BaseCommand
from accounts.models import PrimaryCategory, SecondaryCategory

class Command(BaseCommand):
    help = 'Creates default income categories for church accounting'

    def handle(self, *args, **kwargs):
        # Define primary categories
        primary_categories = [
            {
                'name': 'Collections-Offerings',
                'description': 'Regular and special offerings collected',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Miscellaneous Income',
                'description': 'Other miscellaneous income sources',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Sangam Collections',
                'description': 'Collections from Sangam groups',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Interest Income',
                'description': 'Income from interest and bank deposits',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Offer.&Collections for Depart.',
                'description': 'Offerings designated for specific departments',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Rental Income',
                'description': 'Income from property rentals',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Revenue From Operation',
                'description': 'Revenue from church operations',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Inter Unit Receipts',
                'description': 'Receipts from diocesan and other church units',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Clergy Funds',
                'description': 'Funds related to clergy benefits and welfare',
                'transaction_type': 'credit',
                'is_active': True
            },
            {
                'name': 'Loan Recoveries',
                'description': 'Recovery of loans and advances',
                'transaction_type': 'credit',
                'is_active': True
            },
        ]
        
        # Create primary categories
        primary_category_objects = {}
        for category in primary_categories:
            primary, created = PrimaryCategory.objects.get_or_create(
                name=category['name'],
                defaults={
                    'description': category['description'],
                    'transaction_type': category['transaction_type'],
                    'is_active': category['is_active']
                }
            )
            primary_category_objects[category['name']] = primary
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created primary category: {primary.name}'))
            else:
                self.stdout.write(f'Primary category already exists: {primary.name}')
        
        # Define secondary categories
        secondary_categories = [
            # Collections-Offerings
            {'name': 'Baptism Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Church Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Harvest Festival Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Holy Communion Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'House Visit Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Marriage Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Miscellaneous Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Sunday Collections', 'primary': 'Collections-Offerings'},
            {'name': 'Thanks Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Tithe Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Trumphet Festival', 'primary': 'Collections-Offerings'},
            {'name': 'Self Denial Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'One Day Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Jews Offertory', 'primary': 'Collections-Offerings'},
            {'name': 'Vision Collection', 'primary': 'Collections-Offerings'},
            {'name': 'Local Church Offerings', 'primary': 'Collections-Offerings'},
            {'name': 'Light Offering', 'primary': 'Collections-Offerings'},
            {'name': 'Cottage Prayer', 'primary': 'Collections-Offerings'},
            {'name': 'Church Growth Offerings', 'primary': 'Collections-Offerings'},
            {'name': 'Auction', 'primary': 'Collections-Offerings'},
            {'name': 'Harvest Festival Offertory - Auction', 'primary': 'Collections-Offerings'},
            {'name': 'Harvest Festival Offertory - Donation', 'primary': 'Collections-Offerings'},
            {'name': 'Harvest Festival Offertory - Auction', 'primary': 'Collections-Offerings'},
            
            # Miscellaneous Income
            {'name': 'Miscellaneous Collection', 'primary': 'Miscellaneous Income'},
            {'name': 'Miscellaneous Income', 'primary': 'Miscellaneous Income'},
            {'name': 'Miscellaneous Collections', 'primary': 'Miscellaneous Income'},
            {'name': 'Other Income', 'primary': 'Miscellaneous Income'},
            {'name': 'Others', 'primary': 'Miscellaneous Income'},
            
            # Sangam Collections
            {'name': 'Sangam-CW/DW', 'primary': 'Sangam Collections'},
            {'name': 'Sangam-Sabai', 'primary': 'Sangam Collections'},
            
            # Interest Income
            {'name': 'Interest-Savings Bank', 'primary': 'Interest Income'},
            {'name': 'Interest Income', 'primary': 'Interest Income'},
            {'name': 'Bank Income', 'primary': 'Interest Income'},
            
            # Offer.&Collections for Depart.
            {'name': 'Anbin Illam-Off/Collections', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Children Mission Off/Collections', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Common Question Paper', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Communication off./Collections', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Counselling offer/Collections', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Deaf Ministry Off./Collect.', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Deaf School Off./Collection', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Diocesan School Welfare Fund', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'DME Offertory/Collections', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'ChildCare/Edn. Develop. Coll.', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Elem./Middle School Income', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'IMS Offertory/Collection', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'LCF Offert/Collection', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Men-Offer./Collections', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Mentally Rtd Off/Coll', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Pastorate S.W.F.', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Women\'s-Off/Collection', 'primary': 'Offer.&Collections for Depart.'},
            {'name': 'Youth-Offertory/Collections', 'primary': 'Offer.&Collections for Depart.'},
            
            # Rental Income
            {'name': 'Rent-Building & Land Rent', 'primary': 'Rental Income'},
            {'name': 'Rent Land', 'primary': 'Rental Income'},
            {'name': 'Parish Hall / Multipurpose Hall', 'primary': 'Rental Income'},
            {'name': 'Parish Hall / Multipurpose Hall EB', 'primary': 'Rental Income'},
            {'name': 'Parish Hall / Multipurpose Hall Caution Deposite', 'primary': 'Rental Income'},
            
            # Revenue From Operation
            {'name': 'Donation-Receipt', 'primary': 'Revenue From Operation'},
            
            # Inter Unit Receipts
            {'name': 'Candidate for Ordination-Dio.', 'primary': 'Inter Unit Receipts'},
            {'name': 'Clergy Salary & Allowance (Dio)', 'primary': 'Inter Unit Receipts'},
            {'name': 'Rock Hall (From Dio)', 'primary': 'Inter Unit Receipts'},
            {'name': 'Wife Allowence (From Dio)', 'primary': 'Inter Unit Receipts'},
            {'name': 'Xmas Gift', 'primary': 'Inter Unit Receipts'},
            
            # Clergy Funds
            {'name': 'Clergy Diocesan Pension Fund', 'primary': 'Clergy Funds'},
            {'name': 'Clergy Diocesan Provident Fund', 'primary': 'Clergy Funds'},
            {'name': 'DMAF', 'primary': 'Clergy Funds'},
            {'name': 'Diocesan Family Benefit Fund', 'primary': 'Clergy Funds'},
            {'name': 'Clergy Income Tax', 'primary': 'Clergy Funds'},
            {'name': 'Clergy Staff Welfare Fund', 'primary': 'Clergy Funds'},
            
            # Loan Recoveries
            {'name': 'Clergy Dio PF Loan Recovery', 'primary': 'Loan Recoveries'},
            {'name': 'CSWF Loan', 'primary': 'Loan Recoveries'},
            {'name': 'Clergy Vehicle Loan', 'primary': 'Loan Recoveries'},
            {'name': 'CSWF Loan Refunds', 'primary': 'Loan Recoveries'},
            {'name': 'Other Loans & Advances', 'primary': 'Loan Recoveries'},
            {'name': 'Advances', 'primary': 'Loan Recoveries'},
        ]
        
        # Create secondary categories
        for category in secondary_categories:
            primary = primary_category_objects.get(category['primary'])
            if primary:
                secondary, created = SecondaryCategory.objects.get_or_create(
                    name=category['name'],
                    primary_category=primary,
                    defaults={
                        'description': f"{category['name']} under {primary.name}",
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created secondary category: {secondary.name}'))
                else:
                    self.stdout.write(f'Secondary category already exists: {secondary.name}')
            else:
                self.stdout.write(self.style.ERROR(f'Primary category not found for: {category["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('Income categories setup complete!'))