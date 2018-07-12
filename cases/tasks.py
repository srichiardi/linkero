from celery import task
from django.core.mail import send_mail



@task()
def send_report():
    send_mail('first email from Linkero', 'this is the first email that linkero sends, aren\' you proud?', 'postero@linkero.ie', ['s.richiardi@gmail.com'], fail_silently=False)
    