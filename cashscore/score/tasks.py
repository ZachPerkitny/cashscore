import datetime
import decimal
import uuid

from django.core.mail import EmailMessage
from django.db import DatabaseError
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.db import transaction
from django.utils.http import urlsafe_base64_encode

from celery import shared_task
from djstripe import settings as djstripe_settings
from plaid.errors import APIError, RateLimitExceededError
from smtplib import SMTPException
from stripe.error import StripeError

from cashscore.plaid import client as plaid_client

from .models import Account, Application, Item, Transaction


@shared_task(autoretry_for=(DatabaseError, StripeError,), retry_backoff=True, max_retries=None)
@transaction.atomic
def charge_customer_for_application(application_id, idempotency_key):
    application = Application.objects.get(id=application_id)
    customer = application.property.user.stripe_customer
    customer.charge(
        amount=decimal.Decimal('19.99'),
        idempotency_key=idempotency_key)
    application.state = application.State.completed
    application.save()


@shared_task(autoretry_for=(DatabaseError, APIError, RateLimitExceededError,), retry_backoff=True, max_retries=None)
@transaction.atomic
def get_applicant_transactions(application_id, public_token):
    application = Application.objects.get(id=application_id)
    exchange_response = plaid_client.Item.public_token.exchange(public_token)
    access_token = exchange_response['access_token']
    item_dict = plaid_client.Item.get(access_token)['item']
    item = Item.objects.create(
        id=item_dict['item_id'],
        access_token=access_token,
        institution_id=item_dict['institution_id'])
    application.item = item

    start_date = '{:%Y-%m-%d}'.format(datetime.datetime(1900, 1, 1))
    end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

    transactions_response = plaid_client.Transactions.get(access_token, start_date, end_date)
    account_dicts = transactions_response['accounts']
    transaction_dicts = transactions_response['transactions']

    while len(transaction_dicts) < transactions_response['total_transactions']:
        transactions_response = plaid_client.Transactions.get(
            access_token,
            start_date,
            end_date,
            offset=len(transaction_dicts))
        transaction_dicts.extend(transactions_response['transactions']) 

    accounts = {}
    for account_dict in account_dicts:
        accounts[account_dict['account_id']] = Account.objects.create(
            id=account_dict['account_id'],
            mask=account_dict['mask'],
            name=account_dict['name'],
            official_name=account_dict['official_name'],
            type=account_dict['type'],
            subtype=account_dict['subtype'],
            available_balance=account_dict['balances']['available'],
            current_balance=account_dict['balances']['current'],
            balance_iso_currency_code=account_dict['balances']['iso_currency_code'],
            balance_unofficial_currency_code=account_dict['balances']['unofficial_currency_code'],
            item=item)

    for transaction_dict in transaction_dicts:
        if all(value == None for value in transaction_dict['location'].values()):
            location = None
        else:
            location = transaction_dict['location']

        if all(value == None for value in transaction_dict['payment_meta'].values()):
            payment_meta = None
        else:
            payment_meta = transaction_dict['payment_meta']

        Transaction.objects.create(
            id=transaction_dict['transaction_id'],
            account=accounts[transaction_dict['account_id']],
            category_id=transaction_dict['category_id'],
            transaction_type=transaction_dict['transaction_type'],
            name=transaction_dict['name'],
            amount=transaction_dict['amount'],
            iso_currency_code=transaction_dict['iso_currency_code'],
            unofficial_currency_code=transaction_dict['unofficial_currency_code'],
            date=transaction_dict['date'],
            authorized_date=transaction_dict['authorized_date'],
            location=location,
            payment_meta=payment_meta,
            payment_channel=transaction_dict['payment_channel'],
            pending=transaction_dict['pending'],
            pending_transaction_id=transaction_dict['pending_transaction_id'],
            account_owner=transaction_dict['account_owner'])

    application.state = Application.State.payment_pending
    application.save()

    charge_customer_for_application.delay(
        application_id,
        uuid.uuid4())


@shared_task(autoretry_for=(SMTPException,), retry_backoff=True, max_retries=None)
def send_email_to_applicant(application_id, protocol, domain, token):
    application = Application.objects.get(id=application_id)

    mail_subject = 'Lorem Ipsum Dolor'
    message = render_to_string('score/applicant-request-email.html', {
        'application': application,
        'protocol': protocol,
        'domain': domain,
        'token': token,
        'aidb64': urlsafe_base64_encode(force_bytes(application_id)), 
    })
    to_email = application.applicant_email
    email = EmailMessage(
        mail_subject,
        message,
        to=[to_email])
    email.send()
