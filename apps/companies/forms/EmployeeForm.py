import re
# Django
from django import forms
from apps.companies.models import Tipodocumento ,Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Profesiones,Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit,HTML


class EmployeeForm(forms.Form):
    identification_type = forms.ChoiceField(choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.using("lectaen").all()], label='Tipo de documento de identidad ')
    identification_number = forms.IntegerField(label='Documento de Identidad ')
    expedition_date = forms.DateField(label='Fecha de expedición ',widget=forms.DateInput(attrs={'type': 'date'}))
    expedition_city = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.using("lectaen").all().order_by('ciudad')], label='Ciudad de expedición ' , widget=forms.Select(attrs={'data-control': 'select2'}) )
    first_name = forms.CharField(label='Primer Nombre ')
    second_name = forms.CharField(label='Segundo Nombre', required=False)
    first_last_name = forms.CharField(label='Primer Apellido ')
    second_last_name = forms.CharField(label='Segundo Apellido', required=False)
    sex = forms.ChoiceField(choices=[('', '----------'), ('masculino', 'Masculino'), ('femenino', 'Femenino')], label='Sexo ')
    height = forms.CharField(label='Estatura (Mts)', required=False)
    marital_status = forms.ChoiceField(choices=[('', '----------'), ('soltero', 'Soltero'), ('casado', 'Casado'), ('viudo', 'Viudo'), ('divorciado', 'Divorciado'), ('unionlibre', 'Unión Libre')], label='Estado Civil ')
    weight = forms.CharField(label='Peso (Kg)', required=False)
    birthdate = forms.DateField(label='Fecha de Nacimiento ',widget=forms.DateInput(attrs={'type': 'date'}))
    education_level = forms.ChoiceField(choices=[('', '----------'), ('primaria', 'Primaria'), ('Bachiller', 'Bachiller'), ('bachillerinc', 'Bachiller Incompleto'), ('tecnico', 'Técnico'), ('tecnologo', 'Tecnólogo'), ('universitario', 'Universitario'), ('universitarioinc', 'Universitario Incompleto'), ('postgrado', 'Postgrado'), ('magister', 'Magíster')], label='Nivel Educativo', required=False)
    birth_city = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.using("lectaen").all().order_by('ciudad')], label='Ciudad de Nacimiento',widget=forms.Select(attrs={'data-control': 'select2'}) )
    stratum = forms.ChoiceField(choices=[('', '----------'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], label='Estrato', required=False)
    birth_country = forms.ChoiceField(choices=[('', '----------')] + [(country.pais, country.pais) for country in Paises.objects.using("lectaen").all()], label='País de Nacimiento' , widget=forms.Select(attrs={'data-control': 'select2'}))
    military_id = forms.CharField(label='Libreta Militar', required=False)
    blood_group = forms.ChoiceField(choices=[('', '-----'), ('OP', 'O +'), ('ON', 'O -'), ('AN', 'A -'), ('AP', 'A +'), ('BP', 'B +'), ('BN', 'B -'), ('ABP', 'AB +'), ('ABN', 'AB -')], label='Grupo Sanguíneo', required=False)
    profession = forms.ChoiceField(choices=[('', '----------')] + [(profesion.idprofesion, profesion.profesion) for profesion in Profesiones.objects.using("lectaen").all()], label='Profesión', required=False , widget=forms.Select(attrs={'data-control': 'select2'}) )
    residence_address = forms.CharField(label='Dirección de Residencia')
    email = forms.EmailField(label='E-mail')
    residence_city = forms.ChoiceField(choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.using("lectaen").all().order_by('ciudad')], label='Ciudad de Residencia',widget=forms.Select(attrs={'data-control': 'select2'}))
    cell_phone = forms.CharField(label='Celular')
    residence_country = forms.ChoiceField(choices=[('', '----------')] + [(country.pais, country.pais) for country in Paises.objects.using("lectaen").all()], label='País de residencia' , widget=forms.Select(attrs={'data-control': 'select2'}))
    employee_phone = forms.CharField(label='Teléfono del Empleado', required=False)
    pants_size = forms.ChoiceField(choices=[('', '----------'), ('6', '6'), ('8', '8'), ('10', '10'), ('12', '12'), ('14', '14'), ('16', '16'), ('28', '28'), ('30', '30'), ('32', '32'), ('34', '34'), ('36', '36'), ('38', '38'), ('40', '40')], label='Talla Pantalón',required=False)
    shirt_size = forms.ChoiceField(choices=[('', '----------'), ('38', '38'), ('40', '40'), ('42', '42'), ('44', '44'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], label='Talla Camisa' , required=False)
    shoes_size = forms.ChoiceField(choices=[('', '----------'), ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44')], label='Talla Zapatos', required=False)



            
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        second_name = cleaned_data.get('second_name', '')
        first_last_name = cleaned_data.get('first_last_name')
        second_last_name = cleaned_data.get('second_last_name', '')
        height = cleaned_data.get('height')
        weight = cleaned_data.get('weight')
        identification_number = cleaned_data.get('identification_number')
        military_id = cleaned_data.get('military_id')
        cell_phone = cleaned_data.get('cell_phone')
        employee_phone = cleaned_data.get('employee_phone')

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', first_name):
            self.add_error('first_name', "El nombre solo puede contener letras.")
        else:
            cleaned_data['first_name'] = first_name.upper()

        if second_name and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]*$', second_name):
            self.add_error('second_name', "El segundo nombre solo puede contener letras.")
        else:
            cleaned_data['second_name'] = second_name.upper()

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', first_last_name):
            self.add_error('first_last_name', "El primer apellido solo puede contener letras.")
        else:
            cleaned_data['first_last_name'] = first_last_name.upper()

        if second_last_name and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]*$', second_last_name):
            self.add_error('second_last_name', "El segundo apellido solo puede contener letras.")
        else:
            cleaned_data['second_last_name'] = second_last_name.upper()

        if height is not None and not re.match(r'^\d+(\.)?\d*$', str(height)):
            self.add_error('height', "Por favor, introduzca una altura válida. Debe usar punto decimal.")
        if weight is not None and not re.match(r'^\d+(\.)?\d*$', str(weight)):
            self.add_error('weight', "Por favor, introduzca un peso válido. Debe usar punto decimal.")

        if identification_number and not re.match(r'^\d+$', str(identification_number)):
            self.add_error('identification_number', "Este campo debe contener solo números.")
        if military_id and not re.match(r'^\d+$', military_id):
            self.add_error('military_id', "Este campo debe contener solo números.")
        if not re.match(r'^\d+$', cell_phone):
            self.add_error('cell_phone', "Este campo debe contener solo números.")
        if employee_phone and not re.match(r'^\d+$', employee_phone):
            self.add_error('employee_phone', "Este campo debe contener solo números.")

        return cleaned_data
                
    def set_premium_fields(self, premium=False, fields_to_adjust=None):
        if fields_to_adjust is not None:
            for field_name in fields_to_adjust:
                field = self.fields.get(field_name)
                if field:
                    field.disabled = not premium

    def set_required(self, activate):
        for field_name, field in self.fields.items():
            field.required = activate
        
    
    
    
    
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.layout = Layout(
            Div(
                HTML('<h3>Datos de Identificación</h3>'),
                Div(
                    Div('identification_type', css_class='col'),
                    Div('identification_number', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('expedition_date', css_class='col'),
                    Div('expedition_city', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('first_name', css_class='col'),
                    Div('second_name', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('first_last_name', css_class='col'),
                    Div('second_last_name', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Div(
                HTML('<h3>Datos Personales</h3>'),
                Div(
                    Div('sex', css_class='col'),
                    Div('height', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('marital_status', css_class='col'),
                    Div('weight', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('birthdate', css_class='col'),
                    Div('education_level', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('birth_city', css_class='col'),
                    Div('stratum', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('birth_country', css_class='col'),
                    Div('military_id', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('blood_group', css_class='col'),
                    Div('profession', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Div(
                HTML('<h3>Datos de Contacto</h3>'),
                Div(
                    Div('residence_address', css_class='col'),
                    Div('email', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('residence_city', css_class='col'),
                    Div('cell_phone', css_class='col'),
                    css_class='row'
                ),
                Div(
                    Div('residence_country', css_class='col'),
                    Div('employee_phone', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Div(
                HTML('<h3>Dotación</h3>'),
                Div(
                    Div('pants_size', css_class='col'),
                    Div('shirt_size', css_class='col'),
                    Div('shoes_size', css_class='col'),
                    css_class='row'
                ),
                css_class='container'
            ),
            Submit('submit', 'Guardar Empleado', css_class='btn btn-primary mt-3'),
        )










