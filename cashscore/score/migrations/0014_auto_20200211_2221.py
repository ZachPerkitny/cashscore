# Generated by Django 3.0.2 on 2020-02-11 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0013_application_sent_email_to_client'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='access_token',
            new_name='old_access_token',
        ),
    ]
