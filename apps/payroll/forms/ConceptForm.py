from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa , Contratos , Conceptosdenomina

TIPE_CHOICES = (
    ('', '-------------'),
    ('1', 'Mensual'),
    ('2', 'Quincenal'),
    ('3', 'Por Horas'),
    ('4', 'Primas'),
    ('5', 'Cesantías'),
    ('6', 'Adicional'),
    ('7', 'Vacaciones'),
    ('8', 'Liquidación'),
    ('9', 'Catorcenal'),
    ('10', 'Int. de Cesantías'),
    ('11', 'Semanal'),
)

class ConceptForm(forms.Form):


    idcontrato = forms.ChoiceField(
        label='Empleado',
        choices=TIPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    valor = forms.IntegerField(
        label='Valor',
        widget=forms.NumberInput(attrs={'placeholder': ''})
    )

    cantidad = forms.IntegerField(
        label='Cantidad',
        widget=forms.NumberInput(attrs={'placeholder': ''})
    )

    idconcepto = forms.ChoiceField(
        label='Conceptos',
        choices=TIPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
 

    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        # Obtener la variable externa pasada al formulario
        dropdown_parent = kwargs.pop('dropdown_parent', '#kt_modal_concept')
        select2_ids = kwargs.pop('select2_ids', {})


        super().__init__(*args, **kwargs)

        self.fields['idconcepto'].choices = [('', '----------')] + [(concepto.idconcepto, f"{concepto.nombreconcepto}") for concepto in Conceptosdenomina.objects.all()]
        self.fields['idcontrato'].choices = [('', '----------')] + [(contra.idcontrato, f"{contra.idempleado.papellido } {contra.idempleado.sapellido } {contra.idempleado.pnombre }") for contra in Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa) .order_by('idcontrato')]
        

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_payroll_concept'
        self.helper.enctype = 'multipart/form-data'


        for field_name in ['idconcepto', 'idcontrato']:
            field_id = select2_ids.get(field_name, f'{field_name}_{dropdown_parent.strip("#")}')
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'data-dropdown-parent': dropdown_parent,
                    'class': 'form-select',
                    'id': field_id,
                })


        self.helper.layout = Layout(
            Row(
                Column('idcontrato', css_class='form-group  col-md-12 mb-0'),
                css_class='row'
            ),
            
            Row(
                Column('idconcepto', css_class='form-group  col-md-6 mb-0'),
                Column('valor', css_class='form-group  col-md-3 mb-0'),
                Column('cantidad', css_class='form-group  col-md-3 mb-0'),
                css_class='row'
            ),
        )
