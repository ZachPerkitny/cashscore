from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView, TemplateView, DetailView
from django.shortcuts import render

from .forms import ApplicationForm, ApplicantForm, PropertyForm
from .models import Application, Item, Property, Transaction
from .tasks import send_email_to_applicant, get_applicant_transactions
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
        with transaction.atomic():
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
        with transaction.atomic():
            self.application.state = Application.State.running
            self.application.save()

            public_token = form.cleaned_data.get('public_token')
            get_applicant_transactions.delay(self.application.id, public_token)

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


class ReportDetailView(DetailView, LoginRequiredMixin):
    model = Application
    template_name = 'score/reports.html'
    context_object_name = 'transactions'

    def get_object(self, queryset=None):
        obj = super(ReportDetailView, self).get_object(queryset=queryset)
        obj = Transaction.objects.filter(account__item__application=obj.id)
        return obj

    def get_queryset(self):
        queryset = super(ReportDetailView, self).get_queryset()
        return queryset.filter(property__user=self.request.user)

  
    
