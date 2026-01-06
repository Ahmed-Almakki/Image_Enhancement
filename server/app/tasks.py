from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def SendEmail(subject, email, message):
    sendemail = EmailMessage(
            subject=subject,
            body=message,
            to=[f'{email}']
    )
    sendemail.send(fail_silently=True)
    return 'Done'