from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('congregation', '0002_area_fellowship'),
    ]

    operations = [
        migrations.AddField(
            model_name='church',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='church',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='pastorate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='pastorate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ] 