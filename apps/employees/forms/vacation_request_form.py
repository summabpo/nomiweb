from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import ModelForm
from apps.employees.models import EmpVacaciones, Contratos, Tipoavacaus

class EmpVacacionesForm(forms.ModelForm):
    class Meta:
        model = EmpVacaciones
        fields = ['idcontrato', 'tipovac', 'fechainicialvac', 'fechafinalvac', 'cuentasabados', 'diascalendario', 'comentarios']
        labels = {
            'fechainicialvac': 'Fecha Inicial',
            'fechafinalvac': 'Fecha Final',
            'comentarios': 'Comentarios',
            'diascalendario': 'Dias Calendario',
        }
        widgets = {
            'fechainicialvac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fechafinalvac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diascalendario': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    idcontrato = forms.ModelChoiceField(
        queryset=Contratos.objects.filter(idempleado=580, estadocontrato=1),
        label="Contrato",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione --------->",
    )
    tipovac = forms.ModelChoiceField(
        queryset=Tipoavacaus.objects.exclude(tipovac=5),
        label="Tipo de Solicitud",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione --------->",
    )
    cuentasabados = forms.ChoiceField(
        label="Cuenta Sábados",
        choices=[(1, 'Sí'), (0, 'No')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
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
                Column('fechainicialvac', css_class='col-md-6 mb-3'),
                Column('fechafinalvac', css_class='col-md-6 mb-3'),
            ),
            Row(
                Column('cuentasabados', css_class='col-md-6 mb-3'),
                Column('diascalendario', css_class='col-md-6 mb-3'),
                Column('comentarios', css_class='col-md-6 mb-3'),
            ),
            Submit('submit', 'Guardar',css_class='btn btn-light-info hover-elevate-up')
        )
        
    def label_from_contrato(self, obj):
        return f"{obj.cargo} - {obj.fechainiciocontrato.strftime('%d/%m/%Y')}"

    def label_from_tipovac(self, obj):
        return obj.nombrevacaus
