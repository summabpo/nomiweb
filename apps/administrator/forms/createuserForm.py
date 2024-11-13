from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa , Role , User


ROLES = (
        ('admin', 'Administrator'),
        ('employee', 'Employee'),
        ('company', 'Company'),
        ('accountant', 'Accountant'),
    )

class UserCreationForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='Su contraseña no puede ser demasiado similar a su otra información personal.')
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, help_text='Ingrese la misma contraseña que antes, para verificación.')

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
            self.add_error('company',"Debe seleccionar una compañía para el rol de compañía.")
            
        
        return cleaned_data
    
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(label='Email', help_text='Introduzca una dirección de correo electrónico válida')
        self.fields['first_name'] = forms.CharField(label='First Name')
        self.fields['last_name'] = forms.CharField(label='Last Name')
        self.fields['is_staff'] = forms.BooleanField(label='Staff status', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
        self.fields['is_superuser'] = forms.BooleanField(label='Superuser status', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
        self.fields['is_active'] = forms.BooleanField(label='Active', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
        #self.fields['permission'] = forms.CharField(label='Permisos')
        
        self.fields['role'] = forms.ChoiceField(
            choices= ROLES,
            label='Rol Usuario'
        )
        
        self.fields['company'] = forms.ChoiceField(
            choices=[('', '----------')] + [(empresa.idempresa, empresa.nombreempresa) for empresa in Empresa.objects.all()],
            label='Campañia Usuario',
            required=False,
        )
        
        self.fields['permission'] = forms.ChoiceField(
            choices=[('', '----------')] + [(role.id, role.name) for role in Role.objects.all()],
            label='Permisos',
        )
        # Configurar la apariencia del campo nivelcargo
        self.fields['role'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': "true",
        })
        
        
        # Configurar la apariencia del campo nivelcargo
        self.fields['company'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': "true",
        })
        
        # Configurar la apariencia del campo nivelcargo
        self.fields['permission'].widget.attrs.update({
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': "true",
        })
        #Empresa
        #choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.all()],

        self.helper = FormHelper()
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
            
            
            'is_staff',
            'is_superuser',
            'is_active',
            
            Submit('submit', 'Crear usuario')
        )
