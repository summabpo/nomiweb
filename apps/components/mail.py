from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_template_email(email_type, context, subject, recipient_list, from_email=None):
    
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER
    email_templates = {
        'welcome': 'mails/bienvenido.html',
        'password_reset': 'mails/resetpassword.html',
        
    }
    
    template_name = email_templates.get(email_type)
    
    if not template_name:
        raise ValueError(f"Tipo de correo no reconocido: {email_type}")
    message = render_to_string('mails/bienvenido.html', context)
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
    )
    email.content_subtype = "html"  
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False
