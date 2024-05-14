from django.shortcuts import render,redirect
from apps.administrator.forms.createuserForm import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from apps.components.mail import send_template_email


# Create your views here.

def index_admin(request):
    # email_type = 'welcome' 
    # name = 'nada'  
    # context = {'name': name}  
    # subject = 'Asunto del correo'  
    # recipient_list = ['mikepruebas@yopmail.com']
    
    # if send_template_email(email_type, context, subject, recipient_list):
    #     print('Correo enviado correctamente')
    # else:
    #     print('Error al enviar el correo')
    
    return render(request, './admin/index.html')
    
    