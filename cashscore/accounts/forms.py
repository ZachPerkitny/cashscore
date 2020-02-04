from django.contrib.auth.forms import UserCreationForm
from django import forms

from djstripe import settings as djstripe_settings

from .models import User
from .widgets import StripeElementWidget


class AddPaymentMethodForm(forms.Form):
    stripe_token = forms.CharField(
        widget=StripeElementWidget(djstripe_settings.STRIPE_PUBLIC_KEY),
        label='Debit or credit card',)
    is_default = forms.BooleanField(label='Set as default', required=False)

    def __init__(self, customer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer = customer

    def clean_is_default(self):
        is_default = self.cleaned_data.get('is_default')
        if self.customer.legacy_cards.count() == 0 and not is_default:
            raise forms.ValidationError('This field is required.')

        return is_default

    def save(self):
        return self.customer.add_card(
            self.cleaned_data['stripe_token'],
            set_default=self.cleaned_data['is_default'])


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',)
