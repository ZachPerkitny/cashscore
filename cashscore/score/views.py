from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ApplicationForm, PropertyForm
from .models import Property


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
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class AddPropertyView(LoginRequiredMixin, FormView):
    template_name = 'score/add-property.html'
    form_class = PropertyForm
    success_url = reverse_lazy('score:applications')

    def form_valid(self, form):
        property = form.save(commit=False)
        property.user = self.request.user
        property.save()

        return super().form_valid(form)
