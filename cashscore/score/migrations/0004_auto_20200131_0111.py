# Generated by Django 3.0.2 on 2020-01-31 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0003_auto_20200131_0027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='institution_id',
        ),
        migrations.AddField(
            model_name='item',
            name='institution_id',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='id',
            field=models.CharField(max_length=128, primary_key=True, serialize=False),
        ),
    ]
