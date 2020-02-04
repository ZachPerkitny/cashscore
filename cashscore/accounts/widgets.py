from django.forms.widgets import Widget


class StripeElementWidget(Widget):
    template_name = 'accounts/stripe-element.html'

    class Media:
        js = (
            'https://js.stripe.com/v3/',
            'js/stripe_element.js',
        )

    def __init__(self, public_key, attrs=None):
        attrs = dict(attrs or {}, public_key=public_key)
        super().__init__(attrs)
