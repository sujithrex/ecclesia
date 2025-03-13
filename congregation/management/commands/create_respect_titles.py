from django.core.management.base import BaseCommand
from congregation.models import Respect

class Command(BaseCommand):
    help = 'Creates default respect titles'

    def handle(self, *args, **kwargs):
        # Define unique respect titles
        respect_titles = [
            # Common Professional Titles
            'Dr.',
            'Prof.',
            'Er.',
            'Adv.',
            'Col.',
            'Capt.',
            
            # Religious Titles
            'Rev.',
            'Rev. Dr.',
            'Rt. Rev.',
            'Most Rev.',
            'Bishop',
            'Archbishop',
            'Pastor',
            'Deacon',
            
            # Male Titles
            'Mr.',
            'Bro.',
            'Thiru.',
            
            # Female Titles
            'Mrs.',
            'Miss',
            'Ms.',
            'Sis.',
            'Thirumathi.',
            'Selvi.'
        ]
        
        # Create respect titles
        for title in respect_titles:
            respect, created = Respect.objects.get_or_create(
                name=title
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created respect title: {title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Respect title already exists: {title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created all respect titles!')
        )