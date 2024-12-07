import re
# Django
from django import forms
from apps.common.models import Tipodocumento ,Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Profesiones,Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit,HTML,Row,Column


class EmployeeForm(forms.Form):
    height = forms.CharField(
        required=False,
        initial='0.0',
        label='Estatura (Mts)'
    )
    
    weight = forms.CharField(
        required=False,
        initial='0.0',
        label='Peso (Kg)'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        second_name = cleaned_data.get('second_name')
        first_last_name = cleaned_data.get('first_last_name')
        second_last_name = cleaned_data.get('second_last_name')
        height = cleaned_data.get('height')
        weight = cleaned_data.get('weight')
        identification_number = cleaned_data.get('identification_number')
        military_id = cleaned_data.get('military_id')
        cell_phone = cleaned_data.get('cell_phone')
        employee_phone = cleaned_data.get('employee_phone')

        if first_name:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', first_name):
                self.add_error('first_name', "El nombre solo puede contener letras.")
            else:
                cleaned_data['first_name'] = first_name.upper()

        if second_name:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]*$', second_name):
                self.add_error('second_name', "El segundo nombre solo puede contener letras.")
            else:
                cleaned_data['second_name'] = second_name.upper()

        if first_last_name:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', first_last_name):
                self.add_error('first_last_name', "El primer apellido solo puede contener letras.")
            else:
                cleaned_data['first_last_name'] = first_last_name.upper()

        if second_last_name:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]*$', second_last_name):
                self.add_error('second_last_name', "El segundo apellido solo puede contener letras.")
            else:
                cleaned_data['second_last_name'] = second_last_name.upper()

        # Validación para height y weight si tienen contenido
        if height is not None and not re.match(r'^\d+(\.)?\d*$', str(height)):
            self.add_error('height', "Por favor, introduzca una altura válida. Debe usar punto decimal.")
        if weight is not None and not re.match(r'^\d+(\.)?\d*$', str(weight)):
            self.add_error('weight', "Por favor, introduzca un peso válido. Debe usar punto decimal.")

        if identification_number and not re.match(r'^\d+$', str(identification_number)):
            self.add_error('identification_number', "Este campo debe contener solo números.")
        if military_id and not re.match(r'^\d+$', military_id):
            self.add_error('military_id', "Este campo debe contener solo números.")
        if cell_phone and not re.match(r'^\d+$', cell_phone):
            self.add_error('cell_phone', "Este campo debe contener solo números.")
        if employee_phone and not re.match(r'^\d+$', employee_phone):
            self.add_error('employee_phone', "Este campo debe contener solo números.")

        return cleaned_data
                
    
                    
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        
        campos_a_ajustar = [
            'identification_type', 'identification_number', 'expedition_date', 'expedition_city', 'first_name',
            'second_name', 'first_last_name', 'second_last_name', 'sex', 'birthdate', 'birth_city', 'birth_country', 'blood_group'
        ]

        
        
        self.fields['identification_type'] = forms.ChoiceField(
            choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.all()],
            label='Tipo de documento de identidad',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )

        
        self.fields['identification_number'] = forms.IntegerField(label='Documento de Identidad',required=False)
        self.fields['expedition_date'] = forms.DateField(
            label='Fecha de expedición',
            widget=forms.DateInput(attrs={'type': 'date'}),
            required=False
        )
        self.fields['expedition_city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().exclude(idciudad=1122).order_by('ciudad')],
            label='Ciudad de expedición',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
            }),
            required=False
        )
        self.fields['first_name'] = forms.CharField(label='Primer Nombre',required=False)
        self.fields['second_name'] = forms.CharField(label='Segundo Nombre', required=False)
        self.fields['first_last_name'] = forms.CharField(label='Primer Apellido',required=False)
        self.fields['second_last_name'] = forms.CharField(label='Segundo Apellido', required=False)
        self.fields['sex'] = forms.ChoiceField(
            choices=[('', '----------'), ('masculino', 'Masculino'), ('femenino', 'Femenino')],
            label='Sexo',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        
        
        self.fields['marital_status'] = forms.ChoiceField(
            choices=[('', '----------'), ('soltero', 'Soltero'), ('casado', 'Casado'), ('viudo', 'Viudo'), ('divorciado', 'Divorciado'), ('unionlibre', 'Unión Libre')],
            label='Estado Civil',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        
        self.fields['birthdate'] = forms.DateField(
            label='Fecha de Nacimiento',
            widget=forms.DateInput(attrs={'type': 'date'}),
            required=False
        )
        self.fields['education_level'] = forms.ChoiceField(
            choices=[('', '----------'), ('primaria', 'Primaria'), ('Bachiller', 'Bachiller'), ('bachillerinc', 'Bachiller Incompleto'), ('tecnico', 'Técnico'), ('tecnologo', 'Tecnólogo'), ('universitario', 'Universitario'), ('universitarioinc', 'Universitario Incompleto'), ('postgrado', 'Postgrado'), ('magister', 'Magíster')],
            label='Nivel Educativo',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        self.fields['birth_city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().exclude(idciudad=1122).order_by('ciudad')],
            label='Ciudad de Nacimiento',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
            }),
            required=False
        )
        self.fields['stratum'] = forms.ChoiceField(
            choices=[('', '----------'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')],
            label='Estrato',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        self.fields['birth_country'] = forms.ChoiceField(
            choices=[('', '----------')] + [(country.idpais, country.pais) for country in Paises.objects.all()],
            label='País de Nacimiento',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
            }),
            required=False
        )
        self.fields['military_id'] = forms.CharField(label='Libreta Militar', required=False)
        self.fields['blood_group'] = forms.ChoiceField(
            choices=[('', '-----'), ('OP', 'O +'), ('ON', 'O -'), ('AN', 'A -'), ('AP', 'A +'), ('BP', 'B +'), ('BN', 'B -'), ('ABP', 'AB +'), ('ABN', 'AB -')],
            label='Grupo Sanguíneo',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        self.fields['profession'] = forms.ChoiceField(
            choices=[('', '----------')] + [(profesion.idprofesion, profesion.profesion) for profesion in Profesiones.objects.all()],
            label='Profesión',
            required=False,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
            }),
        )
        self.fields['residence_address'] = forms.CharField(label='Dirección de Residencia',required=False)
        self.fields['email'] = forms.EmailField(label='E-mail',required=False)
        self.fields['residence_city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().exclude(idciudad=1122).order_by('ciudad')],
            label='Ciudad de Residencia',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
            }),
            required=False
        )
        self.fields['cell_phone'] = forms.CharField(label='Celular',required=False)
        self.fields['residence_country'] = forms.ChoiceField(
            choices=[('', '----------')] + [(country.idpais, country.pais) for country in Paises.objects.all()],
            label='País de residencia',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
            }),
            required=False
        )
        self.fields['employee_phone'] = forms.CharField(label='Teléfono del Empleado', required=False)
        self.fields['pants_size'] = forms.ChoiceField(
            choices=[('', '----------'), ('6', '6'), ('8', '8'), ('10', '10'), ('12', '12'), ('14', '14'), ('16', '16'), ('28', '28'), ('30', '30'), ('32', '32'), ('34', '34'), ('36', '36'), ('38', '38'), ('40', '40')],
            label='Talla Pantalón',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        self.fields['shirt_size'] = forms.ChoiceField(
            choices=[('', '----------'), ('38', '38'), ('40', '40'), ('42', '42'), ('44', '44'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')],
            label='Talla Camisa',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        self.fields['shoes_size'] = forms.ChoiceField(
            choices=[('', '----------'), ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44')],
            label='Talla Zapatos',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
            }),
            required=False
        )
        
        
        # Iterar sobre los campos existentes
        for field_name in campos_a_ajustar:
            field = self.fields.get(field_name)
            if field:
                field.disabled = True
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.form_id = 'form_Employee_Edit'
        self.helper.enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            HTML('<h3>Datos de Identificación</h3>'),
            Row(
                Column('identification_type', css_class='form-group mb-0'),
                Column('identification_number', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('expedition_date', css_class='form-group mb-0'),
                Column('expedition_city', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('first_name', css_class='form-group mb-0'),
                Column('second_name', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('first_last_name', css_class='form-group mb-0'),
                Column('second_last_name', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            HTML('<div class="separator my-10"></div>'),
            HTML('<h3>Datos Personales</h3>'),
            
            Row(
                Column('sex', css_class='form-group mb-0'),
                Column('height', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('marital_status', css_class='form-group mb-0'),
                Column('weight', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('birthdate', css_class='form-group mb-0'),
                Column('education_level', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('birth_city', css_class='form-group mb-0'),
                Column('stratum', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('birth_country', css_class='form-group mb-0'),
                Column('military_id', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('blood_group', css_class='form-group mb-0'),
                Column('profession', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            HTML('<div class="separator my-10"></div>'),
            HTML('<h3>Datos de Contacto</h3>'),
            Row(
                Column('residence_address', css_class='form-group mb-0'),
                Column('email', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('residence_city', css_class='form-group mb-0'),
                Column('cell_phone', css_class='form-group mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('residence_country', css_class='form-group mb-0'),
                Column('employee_phone', css_class='form-group mb-0'),
                css_class='row'
            ),
                
            HTML('<div class="separator my-10"></div>'),
            HTML('<h3>Dotación</h3>'),
            Row(
                Column('pants_size', css_class='form-group mb-0'),
                Column('shirt_size', css_class='form-group mb-0'),
                Column('shoes_size', css_class='form-group mb-0'),
                css_class='row'
            ),
        )