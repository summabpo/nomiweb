from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa, Role, User
import random
import string

ROLES = (
    ('', '----------'),
    ('admin', 'Administrator'),
    ('employee', 'Employee'),
    ('company', 'Company'),
    ('accountant', 'Accountant'),
)

class UserCreationForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='Su contraseña no puede ser demasiado similar a su otra información personal.')
    password2 = forms.CharField(label='Password confirmacion', widget=forms.PasswordInput, help_text='Ingrese la misma contraseña que antes, para verificación.')
    generate_password = forms.BooleanField(label='Generar contraseña aleatoria', required=False, help_text='Marque para generar una contraseña aleatoria.')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        role = cleaned_data.get('role')
        company = cleaned_data.get('company')

        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "Esta dirección de correo electrónico ya está en uso")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden")

        if role == 'company' and not company:
            self.add_error('company', "Debe seleccionar una compañía para el rol de compañía.")
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        self.fields['email'] = forms.EmailField(label='Email', help_text='Introduzca una dirección de correo electrónico válida')
        self.fields['first_name'] = forms.CharField(label='Primer Nombre', help_text='Introduzca su primer nombre.')
        self.fields['last_name'] = forms.CharField(label='Apellido', help_text='Introduzca su apellido.')
        
        self.fields['is_active'] = forms.BooleanField(
            label='Active',
            required=False,
            initial=True,  # Se marca por defecto
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
        )
        
        self.fields['is_staff'] = forms.BooleanField(
            label='¿Es parte del equipo?', 
            required=False, 
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        )

        self.fields['is_superuser'] = forms.BooleanField(
            label='¿Es un administrador?', 
            required=False, 
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        )
        
        self.fields['role'] = forms.ChoiceField(
            choices=ROLES,
            label='Rol Usuario',
            help_text='Seleccione el rol que se asignará al usuario.'
        )
        
        self.fields['company'] = forms.ChoiceField(
            choices=[('', '----------')] + [(empresa.idempresa, empresa.nombreempresa) for empresa in Empresa.objects.all()],
            label='Compañía Usuario',
            required=False,
            help_text='Seleccione la compañía del usuario.'
        )
        
        self.fields['permission'] = forms.ChoiceField(
            choices=[('', '----------')] + [(role.id, role.name) for role in Role.objects.all()],
            label='Permisos',
            help_text='Seleccione los permisos del usuario.'
        )
        
        # Configurar la apariencia de los campos
        self.fields['role'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-dropdown-parent':'#kt_modal_maintenance',
            'data-hide-search': "true",
        })
        
        self.fields['company'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-dropdown-parent':'#kt_modal_maintenance',
            'data-hide-search': "true",
        })
        
        self.fields['permission'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-dropdown-parent':'#kt_modal_maintenance',
            'data-hide-search': "true",
        })

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_user'
        self.helper.form_action = '/admin/users/create/'
        self.helper.enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='form-group mb-0 col-md-6'),
                Column('company', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('last_name', css_class='form-group mb-0 col-md-6'),
                Column('first_name', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('permission', css_class='form-group mb-0 col-md-6'),
                Column('role', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group mb-0 col-md-6'),
                Column('password2', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('is_staff', css_class='form-group mb-0 col-md-4'),
                Column('is_superuser', css_class='form-group mb-0 col-md-4'),
                Column('is_active', css_class='form-group mb-0 col-md-4'),
                css_class='form-row'
            ),
        )

    def generate_random_password(self):
        """Genera una contraseña aleatoria"""
        length = 12
        characters = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(random.choice(characters) for i in range(length))
        return random_password
