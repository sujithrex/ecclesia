from django.db import models
from django.core.validators import MinValueValidator
from congregation.models import Pastorate, Church
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class AccountType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Account(models.Model):
    ACCOUNT_LEVELS = [
        ('pastorate', 'Pastorate Level'),
        ('church', 'Church Level'),
    ]
    
    name = models.CharField(max_length=100)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    pastorate = models.ForeignKey(
        Pastorate, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='accounts'
    )
    church = models.ForeignKey(
        Church, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='accounts'
    )
    level = models.CharField(max_length=20, choices=ACCOUNT_LEVELS)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('pastorate', 'name'),
            ('church', 'name'),
        ]
    
    def __str__(self):
        if self.level == 'pastorate':
            return f"{self.pastorate.pastorate_name} - {self.name}"
        return f"{self.church.church_name} - {self.name}"

class PrimaryCategory(models.Model):
    """Primary transaction categories like Income, Expense"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Primary Categories"

    def __str__(self):
        return f"{self.name} ({self.get_transaction_type_display()})"

class SecondaryCategory(models.Model):
    """Secondary transaction categories like Receipts, Bills, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    primary_category = models.ForeignKey(PrimaryCategory, on_delete=models.PROTECT, related_name='secondary_categories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Secondary Categories"

    def __str__(self):
        return f"{self.primary_category.name} - {self.name}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('receipt', 'Receipt'),
        ('bill', 'Bill/Voucher'),
        ('aqudence', 'Aqudence'),
        ('offering', 'Church Offering'),
        ('custom_debit', 'Custom Debit'),
        ('custom_credit', 'Custom Credit'),
        ('contra', 'Contra Entry (Debit)'),
        ('contra_credit', 'Contra Entry (Credit)'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    to_account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True, 
                                 related_name='incoming_transactions', help_text='For contra debit entries only')
    from_account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='outgoing_transactions', help_text='For contra credit entries only')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    
    # Category fields
    primary_category = models.ForeignKey(PrimaryCategory, on_delete=models.PROTECT, null=True, blank=True)
    secondary_category = models.ForeignKey(SecondaryCategory, on_delete=models.PROTECT, null=True, blank=True)
    
    # Fields for different transaction types
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    aqudence_number = models.CharField(max_length=50, blank=True, null=True)
    aqudence_ref = models.CharField(max_length=100, blank=True, null=True)
    family_name = models.CharField(max_length=100, blank=True, null=True)
    member_name = models.CharField(max_length=100, blank=True, null=True)
    church = models.ForeignKey(Church, on_delete=models.PROTECT, null=True, blank=True)
    
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='created_transactions', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.transaction_type == 'receipt':
            return f"Receipt #{self.receipt_number}"
        elif self.transaction_type == 'bill':
            return f"Bill/Voucher #{self.reference_number}"
        elif self.transaction_type == 'aqudence':
            return f"Aqudence #{self.aqudence_number}"
        elif self.transaction_type == 'offering':
            return f"Offering from {self.church.church_name}"
        elif self.transaction_type == 'contra':
            return f"Contra Debit: {self.account.name} → {self.to_account.name}"
        elif self.transaction_type == 'contra_credit':
            return f"Contra Credit: {self.from_account.name} → {self.account.name}"
        else:
            return f"{self.get_transaction_type_display()} #{self.reference_number}"

class TransactionHistory(models.Model):
    """Model to track changes in transactions"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='history')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    aqudence_number = models.CharField(max_length=50, blank=True, null=True)
    aqudence_ref = models.CharField(max_length=100, blank=True, null=True)
    family_name = models.CharField(max_length=100, blank=True, null=True)
    member_name = models.CharField(max_length=100, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True)
    
    class Meta:
        ordering = ['-modified_at']
    
    def __str__(self):
        return f"History for {self.transaction}"

@receiver(post_save, sender=Pastorate)
def create_pastorate_accounts(sender, instance, created, **kwargs):
    """Create default accounts when a new pastorate is created"""
    if created:
        create_default_accounts(instance, 'pastorate')

@receiver(post_save, sender=Church)
def create_church_accounts(sender, instance, created, **kwargs):
    """Create default accounts when a new church is created"""
    if created:
        create_default_accounts(instance, 'church')

def create_default_accounts(entity, level):
    """Helper function to create default cash and bank accounts"""
    # Get or create the account types
    cash_type, _ = AccountType.objects.get_or_create(
        name='Cash Account',
        defaults={'description': 'For managing physical cash transactions'}
    )
    bank_type, _ = AccountType.objects.get_or_create(
        name='Bank Account',
        defaults={'description': 'For managing bank transactions'}
    )
    
    # Create accounts based on level
    if level == 'pastorate':
        # Create cash account
        Account.objects.create(
            name=f"{entity.pastorate_name} Cash Account",
            account_type=cash_type,
            account_number=f"CASH-{entity.id:03d}",
            description=f"Default cash account for {entity.pastorate_name}",
            pastorate=entity,
            level='pastorate'
        )
        
        # Create bank account
        Account.objects.create(
            name=f"{entity.pastorate_name} Bank Account",
            account_type=bank_type,
            account_number=f"BANK-{entity.id:03d}",
            description=f"Default bank account for {entity.pastorate_name}",
            pastorate=entity,
            level='pastorate'
        )
    else:
        # Create cash account
        Account.objects.create(
            name=f"{entity.church_name} Cash Account",
            account_type=cash_type,
            account_number=f"CASH-{entity.pastorate.id:03d}-{entity.id:03d}",
            description=f"Default cash account for {entity.church_name}",
            church=entity,
            level='church'
        )
        
        # Create bank account
        Account.objects.create(
            name=f"{entity.church_name} Bank Account",
            account_type=bank_type,
            account_number=f"BANK-{entity.pastorate.id:03d}-{entity.id:03d}",
            description=f"Default bank account for {entity.church_name}",
            church=entity,
            level='church'
        )

@receiver(post_save, sender=Transaction)
def update_account_balances(sender, instance, created, **kwargs):
    """Update account balances when a transaction is saved"""
    # Get all transactions for the primary account
    account = instance.account
    account.balance = 0  # Reset balance
    
    # Calculate credits (receipts, offerings, custom credits, contra credits)
    credits = Transaction.objects.filter(
        account=account,
        transaction_type__in=['receipt', 'offering', 'custom_credit', 'contra_credit']
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Calculate debits (bills, custom debits, aqudence, contra debits)
    debits = Transaction.objects.filter(
        account=account,
        transaction_type__in=['bill', 'custom_debit', 'aqudence', 'contra']
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Update balance
    account.balance = credits - debits
    print(f"\nUpdating balance for {account.name}:")
    print(f"Credits (including contra credits): {credits}")
    print(f"Debits (including contra debits): {debits}")
    print(f"Final Balance: {account.balance}")
    account.save()
    
    # If this is a contra entry, also update the other account's balance
    if instance.transaction_type == 'contra' and instance.to_account:
        to_account = instance.to_account
        to_account.balance = 0  # Reset balance
        
        # Calculate credits for receiving account
        to_credits = Transaction.objects.filter(
            account=to_account,
            transaction_type__in=['receipt', 'offering', 'custom_credit', 'contra_credit']
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Calculate debits for receiving account
        to_debits = Transaction.objects.filter(
            account=to_account,
            transaction_type__in=['bill', 'custom_debit', 'aqudence', 'contra']
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Update receiving account balance
        to_account.balance = to_credits - to_debits
        print(f"\nUpdating balance for {to_account.name} (receiving account):")
        print(f"Credits (including contra credits): {to_credits}")
        print(f"Debits (including contra debits): {to_debits}")
        print(f"Final Balance: {to_account.balance}")
        to_account.save()
