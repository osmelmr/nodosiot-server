from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_list):
    """
    Envía un correo electrónico a la lista de destinatarios.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
