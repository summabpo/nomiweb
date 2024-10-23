from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import ModelForm
from apps.common.models import EmpVacaciones, Contratos, Tipoavacaus

class EmpVacacionesForm(forms.ModelForm):
    class Meta:
        model = EmpVacaciones
        fields = ['idcontrato', 'tipovac', 'fechainicialvac', 'fechafinalvac', 'cuentasabados', 'diasvac', 'comentarios']
        labels = {
            'fechainicialvac': 'Fecha Inicial',
            'fechafinalvac': 'Fecha Final',
            'comentarios': 'Comentarios',
            'diasvac': 'Dias a Compensar',
        }
        widgets = {
            'fechainicialvac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fechainicialvac-field'}),
            'fechafinalvac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fechafinalvac-field'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diasvac': forms.NumberInput(attrs={'class': 'form-control', 'id': 'diasvac-field'}),
        }
    
    idcontrato = forms.ModelChoiceField(
        queryset=Contratos.objects.filter(idempleado=580, estadocontrato=1),
        label="Contrato",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione --------->",
    )
    tipovac = forms.ModelChoiceField(
        queryset=Tipoavacaus.objects.exclude(idvac=5),
        label="Tipo de Solicitud",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'tipovac-select'}),
        empty_label="Seleccione --------->",
    )
    cuentasabados = forms.ChoiceField(
        label="Cuenta Sábados",
        choices=[(1, 'Sí'), (0, 'No')],
        required=False,
        initial=0,
        
    )

    def __init__(self, *args, **kwargs):
        super(EmpVacacionesForm, self).__init__(*args, **kwargs)
        self.fields['idcontrato'].label_from_instance = self.label_from_contrato
        self.fields['tipovac'].label_from_instance = self.label_from_tipovac
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('idcontrato', css_class='col-md-6 mb-3'),
                Column('tipovac', css_class='col-md-6 mb-3'),
            ),
            Row(
                Column('fechainicialvac', css_class='col-md-6 mb-3', css_id='fechainicialvac-column'),
                Column('fechafinalvac', css_class='col-md-6 mb-3', css_id='fechafinalvac-column'),
            ),
            Row(
                Column('cuentasabados', css_class='col-md-6 mb-3', id='cuentasabados-column'),
                Column('diasvac', css_class='col-md-6 mb-3', id='diasvac-column'),
                Column('comentarios', css_class='col-md-6 mb-3'),
            ),
        )
        
    def label_from_contrato(self, obj):
        return f"{obj.cargo} - {obj.fechainiciocontrato.strftime('%d/%m/%Y')}"

    def label_from_tipovac(self, obj):
        return obj.nombrevacaus
    
    