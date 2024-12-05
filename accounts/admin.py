from django.contrib import admin
from .models import AccountType, Account, Transaction

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'account_number', 'balance', 'level', 'is_active')
    list_filter = ('account_type', 'level', 'is_active')
    search_fields = ('name', 'account_number')
    readonly_fields = ('balance', 'created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'account', 'transaction_type', 'amount', 'date')
    list_filter = ('transaction_type', 'date')
    search_fields = ('reference_number', 'description')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
