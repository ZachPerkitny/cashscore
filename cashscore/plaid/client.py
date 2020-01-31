from django.conf import settings

import plaid


ENV = settings.PLAID_ENV
CLIENT_ID = settings.PLAID_CLIENT_ID
SECRET = settings.PLAID_SECRET
PUBLIC_KEY = settings.PLAID_PUBLIC_KEY


client = plaid.Client(
    environment=ENV,
    client_id=CLIENT_ID,
    secret=SECRET,
    public_key=PUBLIC_KEY,
    api_version='2018-05-22')
