from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.common.models  import Contratos,Entidadessegsocial ,Diagnosticosenfermedades
from django.urls import reverse
import os

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
    origin = forms.ChoiceField(choices=[('', '----------'),('EPS1', 'Enfermedad General - Común'), ('ARL', 'Profesional - Acc. Trabajo'), ('EPS2', 'Maternidad - Paternidad')], label="Origen", widget=forms.Select(attrs={'class': 'form-select'}))
    #entity = forms.ModelChoiceField(queryset=Entidadessegsocial.objects.none(), label="Entidad", widget=forms.Select(attrs={'class': 'form-select'}))
    
    extension = forms.ChoiceField(choices=[('', '-----'),('1', 'Sí'), ('0', 'No')], label="Prórroga", widget=forms.Select(attrs={'class': 'form-select'}))
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
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__pnombre']} - {item['idcontrato']}")
                for item in Contratos.objects.filter(estadocontrato=1 , id_empresa = idempresa )
                .order_by('idempleado__papellido')  # Aplica el orden antes de hacer el slice
                .values('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato')
            ],
            label="Contrato" , 
        )

        self.fields['diagnosis_code'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['coddiagnostico'], f" {item['coddiagnostico']} - {item['diagnostico']} ")
                for item in Diagnosticosenfermedades.objects.all()
                .order_by('coddiagnostico')  # Aplica el orden antes de hacer el slice
                .values('coddiagnostico', 'diagnostico')
            ],
            label="Codigo de Incapacidad" , 
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
    
    
    