from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

"""
Funciones para Enviar Correos Electrónicos con Plantillas

Estas funciones están diseñadas para enviar correos electrónicos utilizando plantillas HTML, con soporte para enviar correos con o sin archivos adjuntos. Las plantillas están predefinidas y se eligen en función del tipo de correo.

1. `send_template_email(email_type, context, subject, recipient_list, from_email=None)`
    Envía un correo electrónico utilizando una plantilla HTML basada en el tipo de correo especificado.

    Parámetros
    ----------
    email_type : str
        Tipo de correo a enviar. Las opciones disponibles incluyen 'welcome', 'password_reset', 'loginweb', 'vacations', 'vacation_request', 'nomina1', 'token'.
    context : dict
        Diccionario de contexto que se utilizará en la plantilla para generar el contenido dinámico.
    subject : str
        Asunto del correo electrónico.
    recipient_list : list
        Lista de direcciones de correo electrónico de los destinatarios.
    from_email : str, opcional
        Dirección de correo electrónico del remitente. Si no se proporciona, se utiliza la dirección configurada en `settings.EMAIL_HOST_USER`.

    Retorna
    -------
    bool
        `True` si el correo se envió correctamente, `False` si ocurrió un error.

    Descripción
    -----------
    Esta función envía un correo electrónico utilizando una plantilla HTML correspondiente al tipo de correo especificado. Si el tipo de correo no es reconocido, lanza una excepción.
    
    Ejemplo
    -------
    send_template_email('welcome', {'nombre': 'Juan'}, 'Bienvenido', ['juan@ejemplo.com'])
    

2. `send_template_email2(email_type, context, subject, recipient_list, from_email=None)`
    Similar a `send_template_email`, pero con manejo de excepciones mejorado para retornar tanto un valor booleano como un mensaje de estado.

    Parámetros
    ----------
    email_type : str
        Tipo de correo a enviar.
    context : dict
        Diccionario de contexto.
    subject : str
        Asunto del correo.
    recipient_list : list
        Lista de destinatarios.
    from_email : str, opcional
        Dirección del remitente.

    Retorna
    -------
    tuple
        Retorna una tupla con dos valores:
            - `True` o `False` dependiendo del éxito del envío.
            - Un mensaje de estado o el error ocurrido.

    Descripción
    -----------
    Esta función tiene la misma funcionalidad que `send_template_email`, pero en lugar de lanzar una excepción, devuelve un valor booleano junto con un mensaje que indica si el correo fue enviado correctamente o si ocurrió un error.

    Ejemplo
    -------
    send_template_email2('password_reset', {'usuario': 'juan'}, 'Restablecer contraseña', ['juan@ejemplo.com'])


3. `send_template_email3(email_type, context, subject, recipient_list, from_email=None, attachment=None)`
    Envía un correo electrónico con una plantilla HTML y opción de adjuntar un archivo.

    Parámetros
    ----------
    email_type : str
        Tipo de correo a enviar.
    context : dict
        Diccionario de contexto.
    subject : str
        Asunto del correo.
    recipient_list : list
        Lista de destinatarios.
    from_email : str, opcional
        Dirección del remitente.
    attachment : dict, opcional
        Diccionario con la información del archivo adjunto. Debe contener las claves 'filename', 'content', y 'mimetype'.

    Retorna
    -------
    tuple
        Retorna una tupla con dos valores:
            - `True` o `False` dependiendo del éxito del envío.
            - Un mensaje de estado o el error ocurrido.

    Descripción
    -----------
    Esta función envía un correo electrónico utilizando una plantilla HTML. Además, permite adjuntar un archivo si se proporciona un diccionario `attachment`. El archivo adjunto puede ser cualquier tipo de archivo, como PDF o imágenes.
    
    Ejemplo
    -------
    send_template_email3('vacations', {'nombre': 'Juan'}, 'Vacaciones pendientes', ['juan@ejemplo.com'], attachment={'filename': 'vacaciones.pdf', 'content': file_content, 'mimetype': 'application/pdf'})
"""


def send_template_email(email_type, context, subject, recipient_list, from_email=None):
    
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER
        
    email_templates = {
        'welcome': 'mails/bienvenido.html',
        'password_reset': 'mails/resetpassword.html',
        'loginweb': 'mails/cuentausuario.html',
        'vacations': 'mails/vacations.html',
        'vacation_request': 'mails/vacation_request.html',
        'nomina1':'mails/correo_de_nomina.html',
        'token': 'mails/tokensend.html',
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
        'vacation_request': 'mails/vacation_request.html',
        'nomina1':'mails/correo_de_nomina.html',
        'token': 'mails/tokensend.html',
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
        'vacation_request': 'mails/vacation_request.html',
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
        return True , '0k'
    except Exception as e:
        return False , e
