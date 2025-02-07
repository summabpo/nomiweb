from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column 
from apps.common.models import Paises ,Ciudades , Bancos , Entidadessegsocial , Tipodocumento
from django.urls import reverse

from django.core.exceptions import ValidationError

def validate_text_length(value, max_length):
    if len(value) > max_length:
        raise ValidationError(f"Este campo no puede tener más de {max_length} caracteres.")

def validate_text_length_imagen(value, max_length):
    if len(value.name) > max_length:
        raise ValidationError(f"Este campo no puede tener más de {max_length} caracteres.")

CHOICE_TIPODOC = [
    ('CC', 'Cédula de Ciudadanía'),
    ('CE', 'Cédula de Extranjería'),
    ('NI', 'NIT'),
]
class  CompaniesForm(forms.Form):# Campos de identificación y datos básicos
    nit = forms.CharField(label='NIT', max_length=20)
    nombreempresa = forms.CharField(label='Nombre de la Empresa', max_length=255 , validators=[lambda v: validate_text_length(v, 255)])
    dv = forms.CharField(label='DV', max_length=2 , validators=[lambda v: validate_text_length(v, 2)])
    replegal = forms.CharField(label='Representante Legal', max_length=255,validators=[lambda v: validate_text_length(v, 255)])

    # Campos de contacto
    direccionempresa = forms.CharField(label='Dirección de la Empresa', max_length=255,validators=[lambda v: validate_text_length(v, 255)])
    telefono = forms.CharField(label='Teléfono', max_length=20,validators=[lambda v: validate_text_length(v, 20)])
    email = forms.EmailField(label='Correo Electrónico', max_length=30,validators=[lambda v: validate_text_length(v, 30)])

    # Relaciones con otras entidades
    # codciudad = forms.CharField(label='Ciudad', max_length=50)
    # pais = forms.CharField(label='País', max_length=50)
    # arl = forms.CharField(label='ARL', max_length=50)

    # Campos de nómina y RRHH
    contactonomina = forms.CharField(label='Contacto de Nómina', max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    emailnomina = forms.EmailField(label='Correo de Nómina', max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    contactorrhh = forms.CharField(label='Contacto RRHH', max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    emailrrhh = forms.EmailField(label='Correo RRHH', max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])

    # Contabilidad y certificaciones
    contactocontab = forms.CharField(label='Contacto Contabilidad', max_length=50,validators=[lambda v: validate_text_length(v,50)])
    emailcontab = forms.EmailField(label='Correo Contabilidad', max_length=50,validators=[lambda v: validate_text_length(v,50)])
    cargocertificaciones = forms.CharField(label='Cargo Certificaciones', max_length=50,validators=[lambda v: validate_text_length(v,50)])
    firmacertificaciones = forms.ImageField(label='Firma Certificaciones',validators=[lambda v: validate_text_length_imagen(v, 30)])

    # Datos adicionales
    website = forms.URLField(label='Sitio Web', required=False)
    logo = forms.ImageField(label='Logo',validators=[lambda v: validate_text_length_imagen(v, 30)])
    metodoextras = forms.CharField(label='Método Extras', max_length=255, required=False,validators=[lambda v: validate_text_length(v, 30)])
    realizarparafiscales = forms.CharField(label='Realizar Parafiscales', max_length=2, required=False,validators=[lambda v: validate_text_length(v, 2)])
    vstccf = forms.CharField(label='VST CCF', max_length=2, required=False,validators=[lambda v: validate_text_length(v, 2)])
    vstsenaicbf = forms.CharField(label='VST SENA/ICBF', max_length=2, required=False,  validators=[lambda v: validate_text_length(v, 2)])
    ige100 = forms.CharField(label='IGE 100', max_length=2, required=False,validators=[lambda v: validate_text_length(v, 2)])
    slntarifapension = forms.CharField(label='SLN Tarifa Pensión', max_length=2, required=False,validators=[lambda v: validate_text_length(v, 2)])

    # Detalles bancarios
    banco = forms.CharField(label='Banco', max_length=50, required=False, validators=[lambda v: validate_text_length(v, 50)])
    numcuenta = forms.CharField(label='Número de Cuenta', max_length=255, required=False,   validators=[lambda v: validate_text_length(v, 255)])
    tipocuenta = forms.CharField(label='Tipo de Cuenta', max_length=10, required=False, validators=[lambda v: validate_text_length(v, 10)])

    # Sucursales y aportantes
    codigosuc = forms.CharField(label='Código Sucursal', max_length=10, required=False ,validators=[lambda v: validate_text_length(v, 10)])
    nombresuc = forms.CharField(label='Nombre Sucursal', max_length=40, required=False,validators=[lambda v: validate_text_length(v, 40)])
    claseaportante = forms.CharField(label='Clase Aportante', max_length=1, required=False, validators=[lambda v: validate_text_length(v, 1)])
    tipoaportante = forms.IntegerField(label='Tipo Aportante', required=False, validators=[lambda v: validate_text_length(v, 1)])
    ajustarnovedad = forms.CharField(label='Ajustar Novedad', max_length=2, required=False,validators=[lambda v: validate_text_length(v, 2)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        self.fields['tipodoc'] = forms.ChoiceField(
            choices=CHOICE_TIPODOC,
            label='Tipo de documento',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
                'data-dropdown-parent':"#conceptsModal",
            })
        )

        
        self.fields['codciudad'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().exclude(idciudad=1122).order_by('ciudad')],
            label='Ciudad',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-dropdown-parent':"#conceptsModal",
            })
        )
        
        self.fields['pais'] = forms.ChoiceField(
            choices=[('', '----------')] + [(country.idpais, country.pais) for country in Paises.objects.all()],
            label='País',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-dropdown-parent':"#conceptsModal",
            })
        )
        
        self.fields['arl'] = forms.ChoiceField(
            choices=[('', '----------')] + [(entidad.identidad, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='ARL').order_by('entidad')],
            label='ARL',
            required=True , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#conceptsModal",
                }),) 
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_compani'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'hx-post': reverse('admin:companiescreate'),  # Usa el nombre de la vista en urls.py
            'hx-target': '#modal-container',  # El elemento donde se actualizará el contenido
            'hx-swap': 'innerHTML',  # Cómo se actualizará el contenido del objetivo
        })
        
        self.helper.layout = Layout(
            Row(
                Column('nit', css_class='form-group col-md-4 mb-0'),
                Column('nombreempresa', css_class='form-group col-md-4 mb-0'),
                Column('dv', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('tipodoc', css_class='form-group col-md-6 mb-0'),
                Column('replegal', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('direccionempresa', css_class='form-group col-md-6 mb-0'),
                Column('telefono', css_class='form-group col-md-3 mb-0'),
                Column('email', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('codciudad', css_class='form-group col-md-4 mb-0'),
                Column('pais', css_class='form-group col-md-4 mb-0'),
                Column('arl', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('contactonomina', css_class='form-group col-md-4 mb-0'),
                Column('contactocontab', css_class='form-group col-md-4 mb-0'),
                Column('contactorrhh', css_class='form-group col-md-4 mb-0'),
                
                css_class='form-row'
            ),
            Row(
                Column('emailnomina', css_class='form-group col-md-4 mb-0'),
                Column('emailcontab', css_class='form-group col-md-4 mb-0'),
                Column('emailrrhh', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('cargocertificaciones', css_class='form-group col-md-6 mb-0'),
                Column('firmacertificaciones', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('website', css_class='form-group col-md-6 mb-0'),
                Column('logo', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('metodoextras', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('realizarparafiscales', css_class='form-group col-md-4 mb-0'),
                Column('vstccf', css_class='form-group col-md-4 mb-0'),
                Column('vstsenaicbf', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('ige100', css_class='form-group col-md-6 mb-0'),
                Column('slntarifapension', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('banco', css_class='form-group col-md-4 mb-0'),
                Column('numcuenta', css_class='form-group col-md-4 mb-0'),
                Column('tipocuenta', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('codigosuc', css_class='form-group col-md-4 mb-0'),
                Column('nombresuc', css_class='form-group col-md-4 mb-0'),
                Column('claseaportante', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('tipoaportante', css_class='form-group col-md-6 mb-0'),
                Column('ajustarnovedad', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )