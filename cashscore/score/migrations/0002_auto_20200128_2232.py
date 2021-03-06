# Generated by Django 3.0.2 on 2020-01-28 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='applicant_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application',
            name='item',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='application', to='score.Item'),
        ),
        migrations.AlterField(
            model_name='application',
            name='unit',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
