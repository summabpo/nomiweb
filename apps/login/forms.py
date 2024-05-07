from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Field
from apps.companies.models import * 


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Ingrese su nombre de usuario'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('username', wrapper_class='col-md-3'),
                    css_class='form-group row'
                ),
                Div(
                    Field('password', wrapper_class='col-md-3'),
                    css_class='form-group row'
                ),
                css_class='form-group'
            ),
            Submit('submit', 'Ingresar', css_class='btn btn-light-success')
        )
        
class MiFormulario(forms.Form):
    def __init__(self, *args, **kwargs):
        opciones_1 = kwargs.pop('opciones_1', [])
        opciones_2 = kwargs.pop('opciones_2', [])
        
        super(MiFormulario, self).__init__(*args, **kwargs)
        
        self.fields['identification_type'] = forms.ChoiceField(
            choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.all()],
            label='Tipo de documento de identidad'
        )
        self.fields['identification_number'] = forms.IntegerField(label='Documento de Identidad')
        self.fields['expedition_date'] = forms.DateField(
            label='Fecha de expedición',
            widget=forms.DateInput(attrs={'type': 'date'})
        )
        self.fields['expedition_city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')],
            label='Ciudad de expedición',
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        self.fields['first_name'] = forms.CharField(label='Primer Nombre')
        self.fields['second_name'] = forms.CharField(label='Segundo Nombre', required=False)
        self.fields['first_last_name'] = forms.CharField(label='Primer Apellido')
        self.fields['second_last_name'] = forms.CharField(label='Segundo Apellido', required=False)
        self.fields['sex'] = forms.ChoiceField(
            choices=[('', '----------'), ('masculino', 'Masculino'), ('femenino', 'Femenino')],
            label='Sexo'
        )
        self.fields['height'] = forms.CharField(label='Estatura (Mts)', required=False)
        self.fields['marital_status'] = forms.ChoiceField(
            choices=[('', '----------'), ('soltero', 'Soltero'), ('casado', 'Casado'), ('viudo', 'Viudo'), ('divorciado', 'Divorciado'), ('unionlibre', 'Unión Libre')],
            label='Estado Civil'
        )
        self.fields['weight'] = forms.CharField(label='Peso (Kg)', required=False)
        self.fields['birthdate'] = forms.DateField(
            label='Fecha de Nacimiento',
            widget=forms.DateInput(attrs={'type': 'date'})
        )
        self.fields['education_level'] = forms.ChoiceField(
            choices=[('', '----------'), ('primaria', 'Primaria'), ('Bachiller', 'Bachiller'), ('bachillerinc', 'Bachiller Incompleto'), ('tecnico', 'Técnico'), ('tecnologo', 'Tecnólogo'), ('universitario', 'Universitario'), ('universitarioinc', 'Universitario Incompleto'), ('postgrado', 'Postgrado'), ('magister', 'Magíster')],
            label='Nivel Educativo',
            required=False
        )
        self.fields['birth_city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')],
            label='Ciudad de Nacimiento',
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        self.fields['stratum'] = forms.ChoiceField(
            choices=[('', '----------'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')],
            label='Estrato',
            required=False
        )
        self.fields['birth_country'] = forms.ChoiceField(
            choices=[('', '----------')] + [(country.pais, country.pais) for country in Paises.objects.all()],
            label='País de Nacimiento',
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        self.fields['military_id'] = forms.CharField(label='Libreta Militar', required=False)
        self.fields['blood_group'] = forms.ChoiceField(
            choices=[('', '-----'), ('OP', 'O +'), ('ON', 'O -'), ('AN', 'A -'), ('AP', 'A +'), ('BP', 'B +'), ('BN', 'B -'), ('ABP', 'AB +'), ('ABN', 'AB -')],
            label='Grupo Sanguíneo',
            required=False
        )
        self.fields['profession'] = forms.ChoiceField(
            choices=[('', '----------')] + [(profesion.idprofesion, profesion.profesion) for profesion in Profesiones.objects.all()],
            label='Profesión',
            required=False,
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        self.fields['residence_address'] = forms.CharField(label='Dirección de Residencia')
        self.fields['email'] = forms.EmailField(label='E-mail')
        self.fields['residence_city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().order_by('ciudad')],
            label='Ciudad de Residencia',
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        self.fields['cell_phone'] = forms.CharField(label='Celular')
        self.fields['residence_country'] = forms.ChoiceField(
            choices=[('', '----------')] + [(country.pais, country.pais) for country in Paises.objects.all()],
            label='País de residencia',
            widget=forms.Select(attrs={'data-control': 'select2'})
        )
        self.fields['employee_phone'] = forms.CharField(label='Teléfono del Empleado', required=False)
        self.fields['pants_size'] = forms.ChoiceField(
            choices=[('', '----------'), ('6', '6'), ('8', '8'), ('10', '10'), ('12', '12'), ('14', '14'), ('16', '16'), ('28', '28'), ('30', '30'), ('32', '32'), ('34', '34'), ('36', '36'), ('38', '38'), ('40', '40')],
            label='Talla Pantalón',
            required=False
        )
        self.fields['shirt_size'] = forms.ChoiceField(
            choices=[('', '----------'), ('38', '38'), ('40', '40'), ('42', '42'), ('44', '44'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')],
            label='Talla Camisa',
            required=False
        )
        self.fields['shoes_size'] = forms.ChoiceField(
            choices=[('', '----------'), ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44')],
            label='Talla Zapatos',
            required=False
        )
        
        
        
        
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