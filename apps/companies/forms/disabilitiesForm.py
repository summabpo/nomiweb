from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.companies.models  import Contratos,Entidadessegsocial ,Diagnosticosenfermedades

class DisabilitiesForm(forms.Form):
    # contract = forms.ModelChoiceField(queryset=Contratos.objects.all(), label="Contrato", widget=forms.Select(attrs={'class': 'form-select'}))
    # contract = forms.ModelChoiceField(queryset=Contratos.objects.all(), label="Contrato", widget=forms.Select(attrs={'class': 'form-select'}))
    # origin = forms.ChoiceField(choices=[('EG', 'Enfermedad General - Común'), ('AT', 'Profesional - Acc. Trabajo'), ('MP', 'Maternidad - Paternidad')], label="Origen", widget=forms.Select(attrs={'class': 'form-select'}))
    # entity = forms.ModelChoiceField(queryset=Entidadessegsocial.objects.none(), label="Entidad", widget=forms.Select(attrs={'class': 'form-select'}))
    # diagnosis_code_prefix = forms.CharField(max_length=3, label="Código Diagnóstico - Prefijo", widget=forms.TextInput(attrs={'class': 'form-control'}))
    # diagnosis_code = forms.ModelChoiceField(queryset=Diagnosticosenfermedades.objects.none(), label="Código Diagnóstico", widget=forms.Select(attrs={'class': 'form-select'}))
    # extension = forms.ChoiceField(choices=[('Yes', 'Sí'), ('No', 'No')], label="Prórroga", widget=forms.Select(attrs={'class': 'form-select'}))
    # initial_date = forms.DateField(label="Fecha Inicial de la Incapacidad", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    # incapacity_days = forms.IntegerField(label="Días de Incapacidad", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # end_date = forms.DateField(label="Fin de la Incapacidad", required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    # previous_month_ibc = forms.DecimalField(label="IBC Mes Anterior", max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # image = forms.ImageField(label="Imagen", widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        initial_date = cleaned_data.get('initial_date')
        incapacity_days = cleaned_data.get('incapacity_days')

        if initial_date and incapacity_days:
            end_date = initial_date + timedelta(days=incapacity_days)
            cleaned_data['end_date'] = end_date
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__sapellido']} {item['idempleado__pnombre']} {item['idempleado__snombre']} - {item['idcontrato']}")
                for item in Contratos.objects.filter(estadocontrato=1)
                .order_by('idempleado__papellido')[:20]  # Aplica el orden antes de hacer el slice
                .values('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato')
            ]
        )

        
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'
        
        self.fields['contract'].widget.attrs.update({
            'data-control': 'select2',
            'data-dropdown-parent': '#kt_modal_1,#kt_modal_2',
            'class': 'form-select',
            
        })
        
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class='mb-10'),
                
                css_class='row'
            ),
            
        )
    