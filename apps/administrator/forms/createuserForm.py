from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa


ROLES = (
        ('administrator', 'Administrator'),
        ('employee', 'Employee'),
        ('accountant', 'Accountant'),
        ('entrepreneur', 'Entrepreneur'),
    )

class UserCreationForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='Su contraseña no puede ser demasiado similar a su otra información personal.')
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, help_text='Ingrese la misma contraseña que antes, para verificación.')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if User.objects.filter(username=username).exists():
            self.add_error('username', "Este nombre de usuario ya está en uso")

        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "Esta dirección de correo electrónico ya está en uso")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden")
        return cleaned_data
    
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'] = forms.CharField(label='Username', max_length=150, help_text='Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ únicamente.')
        self.fields['first_name'] = forms.CharField(label='First Name')
        self.fields['last_name'] = forms.CharField(label='Last Name')
        self.fields['email'] = forms.EmailField(label='Email', help_text='Introduzca una dirección de correo electrónico válida')
        self.fields['is_staff'] = forms.BooleanField(label='Staff status', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
        self.fields['is_superuser'] = forms.BooleanField(label='Superuser status', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
        self.fields['is_active'] = forms.BooleanField(label='Active', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
        self.fields['permission'] = forms.CharField(label='Permisos')
        
        self.fields['role'] = forms.ChoiceField(
            choices= ROLES,
            label='Rol Usuario'
        )
        
        self.fields['company'] = forms.ChoiceField(
            choices=[('', '----------')] + [(empresa.id, empresa.name) for empresa in Empresa.objects.all()],
            label='Campañia Usuario'
        )
        
        #Empresa
        #choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.all()],

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group mb-0 col-md-6'),
                Column('first_name', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('last_name', css_class='form-group mb-0 col-md-6'),
                Column('email', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('permission', css_class='form-group mb-0 col-md-6'),
                Column('role', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('company', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('password1', css_class='form-group mb-0 col-md-6'),
                Column('password2', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            
            
            'is_staff',
            'is_superuser',
            'is_active',
            
            Submit('submit', 'Crear usuario')
        )
