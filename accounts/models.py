from django.db import models
from django.core.validators import MinValueValidator
from congregation.models import Pastorate, Church
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings

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
    
    def get_monthly_stats(self):
        """Get monthly transaction statistics"""
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        monthly_transactions = self.transactions.filter(
            transaction_date__month=current_month,
            transaction_date__year=current_year
        )
        
        total_credits = monthly_transactions.filter(
            transaction_type='credit'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        total_debits = monthly_transactions.filter(
            transaction_type='debit'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return {
            'total_credits': total_credits,
            'total_debits': total_debits,
            'net_change': total_credits - total_debits,
            'transaction_count': monthly_transactions.count()
        }

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    account = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=50, unique=True)
    transaction_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name='created_transactions',
        null=True,
        blank=True
    )
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.reference_number = f"TXN-{timestamp}"
        
        # Get the user who is making the change
        user = kwargs.pop('user', None)
        
        # If this is an existing transaction
        if self.pk:
            # Get the old instance from the database
            old_instance = Transaction.objects.get(pk=self.pk)
            
            # Create history record if there are changes
            if (old_instance.amount != self.amount or 
                old_instance.transaction_type != self.transaction_type or
                old_instance.description != self.description or
                old_instance.transaction_date != self.transaction_date):
                
                TransactionHistory.objects.create(
                    transaction=self,
                    amount=old_instance.amount,
                    description=old_instance.description,
                    transaction_type=old_instance.transaction_type,
                    transaction_date=old_instance.transaction_date,
                    modified_by=user
                )
                
                # Update account balance
                if old_instance.transaction_type == 'credit':
                    self.account.balance -= old_instance.amount
                else:
                    self.account.balance += old_instance.amount
        
        # Update account balance with new values
        if self.transaction_type == 'credit':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        
        self.account.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_number} - {self.account.name}"

class TransactionHistory(models.Model):
    """Model to track changes in transactions"""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='history'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    transaction_type = models.CharField(max_length=10, choices=Transaction.TRANSACTION_TYPES)
    transaction_date = models.DateTimeField()
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name='modified_transactions',
        null=True
    )
    
    class Meta:
        ordering = ['-modified_at']
    
    def __str__(self):
        return f"History for {self.transaction.reference_number}"

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

class LedgerGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=10, choices=Transaction.TRANSACTION_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class TransactionCategory(models.Model):
    CATEGORY_TYPES = [
        ('receipts', 'Receipts'),
        ('offertory', 'Church Offertory'),
        ('bills', 'Bills and Vouchers'),
        ('acquittance', 'Acquittance'),
        ('ledger', 'Ledger Entry'),
    ]
    
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    transaction_type = models.CharField(max_length=10, choices=Transaction.TRANSACTION_TYPES)
    is_active = models.BooleanField(default=True)
    requires_number = models.BooleanField(default=False)
    requires_church = models.BooleanField(default=False)
    ledger_group = models.ForeignKey(LedgerGroup, on_delete=models.PROTECT, null=True, blank=True)
    pastorate_only = models.BooleanField(default=False, help_text='If True, this category is only available for pastorate level accounts')
    
    def __str__(self):
        if self.ledger_group:
            return f"{self.ledger_group.name} - {self.name}"
        return self.name
    
    class Meta:
        verbose_name_plural = "Transaction Categories"

class TransactionDetail(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='details')
    category = models.ForeignKey(TransactionCategory, on_delete=models.PROTECT, related_name='transactions')
    reference_number = models.CharField(max_length=50, null=True, blank=True, help_text='Receipt/Bill/Voucher number')
    church = models.ForeignKey('congregation.Church', on_delete=models.PROTECT, null=True, blank=True, related_name='offertory_transactions')
    member = models.ForeignKey('congregation.Member', on_delete=models.PROTECT, null=True, blank=True, related_name='receipt_transactions', help_text='Optional: Select member for receipt reference')
    family = models.ForeignKey('congregation.Family', on_delete=models.PROTECT, null=True, blank=True, related_name='receipt_transactions', help_text='Optional: Select family for receipt reference')
    
    def __str__(self):
        return f"{self.category.name} - {self.transaction.reference_number}"

class DioceseCategory(models.Model):
    """Categories specific to Diocese Account transactions"""
    name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=10, choices=[('debit', 'Debit'), ('credit', 'Credit')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Diocese Category'
        verbose_name_plural = 'Diocese Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class DioceseTransaction(models.Model):
    """Diocese Account transactions"""
    account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='diocese_transactions')
    category = models.ForeignKey(DioceseCategory, on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=10, choices=[('debit', 'Debit'), ('credit', 'Credit')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    transaction_date = models.DateField()
    reference_number = models.CharField(max_length=50, unique=True)
    
    # For contra entries
    is_contra = models.BooleanField(default=False)
    contra_account = models.ForeignKey('Account', on_delete=models.PROTECT, null=True, blank=True, related_name='contra_transactions')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='diocese_transactions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='diocese_transactions_updated', null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.description}"

    @classmethod
    def generate_reference_number(cls):
        """Generate a unique reference number"""
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        # Get the last transaction number for this month
        last_transaction = cls.objects.filter(
            created_at__year=current_year,
            created_at__month=current_month
        ).order_by('-reference_number').first()
        
        # Extract the last index or start from 0
        if last_transaction and last_transaction.reference_number.startswith(f'DIOC-{current_year}{current_month:02d}-'):
            try:
                last_index = int(last_transaction.reference_number.split('-')[-1])
            except ValueError:
                last_index = 0
        else:
            last_index = 0
        
        # Generate new reference number
        return f'DIOC-{current_year}{current_month:02d}-{last_index + 1:04d}'

    def save(self, *args, **kwargs):
        # Generate reference number if not set
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        
        # If this is an existing transaction, get the old instance
        if self.pk:
            old_instance = DioceseTransaction.objects.get(pk=self.pk)
            
            # Reverse old balance changes
            if old_instance.transaction_type == 'credit':
                old_instance.account.balance -= old_instance.amount
            else:
                old_instance.account.balance += old_instance.amount
            old_instance.account.save()
            
            # If it was a contra entry, reverse the contra account balance too
            if old_instance.is_contra and old_instance.contra_account:
                if old_instance.transaction_type == 'credit':
                    old_instance.contra_account.balance += old_instance.amount
                else:
                    old_instance.contra_account.balance -= old_instance.amount
                old_instance.contra_account.save()
        
        # Apply new balance changes
        if self.transaction_type == 'credit':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        self.account.save()
        
        # If this is a contra entry, update the contra account balance too
        if self.is_contra and self.contra_account:
            if self.transaction_type == 'credit':
                self.contra_account.balance -= self.amount  # If diocese is credited, contra account is debited
                # Create transaction record in pastorate account with unique reference
                timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
                Transaction.objects.create(
                    account=self.contra_account,
                    transaction_type='debit',
                    amount=self.amount,
                    description=f"Diocese Contra Entry - {self.description}",
                    transaction_date=self.transaction_date,
                    created_by=self.created_by,
                    reference_number=f"DIOC-CONTRA-{timestamp}"
                )
            else:
                self.contra_account.balance += self.amount  # If diocese is debited, contra account is credited
                # Create transaction record in pastorate account with unique reference
                timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
                Transaction.objects.create(
                    account=self.contra_account,
                    transaction_type='credit',
                    amount=self.amount,
                    description=f"Diocese Contra Entry - {self.description}",
                    transaction_date=self.transaction_date,
                    created_by=self.created_by,
                    reference_number=f"DIOC-CONTRA-{timestamp}"
                )
            self.contra_account.save()
        
        super().save(*args, **kwargs)

# Signal to create Diocese Account when Pastorate is created
@receiver(post_save, sender=Pastorate)
def create_diocese_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(
            name=f"{instance.pastorate_name} Diocese Account",
            account_type=AccountType.objects.get(name='Cash Account'),  # You might want to create a specific type
            pastorate=instance,
            level='pastorate',
            account_number=f"DIO-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            is_active=True
        )

class DioceseContraCategory(models.Model):
    name = models.CharField(max_length=100)
    transaction_type = models.CharField(choices=[('debit', 'Debit'), ('credit', 'Credit')], max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Diocese Contra Category'
        verbose_name_plural = 'Diocese Contra Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
