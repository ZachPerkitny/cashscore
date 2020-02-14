from djstripe import settings
from stripe.error import InvalidRequestError


def charge_customer(customer, **kwargs):
    try:
        customer.charge(**kwargs)
    except InvalidRequestError as e:
        if settings.STRIPE_LIVE_MODE:
            raise

        if e.code == 'resource_missing' and e.param == 'file' and e.http_status == 404:
            pass
        else:
            raise
