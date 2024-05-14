from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_template_email(email_type, context, subject, recipient_list, from_email=None):
    
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER

    
    email_templates = {
        'welcome': 'mails/bienvenido.html',
        'password_reset': 'mails/resetpassword.html',
        
    }
    print('1')
    
    template_name = email_templates.get(email_type)
    print('2')
    
    if not template_name:
        raise ValueError(f"Tipo de correo no reconocido: {email_type}")

    
    message = render_to_string(template_name, context)
    print('3')
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
    )
    print('4')
    email.content_subtype = "html"  
    
    try:
        print('6')
        email.send()
        print('5')
        return True
    except Exception as e:
        
        print(f"Error al enviar el correo: {e}")
        return False
