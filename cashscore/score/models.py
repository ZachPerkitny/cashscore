from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_cryptography.fields import encrypt

from cashscore.plaid import client as plaid_client
from cashscore.plaid.categories import CATEGORIES_DICT


class Property(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties')
    address = models.CharField(max_length=128)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name_plural = 'properties'


class Application(models.Model):
    user_property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='applications')
    unit = models.CharField(max_length=128, null=True, blank=True)
    rent_asked = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()

    sent_email_to_applicant = models.BooleanField(default=False)
    applicant_connected_to_plaid = models.BooleanField(default=False)
    pulled_plaid_data = models.BooleanField(default=False)
    charged_client = models.BooleanField(default=False)
    sent_email_to_client = models.BooleanField(default=False)

    @property
    def is_completed(self):
        return self.sent_email_to_applicant and\
            self.applicant_connected_to_plaid and\
            self.pulled_plaid_data and\
            self.charged_client and\
            self.sent_email_to_applicant


class Item(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    access_token = encrypt(models.CharField(max_length=128))
    institution_id = models.CharField(max_length=10)
    last_pull = models.DateField(auto_now_add=True)
    application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        related_name='items',
        null=True)

    @property
    def institution(self):
        return plaid_client.Institutions.get_by_id(self.institution_id)['institution']

    @property
    def institution_name(self):
        return self.institution['name']


class Account(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    mask = models.CharField(max_length=4, null=True)
    name = models.CharField(max_length=255)
    official_name = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=128)
    subtype = models.CharField(max_length=128)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    balance_iso_currency_code = models.CharField(max_length=3, null=True)
    balance_unofficial_currency_code = models.CharField(max_length=3, null=True)
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
    authorized_date = models.DateField(null=True)
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

    @property
    def category(self):
        return CATEGORIES_DICT[self.category_id]

    @property
    def category_name(self):
        return self.category['hierarchy'][:-1]
