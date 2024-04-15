from django import forms

class EmployeeForm(forms.Form):
    #* Datos de Identificación
    identificationType = forms.CharField(label='Tipo de documento de identidad', max_length=100, required=True)
    identificationNumber = forms.CharField(label='Documento de Identidad', max_length=100, required=True)
    expeditionDate = forms.DateField(label='Fecha de expedición', required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    expeditionCity = forms.CharField(label='Ciudad de expedición', max_length=100, required=True)
    firstName = forms.CharField(label='Primer Nombre', max_length=100, required=True)
    secondName = forms.CharField(label='Segundo Nombre', max_length=100, required=False)
    firstLastName = forms.CharField(label='Primer Apellido', max_length=100, required=True)
    secondLastName = forms.CharField(label='Segundo Apellido', max_length=100, required=False)
    
    #* Datos Personales
    genderChoices = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    sex = forms.ChoiceField(label='Sexo', choices=genderChoices, required=True)
    height = forms.FloatField(label='Estatura (Mts)', required=False)
    maritalStatus = forms.CharField(label='Estado Civil', max_length=100, required=True)
    weight = forms.FloatField(label='Peso (Kg)', required=False)
    birthDate = forms.DateField(label='Fecha de Nacimiento', required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    educationLevel = forms.CharField(label='Nivel Educativo', max_length=100, required=False)
    birthCity = forms.CharField(label='Ciudad de Nacimiento', max_length=100, required=True)
    stratum = forms.IntegerField(label='Estrato', required=False)
    birthCountry = forms.CharField(label='País de nacimiento', max_length=100, required=True)
    militaryId = forms.CharField(label='Libreta Militar', max_length=100, required=False)
    bloodGroup = forms.CharField(label='Grupo Sanguíneo', max_length=100, required=False)
    profession = forms.CharField(label='Profesión', max_length=100, required=False)

    #* Datos de Residencia
    residenceAddress = forms.CharField(label='Dirección de Residencia', max_length=200, required=True)
    email = forms.EmailField(label='E-mail', required=True)
    residenceCity = forms.CharField(label='Ciudad de Residencia', max_length=100, required=True)
    phone = forms.CharField(label='Teléfono del Empleado', max_length=20, required=False)
    mobile = forms.CharField(label='Celular', max_length=20, required=True)
    residenceCountry = forms.CharField(label='País de residencia', max_length=100, required=True)
