from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('congregation', '0003_add_timestamps'),
    ]

    operations = [
        migrations.RenameField(
            model_name='church',
            old_name='adobe',
            new_name='abode',
        ),
    ] 