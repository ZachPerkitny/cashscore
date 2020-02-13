import uuid

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView, TemplateView

from celery import chain

from .forms import ApplicationForm, ApplicantForm, PropertyForm
from .models import Application, Item, Property
from .tasks import send_email_to_applicant, get_applicant_transactions, charge_client_for_application, send_email_to_client
from .tokens import application_token


class ApplicationsView(LoginRequiredMixin, TemplateView):
    template_name = 'score/applications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = self.request.user.properties.all()
        return context


class AddApplicantView(LoginRequiredMixin, FormView):
    template_name = 'score/add-applicant.html'
    form_class = ApplicationForm
    success_url = reverse_lazy('score:applications')

    def form_valid(self, form):
        application = form.save()

        protocol = 'https' if self.request.is_secure() else 'http'
        domain = get_current_site(self.request).domain
        token = application_token.make_token(application)
        send_email_to_applicant.delay(
            application.id,
            protocol,
            domain,
            token)

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


INTERNAL_APPLICANT_ENTRY_SESSION_TOKEN = '_applicant_entry_token'


class ApplicantView(FormView):
    url_token = 'start-application'
    template_name = 'score/applicant.html'
    form_class = ApplicantForm
    success_url = reverse_lazy('web:home')

    def dispatch(self, *args, **kwargs):
        try:
            application_id = urlsafe_base64_decode(kwargs['aidb64']).decode()
            self.application = Application.objects.get(id=application_id)
        except (TypeError, ValueError, OverflowError, Application.DoesNotExist, Application):
            self.application = None

        if self.application is not None:
            token = kwargs['token']
            if token == self.url_token:
                session_token = self.request.session.get(
                    INTERNAL_APPLICANT_ENTRY_SESSION_TOKEN)
                if application_token.check_token(self.application, session_token):
                    return super().dispatch(*args, **kwargs)
            else:
                if application_token.check_token(self.application, token):
                    # It's important to redirect here to avoid the token being
                    # leaked in the HTTP Referer header.
                    self.request.session[INTERNAL_APPLICANT_ENTRY_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.url_token)
                    return HttpResponseRedirect(redirect_url)

        return HttpResponseRedirect(reverse_lazy('web:home'))

    def form_valid(self, form):
        self.application.applicant_connected_to_plaid = True
        self.application.save()

        chain(
            # Get Applicant Transactions
            get_applicant_transactions.si(
                self.application.id,
                form.cleaned_data.get('tokens'),),
            # Charge only once all transactions have been pulled
            charge_client_for_application.si(
                self.application.id,
                uuid.uuid4()),
            # Notify client only once the charge has been made
            send_email_to_client.si(
                self.application.id,
                'https' if self.request.is_secure() else 'http',
                get_current_site(self.request).domain),
        )()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        context['PLAID_ENV'] = settings.PLAID_ENV
        context['PLAID_PUBLIC_KEY'] = settings.PLAID_PUBLIC_KEY
        return context


class AddPropertyView(LoginRequiredMixin, FormView):
    template_name = 'score/add-property.html'
    form_class = PropertyForm
    success_url = reverse_lazy('score:applications')

    def form_valid(self, form):
        property = form.save(commit=False)
        property.user = self.request.user
        property.save()

        return super().form_valid(form)
