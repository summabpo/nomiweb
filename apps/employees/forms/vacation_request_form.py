from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Contratos, Tipoavacaus

class EmpVacacionesForm(forms.Form):
    idcontrato = forms.ChoiceField(
        choices=[],
        label="Contrato",
        required=False,
        widget=forms.Select(attrs={
            'data-control': 'select2',
            'data-dropdown-parent': '#kt_modal_1',
            'class': 'form-select',
        })
    )
    tipovac = forms.ChoiceField(
        choices=[('', '----------')] + [(nomina.idvac, nomina.nombrevacaus) for nomina in Tipoavacaus.objects.exclude(idvac=5).order_by('idvac')],
        label="Tipo de Solicitud",
        required=False,
        widget=forms.Select(attrs={
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': 'true',
            'id': 'tipovac-select',
            'data-dropdown-parent': "#kt_modal_1",
        })
    )
    fechainicialvac = forms.DateField(
        label='Fecha Inicial',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fechainicialvac-field'})
    )
    fechafinalvac = forms.DateField(
        label='Fecha Final',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fechafinalvac-field'})
    )
    cuentasabados = forms.ChoiceField(
        choices=[('', '----------'), (1, 'Sí'), (0, 'No')],
        label="Cuenta Sábados",
        required=False,
        widget=forms.Select(attrs={
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': 'true',
            'data-dropdown-parent': "#kt_modal_1",
        })
    )
    diasvac = forms.IntegerField(
        label='Dias a Compensar',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'diasvac-field'})
    )
    comentarios = forms.CharField(
        label='Comentarios',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        idempleado = kwargs.pop('idempleado', None)
        dropdown_parent = kwargs.pop('dropdown_parent', '#kt_modal_1')
        select2_ids = kwargs.pop('select2_ids', {})
        
        super(EmpVacacionesForm, self).__init__(*args, **kwargs)
        
        # Actualizar las opciones de 'idcontrato' dinámicamente
        self.fields['idcontrato'].choices = [('', '----------')] + [
            (contrato.idcontrato, f"{contrato.cargo} - {contrato.fechainiciocontrato.strftime('%d/%m/%Y')}")
            for contrato in Contratos.objects.filter(idempleado=idempleado, estadocontrato=1).order_by('idcontrato')
        ]

        for field_name in ['idcontrato', 'cuentasabados', 'tipovac','idcontrato']:
            field_id = select2_ids.get(field_name, f'{field_name}_{dropdown_parent.strip("#")}')
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'data-dropdown-parent': dropdown_parent,
                    'class': 'form-select',
                    'id': field_id,
                })
        
        # Configuración de Crispy Forms
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_loans'
        self.helper.enctype = 'multipart/form-data'
        
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
