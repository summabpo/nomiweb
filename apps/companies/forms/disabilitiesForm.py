from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.companies.models  import Contratos,Entidadessegsocial ,Diagnosticosenfermedades

class DisabilitiesForm(forms.Form):
    origin = forms.ChoiceField(choices=[('', '----------'),('EG', 'Enfermedad General - Común'), ('AT', 'Profesional - Acc. Trabajo'), ('MP', 'Maternidad - Paternidad')], label="Origen", widget=forms.Select(attrs={'class': 'form-select'}))
    #entity = forms.ModelChoiceField(queryset=Entidadessegsocial.objects.none(), label="Entidad", widget=forms.Select(attrs={'class': 'form-select'}))
    
    extension = forms.ChoiceField(choices=[('', '-----'),('1', 'Sí'), ('0', 'No')], label="Prórroga", widget=forms.Select(attrs={'class': 'form-select'}))
    #initial_date = forms.DateField(label="Fecha Inicial de la Incapacidad", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    initial_date = forms.CharField(
        label='Fecha Inicial de la Incapacidad',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Pick date range',
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pick date range',
            'id': 'kt_daterangepicker_2' 
        })
    )
    

    
    previous_month_ibc = forms.DecimalField(
        label="IBC Mes Anterior", 
        max_digits=10, 
        decimal_places=2, 
        initial=0.00, 
        min_value=0,   
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    image = forms.ImageField(label="Imagen",required=False , widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entity'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['codigo'], f"{item['entidad']}")
                for item in Entidadessegsocial.objects.filter( tipoentidad__in=['EPS', 'ERL'])
                .order_by('codigo')  # Aplica el orden antes de hacer el slice
                .values('codigo', 'entidad')
            ],
            label="Entidad" , 
        )

        
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__sapellido']} {item['idempleado__pnombre']} {item['idempleado__snombre']} - {item['idcontrato']}")
                for item in Contratos.objects.filter(estadocontrato=1)
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
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'
        
        self.fields['entity'].widget.attrs.update({
            'data-control': 'select2',
            'data-dropdown-parent': '#kt_modal_1',
            'class': 'form-select',
            
        })
        
        self.fields['contract'].widget.attrs.update({
            'data-control': 'select2',
            'data-dropdown-parent': '#kt_modal_1',
            'class': 'form-select',
            
        })
        
        self.fields['origin'].widget.attrs.update({
            'data-control': 'select2',
            'data-dropdown-parent': '#kt_modal_1',
            'class': 'form-select',
            'data-hide-search': 'true' ,
            
        })
        
        self.fields['diagnosis_code'].widget.attrs.update({
            'data-control': 'select2',
            'data-dropdown-parent': '#kt_modal_1',
            'class': 'form-select',
            
            
        })
        
        self.fields['extension'].widget.attrs.update({
            'data-control': 'select2',
            'data-dropdown-parent': '#kt_modal_1',
            'class': 'form-select',
            'data-hide-search': 'true' ,
        })
        
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('entity', css_class=' form-group col-md-6 mb-3'),
                Column('origin', css_class=' form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('initial_date', css_class=' form-group col-md-6 mb-3'),
                Column('end_date', css_class=' form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('diagnosis_code', css_class=' form-group col-md-6 mb-3'),
                Column('incapacity_days', css_class=' form-group col-md-4 mb-3'),
                Column('extension', css_class=' form-group col-md-2 mb-3'),
                css_class='row'
            ),
            Row(
                Column('previous_month_ibc', css_class=' form-group col-md-6 mb-3'),
                Column('image', css_class=' form-group col-md-6 mb-3'),
                css_class='row'
            ),
            
        )
    