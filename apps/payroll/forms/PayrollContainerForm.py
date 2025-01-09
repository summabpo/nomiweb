from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import NeDatosMensual, Anos, Ciudades, Tipodenomina, Paises

class PayrollContainerForm(forms.Form):
    
    MONTH_CHOICES = (
        ('', '---'),
        ('ENERO', 'ENERO'),
        ('FEBRERO', 'FEBRERO'),
        ('MARZO', 'MARZO'),
        ('ABRIL', 'ABRIL'),
        ('MAYO', 'MAYO'),
        ('JUNIO', 'JUNIO'),
        ('JULIO', 'JULIO'),
        ('AGOSTO', 'AGOSTO'),
        ('SEPTIEMBRE', 'SEPTIEMBRE'),
        ('OCTUBRE', 'OCTUBRE'),
        ('NOVIEMBRE', 'NOVIEMBRE'),
        ('DICIEMBRE', 'DICIEMBRE'),
    )

    fechaliquidacioninicio = forms.DateField(
        label="Fecha Liquidación Inicio",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione una fecha de inicio de liquidación',
            'type': 'date'
        })
    )

    fechaliquidacionfin = forms.DateField(
        label="Fecha Liquidación Fin",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione una fecha de fin de liquidación',
            'type': 'date'
        })
    )

    fechageneracion = forms.DateField(
        label="Fecha Generación",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione una fecha de generación',
            'type': 'date'
        })
    )

    prefijo = forms.CharField(
        label='Prefijo',
        max_length=3,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese el prefijo'})
    )

    consecutivo = forms.IntegerField(
        label='Consecutivo',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ingrese el consecutivo'})
    )

    

    departamentogeneracion = forms.CharField(
        label='Departamento Generación',
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese el departamento de generación'})
    )

    ciudadgeneracion = forms.ChoiceField(
        label='Ciudad Generación',
        choices=[('', '-----')] + [(ciudad.idciudad, ciudad.ciudad) for ciudad in Ciudades.objects.all().order_by('ciudad')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una ciudad',
            'data-dropdown-parent': '#kt_modal_container',
        })
    )
    idioma = forms.CharField(
        label='Idioma',
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese el idioma'})
    )
    horageneracion = forms.TimeField(
        label="Hora Generación",
        required=False,
        input_formats=['%H%M%S'],
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione una hora de generación',
            'id': 'kt_hora_generacion',
            'type': 'time'
        })
    )
    periodonomina = forms.ChoiceField(
        label='Periodo de Nomina',
        choices=[('', '-----')] + [(tipo.idtiponomina, tipo.tipodenomina) for tipo in Tipodenomina.objects.filter(cod_dian__isnull=False).all().order_by('tipodenomina')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una periodo',
            'data-dropdown-parent': '#kt_modal_container',
        })
    )

    tipomoneda = forms.ChoiceField(
        label='Tipo de Moneda',
        choices=[('', '---'), ('COP', 'COP')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una tasa de cambio',
            'data-dropdown-parent': '#kt_modal_container',
        })
    )
    fechapago = forms.DateField(
        label="Fecha Pago",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione una fecha de pago',
            'type': 'date'
        })
    )
    ciudaddepartamento = forms.ChoiceField(
        label='Ciudad Departamento',
        choices=[('', '-----')] + [(ciudad.idciudad, ciudad.ciudad) for ciudad in Ciudades.objects.all().order_by('ciudad')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una ciudad',
            'data-dropdown-parent': '#kt_modal_container',
        })
    )

    mesacumular = forms.ChoiceField(
        label='Mes Acumular',
        choices= MONTH_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccione un mes',
            'data-dropdown-parent': '#kt_modal_container',
        })
    )
    anoacumular = forms.ChoiceField(
        label='Año Acumular',
        choices=[('', '-----')] + [(ano.ano, ano.ano) for ano in Anos.objects.all().order_by('-ano')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',  # Clases CSS del campo  
            'data-control': 'select2',
            'data-placeholder': 'Seleccione un año',
            'data-dropdown-parent': '#kt_modal_container',
        })
    )
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_payroll'
        self.helper.enctype = 'multipart/form-data'


        self.helper.layout = Layout(
            Row(
            Column('mesacumular', css_class='form-group col-md-6 mb-0'),
            Column('anoacumular', css_class='form-group col-md-6 mb-0'),
            css_class='row'
            ),
            Row(
            Column('fechaliquidacioninicio', css_class='form-group col-md-6 mb-0'),
            Column('fechaliquidacionfin', css_class='form-group col-md-6 mb-0'),
            css_class='row'
            ),
            Row(
            Column('prefijo', css_class='form-group col-md-3 mb-0'),
            Column('periodonomina', css_class='form-group col-md-3 mb-0'),
            Column('tipomoneda', css_class='form-group col-md-3 mb-0'),
            Column('idioma', css_class='form-group col-md-3 mb-0'),
            css_class='row'
            ),
            Row(
            # Column('paisgeneracion', css_class='form-group col-md-4 mb-0'),
            Column('ciudadgeneracion', css_class='form-group col-md-6 mb-0'),
            Column('fechapago', css_class='form-group col-md-6 mb-0'),
            css_class='row'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        
        fechaliquidacioninicio = cleaned_data.get("fechaliquidacioninicio")
        fechaliquidacionfin = cleaned_data.get("fechaliquidacionfin")
        fechageneracion = cleaned_data.get("fechageneracion")
        fechapago = cleaned_data.get("fechapago")

        
        
        if fechaliquidacioninicio and fechaliquidacionfin:
            if fechaliquidacioninicio > fechaliquidacionfin:
                self.add_error('fechaliquidacionfin', 'La fecha de liquidación fin debe ser mayor o igual a la fecha de liquidación inicio.')
        
        # if fechageneracion and fechapago:
        #     if fechageneracion > fechapago:
        #         self.add_error('fechapago', 'La fecha de pago debe ser mayor o igual a la fecha de generación.')
        
        return cleaned_data