from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import FormView

from stripe.error import CardError, InvalidRequestError

from .forms import AddPaymentMethodForm, SignUpForm
from .models import User
from .tokens import account_activation_token


class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('web:home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        mail_subject = 'Activate your CashScore account'
        message = render_to_string('accounts/activate-account.html', {
            'user': user,
            'domain': get_current_site(self.request).domain,
            'protocol': 'https' if self.request.is_secure() else 'http',
            'uid': urlsafe_base64_encode(force_bytes(user.id)),
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            mail_subject,
            message,
            to=[to_email])
        email.send()

        messages.success(self.request, 'Please confirm your email address to complete the registration.')

        return super().form_valid(form)


class ActivationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            messages.success(request, 'Your email has been confirmed. You can now login.')

            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        else:
            messages.error(request, 'Activation link is invalid.')
            return HttpResponseRedirect(reverse_lazy('web:home'))


class PaymentMethodsView(LoginRequiredMixin, FormView):
    template_name = 'accounts/payment-methods.html'
    form_class = AddPaymentMethodForm
    success_url = reverse_lazy('accounts:edit_account')

    def form_valid(self, form):
        try:
            form.save()
            messages.success(self.request, 'Succesfully added a new payment method.')
            return super().form_valid(form)
        except (CardError, InvalidRequestError) as e:
            messages.error(self.request, 'Error adding new card.')

        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['customer'] = self.request.user.stripe_customer
        return kwargs
