import re
# Django
from django import forms
from apps.common.models import Tipodocumento , Contratosemp , User , Cargos, Centrotrabajo,Paises , Tipodenomina , Ciudades , Profesiones,Tipocontrato , ModelosContratos ,Tiposalario , Bancos , Costos ,Subcostos , Entidadessegsocial
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Row,Column,HTML
from django.urls import reverse
from django.core.exceptions import ValidationError


TipoCcuenta = [
    ('', '---------------------'),
    ('CC', 'Cédula de Ciudadanía'),
    ('CE', 'Cédula de Extranjería'),
    ('NI', 'NI'),
]


CHOICE_TIPODOC = [
    ('', '---------------------'),
    ('CC', 'Cédula de Ciudadanía'),
    ('CE', 'Cédula de Extranjería'),
    ('NI', 'NI'),
]


CLASE_APORTANTE_CHOICES = [
    ('A', '200 o más cotizantes'),
    ('B', 'Menos de 200 cotizantes'),
    ('C', 'MiPyme Ley 590 de 2000 (menos de 200 cotizantes - descuentos parafiscales)'),
    ('D', 'Beneficiaria Ley 1429 de 2010 (progresividad en aportes parafiscales)'),
    ('I', 'Independientes'),
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

CHOICE_TIPO_PRESENTACION_PLANILLA = [
    ('U', 'Único'),
    ('S', 'Sucursal'),
]

CHOICE_NATURALEZA_JURIDICA = [
    (1, 'Pública'),
    (2, 'Privada'),
    (3, 'Mixta'),
    (4, 'Organismos multilaterales'),
    (5, 'Entidades de derecho público no sometidas a la legislación colombiana'),
]

CHOICE_TIPODOC_REP = [
    ('CC', 'Cédula de Ciudadanía'),
    ('CE', 'Cédula de Extranjería'),
    ('PA', 'Pasaporte'),
    ('CD', 'Carné Diplomático'),
]



def validate_text_length(value, max_length):
    if len(value) > max_length:
        raise ValidationError(f"Este campo no puede tener más de {max_length} caracteres.")

class CompanyForm(forms.Form):
    def disable_field(self, field):
        self.fields[field].disabled = True
        self.fields[field].required = False

    nit = forms.CharField(
        label='NIT',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    nombreempresa = forms.CharField(
        label='Nombre de la Empresa',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    dv = forms.CharField(
        label='Dv',
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    replegal = forms.CharField(
        label='Representante Legal',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


    ## campos de informacion general inicio 
    
    # Número de identificación del representante legal
    numero_identificacion_rep_legal = forms.CharField(
        label='Número Identificación R Legal',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Datos personales del representante legal
    papellido_rep_legal = forms.CharField(
        label='Primer Apellido R Legal',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sapellido_rep_legal = forms.CharField(
        label='Segundo Apellido R Legal',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pnombre_rep_legal = forms.CharField(
        label='Primer Nombre R Legal',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    snombre_rep_legal = forms.CharField(
        label='Segundo Nombre R Legal',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


    ## campos de informacion general  fin 
    direccionempresa = forms.CharField(
        label='Dirección',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label='Correo Electrónico',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    website = forms.URLField(label='Sitio Web', required=False)

    # Campos de nómina
    contactonomina = forms.CharField(label='Contacto de Nómina',required=False, max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    emailnomina = forms.EmailField(label='Correo de Nómina',required=False, max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    # Campos de RRHH
    contactorrhh = forms.CharField(label='Contacto RRHH',required=False, max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])
    emailrrhh = forms.EmailField(label='Correo RRHH',required=False, max_length=50 ,validators=[lambda v: validate_text_length(v, 50)])

    # Contabilidad y certificaciones
    contactocontab = forms.CharField(label='Contacto Contabilidad',required=False, max_length=50,validators=[lambda v: validate_text_length(v,50)])
    emailcontab = forms.EmailField(label='Correo Contabilidad',required=False, max_length=50,validators=[lambda v: validate_text_length(v,50)])




    # Parafiscales 
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

    ajustarnovedad =  forms.BooleanField(
        label='Ajustar Novedad',
        required=False,
        widget=forms.CheckboxInput()
    )

    empresa_exonerada =  forms.BooleanField(
        label='Empresa Exonerada',
        required=False,
        widget=forms.CheckboxInput()
    )


    codigo_sucursal = forms.CharField(
        label='Código Sucursal',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


    nombre_sucursal = forms.CharField(
        label='Nombre Sucursal',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


    def __init__(self, *args, **kwargs):
        self.idempresa = kwargs.pop('idempresa', None)
        edit = kwargs.pop('edit', None)
        super(CompanyForm, self).__init__(*args, **kwargs)
        
        self.fields['tipodoc'] = forms.ChoiceField(
            choices=CHOICE_TIPODOC,
            label='Tipo de documento',
            required=False,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
                
            })
        )

        self.fields['city'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().exclude(idciudad=1122).order_by('ciudad')],
            label='Ciudad',
            required=False,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
    
            })
        )

        self.fields['country'] = forms.ChoiceField(
            choices=[('', '----------')] + [(country.idpais, country.pais) for country in Paises.objects.all()],
            label='País',
            required=False,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
    
            })
        )

        self.fields['bankAccount'] = forms.ChoiceField(
            choices=[('', '----------')] + [(banco.idbanco, banco.nombanco) for banco in Bancos.objects.all().exclude(idbanco=27).order_by('nombanco')], 
            label='Banco de la Cuenta', 
            required=False,
            widget=forms.Select(attrs={
                    'data-control': 'select2',

                    'class': 'form-select',

                }), )
        self.fields['accountType'] = forms.ChoiceField(
            label='Tipo de Cuenta', 
            choices=TipoCcuenta, 
            widget=forms.Select(attrs={
                    'data-control': 'select2',

                    'class': 'form-select',
                    'data-hide-search': 'true',

                }),
            required=False)             


        self.fields['payrollAccount'] = forms.CharField(label='Cuenta de Nómina', max_length=100, required=False) 
        
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
        

        self.fields['tipo_presentacion_planilla'] = forms.ChoiceField(
            choices=[('', '----------')] + CHOICE_TIPO_PRESENTACION_PLANILLA,
            label='Tipo Presentación Planilla',
            required=False , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    
                }),) 
        
        self.fields['arl'] = forms.ChoiceField(
            choices=[('', '----------')] + [(entidad.identidad, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='ARL').order_by('entidad')],
            label='ARL',
            required=False,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    
                }),) 

        self.fields['naturaleza_juridica'] = forms.ChoiceField(
            choices=[('', '----------')] + CHOICE_NATURALEZA_JURIDICA,
            label='Naturaleza Jurídica',
            required=False , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    
                }),) 
        

        self.fields['tipo_identificacion_rep_legal'] = forms.ChoiceField(
            choices=[('', '----------')] + CHOICE_TIPODOC_REP,
            label='Tipo Identificación',
            required=False , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    
                }),) 
        

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_Company'
        self.helper.enctype = 'multipart/form-data'
        
        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('companies:company_edit',kwargs={'type': edit}),
            'up-accept-location': reverse('companies:company_edit',kwargs={'type': edit}),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })



        for field in ['nit','nombreempresa','dv','tipodoc','arl','replegal']:
            self.disable_field(field)

        # Atributos específicos para Unpoly
        # self.helper.attrs.update({
        #     'up-target': '#modal-content',
        #     'up-mode': 'replace',
        #     'up-layer': 'current',
        #     'up-submit': reverse('companies:company_edit',kwargs={'type': edit}),
        #     'up-accept-location': reverse('companies:company_edit',kwargs={'type': edit}),
        # })
        
        layout_fields = [

            ##Información General ( va bloqueada )
            Row(
                Column('nombreempresa', css_class='col-md-12'),
            ),
            Row(
                Column('nit', css_class='col-md-4'),
                Column('dv', css_class='col-md-2'),
                Column('tipodoc', css_class='col-md-6'),
            ),

            Row(
                Column('replegal', css_class='col-md-6'),
                Column('arl', css_class='col-md-6'),
            ),

        ]
        
        if edit == '1':
            layout_fields.append(
                ## Información Bancaria
                Row(
                    Column('naturaleza_juridica', css_class='form-group col-md-4 mb-0'),
                    Column('tipo_identificacion_rep_legal', css_class='form-group col-md-4 mb-0'),
                    Column('numero_identificacion_rep_legal', css_class='form-group col-md-4 mb-0'),
                    css_class='row'
                )
            )

            layout_fields.append(

                Row(
                    Column('papellido_rep_legal', css_class='col-md-3'),
                    Column('sapellido_rep_legal', css_class='col-md-3'),
                    Column('pnombre_rep_legal', css_class='col-md-3'),
                    Column('snombre_rep_legal', css_class='col-md-3'),
                    css_class='row'
                )
            )


        
        if edit == '2':
            layout_fields.append(
                ## Información Bancaria
                Row(
                    Column('bankAccount', css_class='col-md-4'),
                    Column('accountType', css_class='col-md-4'),
                    Column('payrollAccount', css_class='col-md-4'),
                    css_class='row'
                )
            )

        if edit == '3':
            ## Ubicación y Contacto
            layout_fields.append(
                Row(
                    Column('direccionempresa', css_class='col-md-6'),
                    Column('city', css_class='col-md-3'),
                    Column('country', css_class='col-md-3'),
                    css_class='row'
                )
            )

            layout_fields.append(
                Row(
                    Column('telefono', css_class='col-md-2'),
                    Column('email', css_class='col-md-4'),
                    Column('website', css_class='col-md-6'),
                    css_class='row'
                ),
            )


        if edit == '4':
            ## Ubicación y Contacto
            layout_fields.append(
                Row(
                    Column('contactonomina', css_class='form-group col-md-4 mb-0'),
                    Column('contactocontab', css_class='form-group col-md-4 mb-0'),
                    Column('contactorrhh', css_class='form-group col-md-4 mb-0'),
                )
            )

            layout_fields.append(
                Row(
                    Column('emailnomina', css_class='form-group col-md-4 mb-0'),
                    Column('emailcontab', css_class='form-group col-md-4 mb-0'),
                    Column('emailrrhh', css_class='form-group col-md-4 mb-0'),
                    css_class='row'
                ),
            )

        if edit == '5':
            ## Ubicación y Contacto
            layout_fields.append(
                Row(
                    Column('claseaportante', css_class='form-group col-md-4 mb-0'),
                    Column('tipoaportante', css_class='form-group col-md-4 mb-0'),
                    Column('tipo_presentacion_planilla', css_class='form-group col-md-4 mb-0'),
                )
            )

            layout_fields.append(
                Row(
                    Column('codigo_sucursal', css_class='form-group col-md-3 mb-0'),
                    Column('nombre_sucursal', css_class='form-group col-md-9 mb-0'),
                )
            )

            layout_fields.append(
                HTML('<div class="separator my-10"></div>'),
            )

            layout_fields.append(
                Row(
                    Column('vstccf', css_class='form-group col-md-6 mb-0'),
                    Column('vstsenaicbf', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
            )
            layout_fields.append(
                Row(
                    Column('ige100', css_class='form-group col-md-6 mb-0'),
                    Column('slntarifapension', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
            )
            layout_fields.append(
                Row(
                    Column('ajustarnovedad', css_class='form-group col-md-6 mb-0'),
                    Column('metodoextras', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
            )
            layout_fields.append(
                Row(
                    Column('realizarparafiscales', css_class='form-group col-md-6 mb-0'),
                    Column('empresa_exonerada', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
            )






        self.helper.layout = Layout(*layout_fields)


        
                
    