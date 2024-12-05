from django.core.management.base import BaseCommand
from django.db.models import Q
from accounts.models import Transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Check contra entries for potential issues'

    def handle(self, *args, **options):
        # Get all contra transactions
        contra_transactions = Transaction.objects.filter(
            Q(transaction_type='contra') | Q(transaction_type='contra_credit')
        ).select_related(
            'account',
            'account__pastorate',
            'account__church',
            'to_account',
            'from_account'
        ).order_by('date', 'created_at')

        self.stdout.write("Checking contra entries...")
        
        # Group transactions by reference number to check pairs
        transaction_pairs = {}
        for trans in contra_transactions:
            if trans.reference_number not in transaction_pairs:
                transaction_pairs[trans.reference_number] = []
            transaction_pairs[trans.reference_number].append(trans)

        issues_found = False
        
        # Check each pair of transactions
        for ref_num, transactions in transaction_pairs.items():
            if len(transactions) != 2:
                issues_found = True
                self.stdout.write(self.style.ERROR(
                    f"Issue: Reference {ref_num} has {len(transactions)} transactions instead of 2"
                ))
                continue

            debit = next((t for t in transactions if t.transaction_type == 'contra'), None)
            credit = next((t for t in transactions if t.transaction_type == 'contra_credit'), None)

            if not debit or not credit:
                issues_found = True
                self.stdout.write(self.style.ERROR(
                    f"Issue: Reference {ref_num} missing debit or credit entry"
                ))
                continue

            # Check amounts match
            if debit.amount != credit.amount:
                issues_found = True
                self.stdout.write(self.style.ERROR(
                    f"Issue: Amount mismatch for reference {ref_num}"
                    f"\nDebit amount: {debit.amount}"
                    f"\nCredit amount: {credit.amount}"
                ))

            # Check account relationships
            if debit.account != credit.from_account:
                issues_found = True
                self.stdout.write(self.style.ERROR(
                    f"Issue: Account mismatch for reference {ref_num}"
                    f"\nDebit account: {debit.account}"
                    f"\nCredit from_account: {credit.from_account}"
                ))

            if debit.to_account != credit.account:
                issues_found = True
                self.stdout.write(self.style.ERROR(
                    f"Issue: Account mismatch for reference {ref_num}"
                    f"\nDebit to_account: {debit.to_account}"
                    f"\nCredit account: {credit.account}"
                ))

            # Check dates match
            if debit.date != credit.date:
                issues_found = True
                self.stdout.write(self.style.ERROR(
                    f"Issue: Date mismatch for reference {ref_num}"
                    f"\nDebit date: {debit.date}"
                    f"\nCredit date: {credit.date}"
                ))

        if not issues_found:
            self.stdout.write(self.style.SUCCESS("No issues found in contra entries"))
        else:
            self.stdout.write(self.style.WARNING("Issues were found in contra entries. Please review the errors above.")) 