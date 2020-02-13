# Generated by Django 3.0.2 on 2020-02-13 20:18

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaskMeta',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('result', models.TextField(editable=False, null=True)),
                ('status', models.CharField(choices=[('FAILURE', 'FAILURE'), ('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('RETRY', 'RETRY'), ('REVOKED', 'REVOKED'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS')], max_length=50)),
                ('name', models.CharField(max_length=255, null=True)),
                ('args', django.contrib.postgres.fields.jsonb.JSONField()),
                ('kwargs', django.contrib.postgres.fields.jsonb.JSONField()),
                ('worker', models.CharField(max_length=100, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('completed', models.DateTimeField(null=True)),
                ('traceback', models.TextField(null=True)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(editable=False, null=True)),
                ('locked_at', models.DateTimeField(null=True)),
            ],
        ),
    ]
