from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from apps.common.models  import Conceptosdenomina
class UpdateForm(forms.Form):

    
    concept_quantity = forms.IntegerField(
        required=False,
        label="",
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'})
    )

    concept_value = forms.DecimalField(
        required=False,
        label="",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm '})
    )

    def __init__(self, *args, **kwargs):
        id_empresa = kwargs.pop('id_empresa', None) 
        id_payroll = kwargs.pop('id_payroll', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_payroll'
        self.helper.enctype = 'multipart/form-data'
        
        self.fields['payroll_concept'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idconcepto'], f"{item['nombreconcepto']} - {item['codigo']}")
                for item in Conceptosdenomina.objects.filter(id_empresa_id = id_empresa)
                .order_by('codigo')
                .values('idconcepto', 'nombreconcepto', 'codigo')
            ],
            label="",
            widget=forms.Select(attrs={
                'id': id_payroll, 
                'data-control': 'select2',
                'data-dropdown-parent': "#conceptsModal",
                'class': 'form-select form-select-sm'
            })
        )

        self.helper.layout = Layout(
            Row(
                Column('payroll_concept', css_class='input-group-sm  col-md-6'),
                Column('concept_quantity', css_class='form-group col-md-3'),
                Column('concept_value', css_class='form-group col-md-3'),
                css_class='row'
            )
        )
        
        

    

