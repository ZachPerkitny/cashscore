from django.db import migrations, models


def encrypt_access_tokens(apps, schema_editor):
    Item = apps.get_model('score', 'Item')

    for item in Item.objects.all():
        item.access_token = item.old_access_token
        item.save(update_fields=['access_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0015_item_access_token'),
    ]

    operations = [
        migrations.RunPython(encrypt_access_tokens),
    ]
