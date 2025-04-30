from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.core.exceptions import ValidationError
from datetime import timedelta , datetime
from apps.common.models  import Contratos, Entidadessegsocial , Diagnosticosenfermedades , Incapacidades
from django.urls import reverse
import os
from django.core.cache import cache
from django.db import models
from dateutil.relativedelta import relativedelta


def get_diagnostico_choices():
    return cache.get_or_set('diagnostico_choices', lambda: [
        ('', '----------')
    ] + list(Diagnosticosenfermedades.objects
        .order_by('coddiagnostico')
        .values_list('coddiagnostico', 'diagnostico')
        .iterator()
    ), 60 * 60)  # Cache por 1 hora


def validate_pdf_file(value):
    # Verificar que el archivo sea un PDF
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Solo se permiten archivos en formato PDF.")

    # Verificar el tamaño del archivo (máx. 5 MB)
    max_size = 5 * 1024 * 1024  # 5MB en bytes
    if value.size > max_size:
        raise ValidationError("El tamaño máximo permitido es 5 MB.")

    # Verificar que el nombre no contenga caracteres especiales
    if not value.name.replace(".", "").replace("_", "").isalnum():
        raise ValidationError("El nombre del archivo no debe contener caracteres especiales.")

class DisabilitiesForm(forms.Form):
    
    def clean(self):
        incapa = []
        # Llama primero al clean() del padre para asegurar que los datos del formulario
        # hayan sido limpiados (convertidos al tipo correcto, etc.)
        cleaned_data = super().clean()

        # Obtenemos los valores necesarios del formulario
        contrato = cleaned_data.get("contract")      # Contrato asociado a la incapacidad
        fechainicial = cleaned_data.get("initial_date")  # Fecha inicial de la incapacidad
        dias = cleaned_data.get("incapacity_days")                # Duración de la incapacidad en días

            
        # Solo validamos si los tres datos requeridos están presentes
        if contrato and fechainicial and dias:
            # Asegurarse de que fechainicial sea una fecha (por si viene como texto)
            if isinstance(fechainicial, str):
                fechainicial = datetime.strptime(fechainicial, "%Y-%m-%d").date()

            # Convertir dias a entero si es necesario
            fechafinal = fechainicial + timedelta(days=int(dias))

             # Ampliar el rango de búsqueda a un mes antes y un mes después
            fecha_inicio_busqueda = fechainicial - relativedelta(months=1)
            fecha_fin_busqueda = fechainicial + relativedelta(months=1)

            overlapping = Incapacidades.objects.filter(
                idcontrato=contrato,
                fechainicial__gte=fecha_inicio_busqueda,
                fechainicial__lte=fecha_fin_busqueda
            )

            
            for data in overlapping:
                data_fechafinal = data.fechainicial + timedelta(days=int(data.dias))

                # Aquí validamos si hay cruce real de fechas
                if fechainicial <= data_fechafinal and fechafinal >= data.fechainicial:
                    self.add_error('initial_date', 'Ya existe una incapacidad que se cruza con este nuevo rango de fechas.')
                    break  # Ya con una sola basta para mostrar el error
                            

        return cleaned_data
    
    
        
    origin = forms.ChoiceField(choices=[('', '----------'),('EPS1', 'Enfermedad General - Común'), ('ARL', 'Profesional - Acc. Trabajo'), ('EPS2', 'Maternidad - Paternidad')], label="Origen", widget=forms.Select(attrs={'class': 'form-select'}))
    #entity = forms.ModelChoiceField(queryset=Entidadessegsocial.objects.none(), label="Entidad", widget=forms.Select(attrs={'class': 'form-select'}))
    
    extension = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')],initial='0', label="Prórroga", widget=forms.Select(attrs={'class': 'form-select'}))
    #initial_date = forms.DateField(label="Fecha Inicial de la Incapacidad", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    initial_date = forms.CharField(
        label='Fecha de Inicio',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Seleccione una fecha',
            'id': 'kt_daterangepicker_1'
        })
    )
    
    incapacity_days = forms.DecimalField(label="Días de Incapacidad", 
                                        max_digits=10, 
                                        decimal_places=2, 
                                        initial=0, 
                                        min_value=0,   
                                        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    end_date  = forms.CharField(
        label="Fin de la Incapacidad",
        required=False ,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'kt_daterangepicker_2' 
        })
    )
    

    #image = forms.ImageField(label="Imagen",required=False , widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    pdf_file = forms.FileField(
        label="Subir archivo PDF",
        validators=[validate_pdf_file],
        required=False ,
        help_text="Solo archivos PDF. Tamaño máximo: 5MB."
    )
    
    
    def __init__(self, *args, **kwargs):
        # Obtener la variable externa pasada al formulario
        idempresa = kwargs.pop('idempresa', None)
        
        super().__init__(*args, **kwargs)
        self.fields['entity'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['codigo'], f"{item['entidad']}")
                for item in Entidadessegsocial.objects.filter( tipoentidad__in=['EPS', 'ARL'])
                .order_by('codigo')  # Aplica el orden antes de hacer el slice
                .values('codigo', 'entidad')
            ],
            label="Entidad" , 
        )

        
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__pnombre']} - {item['cargo__nombrecargo']} - Contrato #{item['idcontrato']} ")
                for item in Contratos.objects.filter(estadocontrato=1 ,  id_empresa = idempresa ).exclude( tipocontrato__idtipocontrato__in = [5,6] )
                .order_by('idempleado__papellido')  # Aplica el orden antes de hacer el slice
                .values('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato','cargo__nombrecargo')
            ],
            label="Contrato" , 
        )

        self.fields['diagnosis_code'] = forms.ChoiceField(
            choices=[(cod, f"{cod} - {desc}") for cod, desc in get_diagnostico_choices()],
            label="Código de Incapacidad"
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_disablities'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('companies:disabilities_modal'),
            'up-accept-location': reverse('companies:disabilities'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
        
        
        
        for field_name in ['entity', 'contract', 'diagnosis_code']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    
                })
        
        for field_name in [ 'origin','extension']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    'data-hide-search': 'true' ,
                })
                
                
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('origin', css_class=' form-group col-md-6 mb-3'),
                Column('entity', css_class=' form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('initial_date', css_class=' form-group col-md-4 mb-3'),
                Column('incapacity_days', css_class=' form-group col-md-4 mb-3'),
                Column('end_date', css_class=' form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('diagnosis_code', css_class=' form-group col-md-8 mb-3'),
                
                Column('extension', css_class=' form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('pdf_file', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            
        )
    
    


class DisabilitiesEditForm(forms.Form):
    
    def clean(self):
        incapa = []
        # Llama primero al clean() del padre para asegurar que los datos del formulario
        # hayan sido limpiados (convertidos al tipo correcto, etc.)
        cleaned_data = super().clean()

        # Obtenemos los valores necesarios del formulario
        contrato = cleaned_data.get("contract")      # Contrato asociado a la incapacidad
        fechainicial = cleaned_data.get("initial_date")  # Fecha inicial de la incapacidad
        dias = cleaned_data.get("incapacity_days")                # Duración de la incapacidad en días

            
        # Solo validamos si los tres datos requeridos están presentes
        if contrato and fechainicial and dias:
            # Asegurarse de que fechainicial sea una fecha (por si viene como texto)
            if isinstance(fechainicial, str):
                fechainicial = datetime.strptime(fechainicial, "%Y-%m-%d").date()

            # Convertir dias a entero si es necesario
            fechafinal = fechainicial + timedelta(days=int(dias))

             # Ampliar el rango de búsqueda a un mes antes y un mes después
            fecha_inicio_busqueda = fechainicial - relativedelta(months=1)
            fecha_fin_busqueda = fechainicial + relativedelta(months=1)

            overlapping = Incapacidades.objects.filter(
                idcontrato=contrato,
                fechainicial__gte=fecha_inicio_busqueda,
                fechainicial__lte=fecha_fin_busqueda
            )

            
            for data in overlapping:
                data_fechafinal = data.fechainicial + timedelta(days=int(data.dias))

                # Aquí validamos si hay cruce real de fechas
                if fechainicial <= data_fechafinal and fechafinal >= data.fechainicial:
                    self.add_error('initial_date', 'Ya existe una incapacidad que se cruza con este nuevo rango de fechas.')
                    break  # Ya con una sola basta para mostrar el error
                            

        return cleaned_data
    
    
        
    origin = forms.ChoiceField(choices=[('', '----------'),('EPS1', 'Enfermedad General - Común'), ('ARL', 'Profesional - Acc. Trabajo'), ('EPS2', 'Maternidad - Paternidad')], label="Origen",required=False , widget=forms.Select(attrs={'class': 'form-select'}))
    #entity = forms.ModelChoiceField(queryset=Entidadessegsocial.objects.none(), label="Entidad", widget=forms.Select(attrs={'class': 'form-select'}))
    
    extension = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')],initial='0', label="Prórroga",required=False , widget=forms.Select(attrs={'class': 'form-select'}))
    #initial_date = forms.DateField(label="Fecha Inicial de la Incapacidad", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    initial_date = forms.CharField(
        label='Fecha de Inicio',
        required=False ,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Seleccione una fecha',
            'id': 'kt_daterangepicker_1'
        })
    )
    
    incapacity_days = forms.DecimalField(label="Días de Incapacidad", 
                                        max_digits=10, 
                                        decimal_places=2, 
                                        initial=0, 
                                        required=False ,
                                        min_value=0,   
                                        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    end_date  = forms.CharField(
        label="Fin de la Incapacidad",
        required=False ,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'kt_daterangepicker_2' 
        })
    )
    

    #image = forms.ImageField(label="Imagen",required=False , widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    pdf_file = forms.FileField(
        label="Subir archivo PDF",
        validators=[validate_pdf_file],
        required=False ,
        help_text="Solo archivos PDF. Tamaño máximo: 5MB."
    )
    
    
    def __init__(self, *args, **kwargs):
        
        # Obtener la variable externa pasada al formulario
        idempresa = kwargs.pop('idempresa', None)
        id = kwargs.pop('id', None)
        
        super().__init__(*args, **kwargs)
        self.fields['entity'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['codigo'], f"{item['entidad']}")
                for item in Entidadessegsocial.objects.filter( tipoentidad__in=['EPS', 'ARL'])
                .order_by('codigo')  # Aplica el orden antes de hacer el slice
                .values('codigo', 'entidad')
            ],
            required=False ,
            label="Entidad" , 
        )

        
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__pnombre']} - {item['cargo__nombrecargo']} - Contrato #{item['idcontrato']} ")
                for item in Contratos.objects.filter(estadocontrato=1 ,  id_empresa = idempresa ).exclude( tipocontrato__idtipocontrato__in = [5,6] )
                .order_by('idempleado__papellido')  # Aplica el orden antes de hacer el slice
                .values('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato','cargo__nombrecargo')
            ],
            required=False ,
            label="Contrato" , 
        )

        self.fields['diagnosis_code'] = forms.ChoiceField(
            choices=[(cod, f"{cod} - {desc}") for cod, desc in get_diagnostico_choices()],
            label="Código de Incapacidad"
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_disablities'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'up-target': '#modal-content-edit',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('companies:disabilities_modal_edit',kwargs={'id': id} ),
            'up-accept-location': reverse('companies:disabilities'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
        
        
        
        for field_name in ['entity', 'contract', 'diagnosis_code']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    
                })
        
        for field_name in [ 'origin','extension']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    'data-hide-search': 'true' ,
                })
                
                
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('origin', css_class=' form-group col-md-6 mb-3'),
                Column('entity', css_class=' form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('initial_date', css_class=' form-group col-md-4 mb-3'),
                Column('incapacity_days', css_class=' form-group col-md-4 mb-3'),
                Column('end_date', css_class=' form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('diagnosis_code', css_class=' form-group col-md-8 mb-3'),
                
                Column('extension', css_class=' form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('pdf_file', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            
        )
    
    
    