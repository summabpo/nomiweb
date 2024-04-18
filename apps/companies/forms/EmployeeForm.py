from django import forms
from apps.companies.models import Tipodocumento , Paises


class EmployeeForm(forms.Form):
    identificationType = forms.ModelChoiceField(
        label='Tipo de documento de identidad',
        queryset=Tipodocumento.objects.using("lectaen").all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    identificationNumber = forms.CharField(
        label='Documento de Identidad',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    expeditionDate = forms.DateField(
        label='Fecha de expedición',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    expeditionCity = forms.CharField(
        label='Ciudad de expedición',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    firstName = forms.CharField(
        label='Primer Nombre',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    secondName = forms.CharField(
        label='Segundo Nombre',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    firstLastName = forms.CharField(
        label='Primer Apellido',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    secondLastName = forms.CharField(
        label='Segundo Apellido',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sex = forms.ChoiceField(
        label='Sexo',
        choices=(
            ('M', 'Masculino'),
            ('F', 'Femenino'),
        ),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    height = forms.FloatField(
        label='Estatura (Mts)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    maritalStatus = forms.ChoiceField(
        label='Estado Civil',
        choices=(
            ('', 'Seleccione --------------'),
            ('soltero', 'Soltero'),
            ('casado', 'Casado'),
            ('viudo', 'Viudo'),
            ('divorciado', 'Divorciado'),
            ('union_libre', 'Union Libre'),
        ),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    weight = forms.FloatField(
        label='Peso (Kg)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birthDate = forms.DateField(
        label='Fecha de Nacimiento',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    educationLevel = forms.CharField(
        label='Nivel Educativo',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birthCity = forms.CharField(
        label='Ciudad de Nacimiento',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    stratum = forms.IntegerField(
        label='Estrato',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birthCountry = forms.CharField(
        label='País de nacimiento',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    militaryId = forms.CharField(
        label='Libreta Militar',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bloodGroup = forms.CharField(
        label='Grupo Sanguíneo',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profession = forms.CharField(
        label='Profesión',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    residenceAddress = forms.CharField(
        label='Dirección de Residencia',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    residenceCity = forms.CharField(
        label='Ciudad de Residencia',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='Teléfono del Empleado',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mobile = forms.CharField(
        label='Celular',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    residenceCountry = forms.CharField(
        label='País de residencia',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
