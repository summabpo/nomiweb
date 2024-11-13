from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class  CompaniesForm(forms.Form):# Campos de identificación y datos básicos
    nit = forms.CharField(label='NIT', max_length=20)
    nombreempresa = forms.CharField(label='Nombre de la Empresa', max_length=255)
    dv = forms.CharField(label='DV', max_length=10)
    tipodoc = forms.CharField(label='Tipo de Documento', max_length=2)
    replegal = forms.CharField(label='Representante Legal', max_length=255)

    # Campos de contacto
    direccionempresa = forms.CharField(label='Dirección de la Empresa', max_length=255)
    telefono = forms.CharField(label='Teléfono', max_length=20)
    email = forms.EmailField(label='Correo Electrónico', max_length=30)

    # Relaciones con otras entidades
    codciudad = forms.CharField(label='Ciudad', max_length=50)
    pais = forms.CharField(label='País', max_length=50)
    arl = forms.CharField(label='ARL', max_length=50)

    # Campos de nómina y RRHH
    contactonomina = forms.CharField(label='Contacto de Nómina', max_length=50)
    emailnomina = forms.EmailField(label='Correo de Nómina', max_length=50)
    contactorrhh = forms.CharField(label='Contacto RRHH', max_length=50)
    emailrrhh = forms.EmailField(label='Correo RRHH', max_length=50)

    # Contabilidad y certificaciones
    contactocontab = forms.CharField(label='Contacto Contabilidad', max_length=50)
    emailcontab = forms.EmailField(label='Correo Contabilidad', max_length=50)
    cargocertificaciones = forms.CharField(label='Cargo Certificaciones', max_length=50)
    firmacertificaciones = forms.CharField(label='Firma Certificaciones', max_length=50)

    # Datos adicionales
    website = forms.URLField(label='Sitio Web', required=False)
    logo = forms.CharField(label='Logo', max_length=40, required=False)
    metodoextras = forms.CharField(label='Método Extras', max_length=255, required=False)
    realizarparafiscales = forms.CharField(label='Realizar Parafiscales', max_length=2, required=False)
    vstccf = forms.CharField(label='VST CCF', max_length=2, required=False)
    vstsenaicbf = forms.CharField(label='VST SENA/ICBF', max_length=2, required=False)
    ige100 = forms.CharField(label='IGE 100', max_length=2, required=False)
    slntarifapension = forms.CharField(label='SLN Tarifa Pensión', max_length=2, required=False)

    # Detalles bancarios
    banco = forms.CharField(label='Banco', max_length=50, required=False)
    numcuenta = forms.CharField(label='Número de Cuenta', max_length=255, required=False)
    tipocuenta = forms.CharField(label='Tipo de Cuenta', max_length=10, required=False)

    # Sucursales y aportantes
    codigosuc = forms.CharField(label='Código Sucursal', max_length=10, required=False)
    nombresuc = forms.CharField(label='Nombre Sucursal', max_length=40, required=False)
    claseaportante = forms.CharField(label='Clase Aportante', max_length=1, required=False)
    tipoaportante = forms.IntegerField(label='Tipo Aportante', required=False)
    ajustarnovedad = forms.CharField(label='Ajustar Novedad', max_length=2, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
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
            Submit('submit', 'Guardar')
        )