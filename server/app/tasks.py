from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def SendEmail(otp, email):
    sendemail = EmailMessage(
            subject='Your Password Rest Code',
            body=f'''
                    Your verification code is: {otp}
                ''',
            to=[f'{email}']
    )
    sendemail.send(fail_silently=True)
    return 'Done'