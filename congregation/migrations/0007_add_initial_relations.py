from django.db import migrations

def add_initial_relations(apps, schema_editor):
    Relation = apps.get_model('congregation', 'Relation')
    relations = ['Family Head', 'Spouse', 'Son', 'Daughter', 'Father', 'Mother']
    for relation in relations:
        Relation.objects.create(name=relation)

def remove_relations(apps, schema_editor):
    Relation = apps.get_model('congregation', 'Relation')
    Relation.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('congregation', '0006_add_initial_respect_titles'),
    ]

    operations = [
        migrations.RunPython(add_initial_relations, remove_relations),
    ] 