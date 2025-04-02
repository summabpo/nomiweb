from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.common.models  import Contratos,Entidadessegsocial ,Diagnosticosenfermedades
from django.urls import reverse


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
    

    image = forms.ImageField(label="Imagen",required=False , widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    
    def __init__(self, *args, **kwargs):
        # Obtener la variable externa pasada al formulario
        idempresa = kwargs.pop('idempresa', None)
        dropdown_parent = kwargs.pop('dropdown_parent', '#kt_modal_1')
        select2_ids = kwargs.pop('select2_ids', {})
        
        super().__init__(*args, **kwargs)
        self.fields['entity'] = forms.ChoiceField(
            choices=[('', '----------')],
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
        self.helper.form_action = reverse('companies:disabilities_modal') 
        
        for field_name in ['entity', 'contract', 'diagnosis_code']:
            field_id = select2_ids.get(field_name, f'{field_name}_{dropdown_parent.strip("#")}')
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    'id': field_id,
                })
        
        for field_name in [ 'origin','extension']:
            field_id = select2_ids.get(field_name, f'{field_name}_{dropdown_parent.strip("#")}')
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                    'data-hide-search': 'true' ,
                    'id': field_id,
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
                Column('image', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            
        )
    
    
    