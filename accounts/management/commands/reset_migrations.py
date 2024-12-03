from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Reset migration history for accounts app'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM django_migrations WHERE app = 'accounts'"
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully reset migration history for accounts app')
            ) 