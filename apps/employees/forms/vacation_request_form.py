from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import ModelForm
from apps.employees.models import EmpVacaciones, Contratos, Tipoavacaus

class EmpVacacionesForm(forms.ModelForm):
    class Meta:
        model = EmpVacaciones
        fields = ['idcontrato', 'tipovac', 'fechainicialvac', 'fechafinalvac', 'cuentasabados', 'comentarios']
        widgets = {
            'fechainicialvac': forms.DateInput(attrs={'type': 'date'}),
            'fechafinalvac': forms.DateInput(attrs={'type': 'date'}),
            'cuentasabados': forms.CheckboxInput(),
        }
    
    idcontrato = forms.ModelChoiceField(
        queryset=Contratos.objects.filter(idempleado=880, estadocontrato=1),
        label="Contrato",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione --------->",
    )
    tipovac = forms.ModelChoiceField(
        queryset=Tipoavacaus.objects.exclude(tipovac=5),
        label="Tipo de Vacación",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione --------->",
    )

    def __init__(self, *args, **kwargs):
        super(EmpVacacionesForm, self).__init__(*args, **kwargs)
        self.fields['idcontrato'].label_from_instance = self.label_from_contrato
        self.fields['tipovac'].label_from_instance = self.label_from_tipovac
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('idcontrato', css_class='form-group col-md-6 mb-0'),
                Column('tipovac', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('fechainicialvac', css_class='form-group col-md-6 mb-0'),
                Column('fechafinalvac', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('cuentasabados', css_class='form-group col-md-6 mb-0'),
                Column('comentarios', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Guardar', css_class='btn btn-primary')
        )

    def label_from_contrato(self, obj):
        return "{} - {}".format(obj.cargo, obj.fechainiciocontrato.strftime('%d/%m/%Y'))

    def label_from_tipovac(self, obj):
        return obj.nombrevacaus
