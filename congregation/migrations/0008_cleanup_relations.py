from django.db import migrations

def cleanup_and_add_relations(apps, schema_editor):
    Relation = apps.get_model('congregation', 'Relation')
    # First, delete all existing relations
    Relation.objects.all().delete()
    
    # Re-add relations
    relations = ['Family Head', 'Spouse', 'Son', 'Daughter', 'Father', 'Mother']
    for relation in relations:
        Relation.objects.create(name=relation)

def reverse_migration(apps, schema_editor):
    Relation = apps.get_model('congregation', 'Relation')
    Relation.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('congregation', '0007_add_initial_relations'),
    ]

    operations = [
        migrations.RunPython(cleanup_and_add_relations, reverse_migration),
    ] 