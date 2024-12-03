from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('congregation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fellowship',
            name='church',
        ),
        migrations.AddField(
            model_name='fellowship',
            name='address',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fellowship',
            name='area',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='congregation.area'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='area',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='area',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='fellowship',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='fellowship',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterModelOptions(
            name='area',
            options={'ordering': ['area_id'], 'verbose_name_plural': 'Areas'},
        ),
        migrations.AlterModelOptions(
            name='fellowship',
            options={'ordering': ['fellowship_id'], 'verbose_name_plural': 'Fellowships'},
        ),
    ] 