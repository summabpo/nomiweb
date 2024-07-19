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
        'loginweb': 'mails/cuentausuario.html',
        'vacations': 'mails/vacations.html',
        
    }
    
    template_name = email_templates.get(email_type)
    
    if not template_name:
        raise ValueError(f"Tipo de correo no reconocido: {email_type}")
    
    
    message = render_to_string(template_name, context)
    
    
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



def send_template_email2(email_type, context, subject, recipient_list, from_email=None):
    
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER
        
    email_templates = {
        'welcome': 'mails/bienvenido.html',
        'password_reset': 'mails/resetpassword.html',
        'loginweb': 'mails/cuentausuario.html',
        'vacations': 'mails/vacations.html',
        
    }
    
    template_name = email_templates.get(email_type)
    
    if not template_name:
        raise ValueError(f"Tipo de correo no reconocido: {email_type}")
    
    
    message = render_to_string(template_name, context)
    
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
    )
    email.content_subtype = "html"  
    try:
        email.send()
        return True , '0k'
    except Exception as e:
        return False , e


def send_template_email3(email_type, context, subject, recipient_list, from_email=None, attachment=None):
    
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER
        
    email_templates = {
        'welcome': 'mails/bienvenido.html',
        'password_reset': 'mails/resetpassword.html',
        'loginweb': 'mails/cuentausuario.html',
        'vacations': 'mails/vacations.html',
        'nomina1':'mails/correo_de_nomina.html'
    }
    
    template_name = email_templates.get(email_type)
    
    if not template_name:
        raise ValueError(f"Tipo de correo no reconocido: {email_type}")
    
    message = render_to_string(template_name, context)
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
    )
    email.content_subtype = "html"  

    # Adjuntar archivo si se proporciona
    if attachment:
        email.attach(attachment['filename'], attachment['content'], attachment['mimetype'])
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False
