from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Item(models.Model):
    creds = JSONField()
    last_pull = models.DateField()


class Account(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    mask = models.CharField(max_length=4, null=True)
    name = models.CharField(max_length=255)
    official_name = models.CharField(max_length=255)
    type = models.CharField(max_length=128)
    subtype = models.CharField(max_length=128)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    balance_iso_currency_code = models.CharField(max_length=3)
    balance_unofficial_currency_code = models.CharField(max_length=3)
    institution_id = models.CharField(max_length=10)
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='accounts')


class Transaction(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='transactions')
    category_id = models.CharField(max_length=255, null=True)
    transaction_type = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    iso_currency_code = models.CharField(max_length=3, null=True)
    unofficial_currency_code = models.CharField(max_length=3, null=True)
    date = models.DateField()
    authorized_date = models.DateField()
    location = JSONField(null=True)
    payment_meta = JSONField(null=True)
    payment_channel = models.CharField(max_length=8)
    pending = models.BooleanField()
    pending_transaction_id = models.CharField(max_length=128, null=True)
    account_owner = models.CharField(max_length=255, null=True)
    transfer = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True)


class Property(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties')
    address = models.TextField()

    def __str__(self):
        return self.address


class Application(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='applications')
    unit = models.CharField(max_length=128, null=True, blank=True)
    rent_asked = models.DecimalField(max_digits=10, decimal_places=2)
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    item = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        related_name='application',
        null=True)

    class State(models.TextChoices):
        waiting_for_applicant = 'waiting_for_applicant', _('waiting for applicant')
        running = 'running', _('running')
        waiting_for_payment = 'waiting_for_payment', _('waiting for payment')
        completed = 'completed', _('completed')

    state = models.CharField(
        max_length=21,
        choices=State.choices,
        default=State.waiting_for_applicant)
