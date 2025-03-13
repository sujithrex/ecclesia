from django.core.management.base import BaseCommand
from congregation.models import Relation

class Command(BaseCommand):
    help = 'Creates default family relations'

    def handle(self, *args, **kwargs):
        # Define family relations
        relations = [
            # Primary Relations
            'Family Head',
            'Husband',
            'Wife',
            
            # Children
            'Son',
            'Daughter',
            'Son-in-law',
            'Daughter-in-law',
            'Step Son',
            'Step Daughter',
            
            # Parents
            'Father',
            'Mother',
            'Step Father',
            'Step Mother',
            'Father-in-law',
            'Mother-in-law',
            
            # Siblings
            'Brother',
            'Sister',
            'Step Brother',
            'Step Sister',
            'Brother-in-law',
            'Sister-in-law',
            
            # Grandparents/Grandchildren
            'Grandfather',
            'Grandmother',
            'Grandson',
            'Granddaughter',
            
            # Extended Family
            'Uncle',
            'Aunt',
            'Nephew',
            'Niece',
            'Cousin',
            
            # Other Relations
            'Guardian',
            'Ward',
            'Dependent'
        ]
        
        # Create relations
        for relation in relations:
            rel, created = Relation.objects.get_or_create(
                name=relation
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created relation: {relation}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Relation already exists: {relation}')
                )
        
        total_count = Relation.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created all relations! Total relations: {total_count}')
        )