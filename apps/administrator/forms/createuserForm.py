from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class UserCreationForm(forms.ModelForm):
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
    
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active']
        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'is_staff': 'Staff status',
            'is_superuser': 'Superuser status',
            'is_active': 'Active',
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ únicamente.',
            'email': 'Introduzca una dirección de correo electrónico válida',
        }
        widgets = {
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                Column('password1', css_class='form-group mb-0 col-md-6'),
                Column('password2', css_class='form-group mb-0 col-md-6'),
                css_class='form-row'
            ),
            
            'is_staff',
            'is_superuser',
            'is_active',
            
            Submit('submit', 'Crear usuario')
        )
