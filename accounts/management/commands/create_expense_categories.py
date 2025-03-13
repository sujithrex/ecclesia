from django.core.management.base import BaseCommand
from accounts.models import PrimaryCategory, SecondaryCategory

class Command(BaseCommand):
    help = 'Creates default expense categories for church accounting'

    def handle(self, *args, **kwargs):
        # Define primary categories
        primary_categories = [
            {
                'name': 'Capital Expenditure',
                'description': 'Long-term assets and investments',
                'transaction_type': 'debit',
                'is_active': True
            },
            {
                'name': 'Employee Benefit Expenses',
                'description': 'Salaries and benefits for staff and clergy',
                'transaction_type': 'debit',
                'is_active': True
            },
            {
                'name': 'Grants, Contributions & Donations',
                'description': 'Outgoing grants and donations',
                'transaction_type': 'debit',
                'is_active': True
            },
            {
                'name': 'Other Exp./Minist.Work',
                'description': 'Expenses related to ministry activities',
                'transaction_type': 'debit',
                'is_active': True
            },
            {
                'name': 'Other Exp. - Admin',
                'description': 'Administrative and operational expenses',
                'transaction_type': 'debit',
                'is_active': True
            },
            {
                'name': 'Inter Unit Expenses',
                'description': 'Payments to other church units and departments',
                'transaction_type': 'debit',
                'is_active': True
            },
            {
                'name': 'Other Current Liability-Others',
                'description': 'Other current liabilities and payments',
                'transaction_type': 'debit',
                'is_active': True
            },
            {
                'name': 'Other Loans & Advances',
                'description': 'Loan disbursements and advances',
                'transaction_type': 'debit',
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
            # Capital Expenditure
            {'name': 'Furniture & Fittings', 'primary': 'Capital Expenditure'},
            {'name': 'Land Purchased', 'primary': 'Capital Expenditure'},
            {'name': 'New Buildings (completed)', 'primary': 'Capital Expenditure'},
            {'name': 'Office Equipments', 'primary': 'Capital Expenditure'},
            {'name': 'Adv. Payment Build.', 'primary': 'Capital Expenditure'},
            
            # Employee Benefit Expenses
            {'name': 'Salary (STAFF)', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Clergy Salary & Allowences', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Wife Allowence Payment', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Clergy Dio. Pension Fund', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Clergy Dio. Provident Fund', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Diocesan Medical Aid Fund', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Diocesan Fly Benefit Fund', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Clergy Income Tax', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Clergy Staff Welfare Fund', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Past. Workers Xmas gift', 'primary': 'Employee Benefit Expenses'},
            {'name': 'Past. Com. &Workers. Xmas Gift', 'primary': 'Employee Benefit Expenses'},
            
            # Grants, Contributions & Donations
            {'name': 'Donations Payment', 'primary': 'Grants, Contributions & Donations'},
            {'name': 'Grants/ Contribution', 'primary': 'Grants, Contributions & Donations'},
            
            # Other Exp./Minist.Work
            {'name': 'Committee Confer. & Meeting', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Convention', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Dio Cat.&Candi for ordin.', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Fasting Prayer Expen', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Festival Expenses', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Harvest Festival Exp.', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Holy Communion Exp.', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Past.Committ.Retreat', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Trumphat Festival Exp.', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'VBS', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Pastorate Retreat', 'primary': 'Other Exp./Minist.Work'},
            {'name': 'Past.Youth,Men,Women Retr. Exp', 'primary': 'Other Exp./Minist.Work'},
            
            # Other Exp. - Admin
            {'name': 'Audit fees', 'primary': 'Other Exp. - Admin'},
            {'name': 'Electr. Charge- Church', 'primary': 'Other Exp. - Admin'},
            {'name': 'Elec.ChargeParsonag.', 'primary': 'Other Exp. - Admin'},
            {'name': 'Hospitality', 'primary': 'Other Exp. - Admin'},
            {'name': 'Miscelleous Expenses', 'primary': 'Other Exp. - Admin'},
            {'name': 'Printing & Stationary', 'primary': 'Other Exp. - Admin'},
            {'name': 'Rates &Property Tax', 'primary': 'Other Exp. - Admin'},
            {'name': 'Repair&Maint. Build', 'primary': 'Other Exp. - Admin'},
            {'name': 'Repair&Maint.Plant&E', 'primary': 'Other Exp. - Admin'},
            {'name': 'School Expenses', 'primary': 'Other Exp. - Admin'},
            {'name': 'Parsonage White Wash', 'primary': 'Other Exp. - Admin'},
            {'name': 'Telephone Bill- Office', 'primary': 'Other Exp. - Admin'},
            {'name': 'Telep.Bill- Parsonage', 'primary': 'Other Exp. - Admin'},
            {'name': 'T.A and Conveyance', 'primary': 'Other Exp. - Admin'},
            
            # Inter Unit Expenses
            {'name': 'Assesment-Dio. (Past.)', 'primary': 'Inter Unit Expenses'},
            {'name': 'Paym .to Anbin Illam', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Church Council', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Children Mission', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Common Q.P.', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Communication', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to all Dept. Past.Cont', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Counselling', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Deaf Mission', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to DioceseMagazine', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Deaf School', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Diocese SWF.', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to DME', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to North Council', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Child Care', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Mens', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Mentally RTD', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Self Denial & Jews', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Womens', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Vision', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Youth', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Pastorate', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Confirmation Off.', 'primary': 'Inter Unit Expenses'},
            {'name': 'Payment to Ecology Dept.', 'primary': 'Inter Unit Expenses'},
            
            # Other Current Liability-Others
            {'name': 'Other Current Liability', 'primary': 'Other Current Liability-Others'},
            
            # Other Loans & Advances
            {'name': 'Clergy Dio PF Loan Recov.', 'primary': 'Other Loans & Advances'},
            {'name': 'Clergy Staff Welf. Fund Loan', 'primary': 'Other Loans & Advances'},
            {'name': 'Clergy Vehicle Loan', 'primary': 'Other Loans & Advances'},
            {'name': 'Advances', 'primary': 'Other Loans & Advances'},
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
        
        self.stdout.write(self.style.SUCCESS('Expense categories setup complete!'))