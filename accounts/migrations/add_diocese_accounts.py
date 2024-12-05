from django.db import migrations

def add_diocese_accounts(apps, schema_editor):
    """Add Diocese accounts to existing pastorates"""
    # Get the models
    Pastorate = apps.get_model('congregation', 'Pastorate')
    Account = apps.get_model('accounts', 'Account')
    AccountType = apps.get_model('accounts', 'AccountType')
    
    # Get or create General Account type
    general_type, _ = AccountType.objects.get_or_create(
        name='General Account',
        defaults={'description': 'For managing general transactions'}
    )
    
    # Get all existing pastorates
    pastorates = Pastorate.objects.all()
    
    # Create Diocese account for each pastorate if it doesn't exist
    for pastorate in pastorates:
        # Check if Diocese account already exists
        diocese_exists = Account.objects.filter(
            pastorate=pastorate,
            account_number__startswith='DIO-'
        ).exists()
        
        if not diocese_exists:
            Account.objects.create(
                name=f"{pastorate.pastorate_name} Diocese Account",
                account_type=general_type,
                account_number=f"DIO-{pastorate.id:03d}",
                description=f"Diocese account for {pastorate.pastorate_name}",
                pastorate=pastorate,
                level='pastorate'
            )

def remove_diocese_accounts(apps, schema_editor):
    """Remove Diocese accounts if migration is reversed"""
    Account = apps.get_model('accounts', 'Account')
    Account.objects.filter(account_number__startswith='DIO-').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),  # Replace with your last migration
        ('congregation', '0001_initial'),  # Replace with your last congregation migration
    ]

    operations = [
        migrations.RunPython(add_diocese_accounts, remove_diocese_accounts),
    ] 