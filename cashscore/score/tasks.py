from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from celery import shared_task

from .models import Application


@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=None)
def send_email_to_applicant(application_id, protocol, domain, token):
    application = Application.objects.get(id=application_id)

    mail_subject = 'Lorem Ipsum Dolor'
    message = render_to_string('score/applicant-request.html', {
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
