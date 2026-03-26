from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column ,HTML
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
    ('', '---------------------'),
    ('CC', 'Cédula de Ciudadanía'),
    ('CE', 'Cédula de Extranjería'),
    ('TI', 'Tarjeta de Identidad'),
    ('PA', 'Pasaporte'),
    ('CD', 'Carné Diplomático'),
    ('SC', 'Salvoconducto de Permanencia'),
    ('PT', 'Permiso por Protección Temporal'),
    ('NI', 'NI'),
]


TIPO_APORTANTE_CHOICES = [
    (1, '1 - Empleador'),
    (2, '2 - Independiente'),
    (3, '3 - Independiente con trabajadores a cargo'),
    (4, '4 - Contratista'),
    (5, '5 - Pensionado'),
    (6, '6 - Administradora'),
    (7, '7 - Caja de Compensación Familiar'),
    (8, '8 - Entidad pública'),
    (9, '9 - Cooperativa / Precooperativa de trabajo asociado'),
    (10, '10 - Grupos y agremiaciones'),
    (11, '11 - Asociación/agremiación de pensionados'),
    (12, '12 - Madres comunitarias / FAMI'),
    (14, '14 - Empresas de servicios temporales'),
    (15, '15 - Personas naturales sector agropecuario'),
    (16, '16 - Servicio doméstico'),
    (18, '18 - Aportante Economía Naranja'),
    (19, '19 - Entidades territoriales en educación'),
    (20, '20 - Entidades religiosas'),
]

CLASE_APORTANTE_CHOICES = [
    ('A', '200 o más cotizantes'),
    ('B', 'Menos de 200 cotizantes'),
    ('C', 'MiPyme Ley 590 de 2000 (menos de 200 cotizantes - descuentos parafiscales)'),
    ('D', 'Beneficiaria Ley 1429 de 2010 (progresividad en aportes parafiscales)'),
    ('I', 'Independientes'),
]


TIPO_PERSONA_CHOICES = [
    ('N', 'Natural'),
    ('J', 'Jurídica'),
]

TIPO_PRESENTACION_PLANILLA_CHOICES = [
    ('U', 'Único'),
    ('S', 'Sucursal'),
]

NATURALEZA_JURIDICA_CHOICES = [
    (1, 'Pública'),
    (2, 'Privada'),
    (3, 'Mixta'),
    (4, 'Organismos multilaterales'),
    (5, 'Entidades de derecho público no sometidas a la legislación colombiana'),
]

TIPODOC_REP_CHOICES = [
    ('CC', 'Cédula de Ciudadanía'),
    ('CE', 'Cédula de Extranjería'),
    ('PA', 'Pasaporte'),
    ('CD', 'Carné Diplomático'),
]



class  CompaniesForm(forms.Form):# Campos de identificación y datos básicos
    nit = forms.CharField(label='NIT', max_length=20)
    nombreempresa = forms.CharField(label='Nombre de la Empresa', max_length=255 , validators=[lambda v: validate_text_length(v, 255)])
    dv = forms.CharField(label='DV', max_length=2 , validators=[lambda v: validate_text_length(v, 2)])
    replegal = forms.CharField(label='Representante Legal', max_length=255,validators=[lambda v: validate_text_length(v, 255)])

    # Campos de contacto
    direccionempresa = forms.CharField(label='Dirección de la Empresa', max_length=255,validators=[lambda v: validate_text_length(v, 255)])
    telefono = forms.CharField(label='Teléfono', max_length=20,validators=[lambda v: validate_text_length(v, 20)])
    email = forms.EmailField(label='Correo Electrónico', max_length=30)

    # Relaciones con otras entidades
    # codciudad = forms.CharField(label='Ciudad', max_length=50)
    # pais = forms.CharField(label='País', max_length=50)
    # arl = forms.CharField(label='ARL', max_length=50)

    # Campos de nómina y RRHH
    contactonomina = forms.CharField(label='Contacto de Nómina',required=False, max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    emailnomina = forms.EmailField(label='Correo de Nómina',required=False, max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    contactorrhh = forms.CharField(label='Contacto RRHH', max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    emailrrhh = forms.EmailField(label='Correo RRHH', max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])

    # Contabilidad y certificaciones
    contactocontab = forms.CharField(label='Contacto Contabilidad',required=False, max_length=50,validators=[lambda v: validate_text_length(v,50)])
    emailcontab = forms.EmailField(label='Correo Contabilidad',required=False, max_length=50,validators=[lambda v: validate_text_length(v,50)])
    cargocertificaciones = forms.CharField(label='Cargo Certificaciones',required=False, max_length=50,validators=[lambda v: validate_text_length(v,50)])
    firmacertificaciones = forms.ImageField(label='Firma Certificaciones',required=False,validators=[lambda v: validate_text_length_imagen(v, 30)])

    # Datos adicionales
    website = forms.URLField(label='Sitio Web', required=False)
    logo = forms.ImageField(label='Logo',validators=[lambda v: validate_text_length_imagen(v, 30)])
    
    metodoextras = forms.BooleanField(
        label='Método Extras',
        required=False,
        widget=forms.CheckboxInput()
    )

    realizarparafiscales = forms.BooleanField(
        label='Realizar Parafiscales',
        required=False,
        widget=forms.CheckboxInput()
    )

    vstccf = forms.BooleanField(
        label='VST CCF',
        required=False,
        widget=forms.CheckboxInput()
    )

    vstsenaicbf = forms.BooleanField(
        label='VST SENA/ICBF',
        required=False,
        widget=forms.CheckboxInput()
    )

    ige100 = forms.BooleanField(
        label='IGE 100',
        required=False,
        widget=forms.CheckboxInput()
    )

    slntarifapension = forms.BooleanField(
        label='SLN Tarifa Pensión',
        required=False,
        widget=forms.CheckboxInput()
    )
    
    ajustarnovedad =  forms.BooleanField(
        label='Ajustar Novedad',
        required=False,
        widget=forms.CheckboxInput()
    )
    
    
    # Detalles bancarios
    banco = forms.CharField(label='Banco', max_length=50, required=False, validators=[lambda v: validate_text_length(v, 50)])
    numcuenta = forms.CharField(label='Número de Cuenta', max_length=255, required=False,   validators=[lambda v: validate_text_length(v, 255)])
    tipocuenta = forms.CharField(label='Tipo de Cuenta', max_length=10, required=False, validators=[lambda v: validate_text_length(v, 10)])

    # Sucursales y aportantes
    codigosuc = forms.CharField(label='Código Sucursal', max_length=10, required=False ,validators=[lambda v: validate_text_length(v, 10)])
    nombresuc = forms.CharField(label='Nombre Sucursal', max_length=40, required=False,validators=[lambda v: validate_text_length(v, 40)])
    
    # Tipo de persona
    tipo_persona = forms.ChoiceField(
        label='Tipo Persona',
        choices=[('', '----------')] + TIPO_PERSONA_CHOICES,
        required=False
    )

    naturaleza_juridica = forms.ChoiceField(
        label='Naturaleza Jurídica',
        choices=[('', '----------')] + NATURALEZA_JURIDICA_CHOICES,
        required=False
    )

    empresa_exonerada = forms.BooleanField(
        label='Empresa Exonerada',
        required=False,
        widget=forms.CheckboxInput()
    )

    tipo_presentacion_planilla = forms.ChoiceField(
        label='Tipo Presentación Planilla',
        choices=[('', '----------')] + TIPO_PRESENTACION_PLANILLA_CHOICES,
        required=False
    )

    codigo_sucursal = forms.CharField(
        label='Código Sucursal',
        max_length=10,
        required=False
    )

    nombre_sucursal = forms.CharField(
        label='Nombre Sucursal',
        max_length=40,
        required=False
    )

    # Representante legal estructurado
    tipo_identificacion_rep_legal = forms.ChoiceField(
        label='Tipo Documento Representante Legal',
        choices=[('', '----------')] + TIPODOC_REP_CHOICES,
        required=False
    )

    numero_identificacion_rep_legal = forms.CharField(
        label='Número Identificación Representante Legal',
        max_length=20,
        required=False
    )

    papellido_rep_legal = forms.CharField(
        label='Primer Apellido Representante Legal',
        max_length=50,
        required=False
    )

    sapellido_rep_legal = forms.CharField(
        label='Segundo Apellido Representante Legal',
        max_length=50,
        required=False
    )

    pnombre_rep_legal = forms.CharField(
        label='Primer Nombre Representante Legal',
        max_length=50,
        required=False
    )

    snombre_rep_legal = forms.CharField(
        label='Segundo Nombre Representante Legal',
        max_length=50,
        required=False
    )
    
    
    
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
                
            })
        )

        
        self.fields['codciudad'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().exclude(idciudad=1122).order_by('ciudad')],
            label='Ciudad',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                
            })
        )
        
        self.fields['pais'] = forms.ChoiceField(
            choices=[('', '----------')] + [(country.idpais, country.pais) for country in Paises.objects.all()],
            label='País',
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                
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
                    
                }),) 
        
        self.fields['claseaportante'] = forms.ChoiceField(
            choices=[('', '----------')] + CLASE_APORTANTE_CHOICES,
            label='Clase Aportante',
            required=False , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    
                }),) 
        self.fields['tipoaportante'] = forms.ChoiceField(
            choices=[('', '----------')] + TIPO_APORTANTE_CHOICES,
            label='Tipo Aportante',
            required=False,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    
                }),) 
        
        self.helper = FormHelper()        
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_compani'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('admin:companiescreate'),
            'up-accept-location': reverse('admin:companiescreate'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
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
                Column('tipo_persona', css_class='form-group col-md-6 mb-0'),
                Column('naturaleza_juridica', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            HTML('<h3>Representante Legal</h3>'),

            Row(
                Column('tipo_identificacion_rep_legal', css_class='form-group col-md-4 mb-0'),
                Column('numero_identificacion_rep_legal', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),

            Row(
                Column('pnombre_rep_legal', css_class='form-group col-md-3 mb-0'),
                Column('snombre_rep_legal', css_class='form-group col-md-3 mb-0'),
                Column('papellido_rep_legal', css_class='form-group col-md-3 mb-0'),
                Column('sapellido_rep_legal', css_class='form-group col-md-3 mb-0'),
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
            HTML('<h3>Banco</h3>'),
            Row(
                Column('banco', css_class='form-group col-md-4 mb-0'),
                Column('numcuenta', css_class='form-group col-md-4 mb-0'),
                Column('tipocuenta', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('codigosuc', css_class='form-group col-md-6 mb-0'),
                Column('nombresuc', css_class='form-group col-md-6 mb-0'),
                
                css_class='form-row'
            ),
            Row(
                Column('claseaportante', css_class='form-group col-md-6 mb-0'),
                Column('tipoaportante', css_class='form-group col-md-6 mb-0'),
                
                css_class='form-row'
            ),
            HTML('<h3>Configuración PILA</h3>'),

            Row(
                Column('tipo_presentacion_planilla', css_class='form-group col-md-6 mb-0'),
                Column('empresa_exonerada', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),

            Row(
                Column('codigo_sucursal', css_class='form-group col-md-6 mb-0'),
                Column('nombre_sucursal', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),

            HTML('<h3>Ajustes</h3>'),
            Row(
                
                Column('vstccf', css_class='form-group col-md-6 mb-0'),
                Column('vstsenaicbf', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('ige100', css_class='form-group col-md-6 mb-0'),
                Column('slntarifapension', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('ajustarnovedad', css_class='form-group col-md-6 mb-0'),
                Column('metodoextras', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('realizarparafiscales', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )