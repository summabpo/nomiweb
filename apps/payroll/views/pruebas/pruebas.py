from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from apps.common.models import Contratos
from django.shortcuts import get_object_or_404

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Field ,Row , Column 
from apps.common.models import User
from django.urls import reverse

from django.contrib import messages
from django.http import HttpResponse

from django.core.exceptions import ValidationError

        
class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo electrónico:',
        widget=forms.EmailInput(attrs={'placeholder': 'Ingrese su correo electrónico'})
    )
    password = forms.CharField(
        label='Contraseña:',
        max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email =  cleaned_data.get('email','0')
        if email.endswith('@hotmail.com'):
            self.add_error('email', 'No se permite usar correos de Hotmail.')
        
        cleaned_data["email"] = email
        return cleaned_data
    

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_login'
        self.helper.enctype = 'multipart/form-data'

        # Atributos específicos para Unpoly
        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',
            'up-submit': reverse('payroll:prueba_modal'),
            'up-accept-location': reverse('payroll:prueba'),
            'up-on-accepted': 'up.modal.close()',
        })

        self.helper.layout = Layout(
            Row(
                Column('email', css_class='form-group mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('password', css_class='form-group mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Ingresar', css_class='btn btn-light-success w-100')
        )
        
        
        
        

# Vista principal con el botón para abrir el modal
def prueba(request):
    return render(request, './payroll/prueba.html')


def prueba_modal(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            
            contract = form.cleaned_data['email']
            origin = form.cleaned_data['password']
            
            messages.success(request, "Proceso de Transporte realizado correctamente")
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  # Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-Location'] = reverse('payroll:prueba')  # URL para recargar la página principal
            return response
            
    return render(request, './payroll/partials/prueba.html',{'form' :form})