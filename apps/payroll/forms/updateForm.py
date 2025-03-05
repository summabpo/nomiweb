from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Hidden
from apps.common.models import Conceptosdenomina
from django.urls import reverse_lazy

class UpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        id_empresa = kwargs.pop('id_empresa', None)
        id_payroll = kwargs.pop('id_payroll', None)
        super().__init__(*args, **kwargs)
        
        id = id_payroll.replace("old-", "").replace("new-", "")
        # Campo oculto para id_payroll
        self.fields['id'] = forms.CharField(
            initial=id_payroll,
            widget=forms.HiddenInput(attrs={
                'id': 'id_payroll',  # Opcional: puedes personalizar el id del campo
            })
        )
        
        # Definir los campos con los atributos personalizados
        self.fields['concept_quantity'] = forms.IntegerField(
            required=False,
            label="",
            widget=forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'id': f"{id_payroll}-quantity", 
                'name': f"{id_payroll}-quantity",
                'hx-get': reverse_lazy('payroll:payroll_concept', kwargs={'data': id_payroll} ),
                'hx-params': "payroll_concept,concept_quantity",
                'hx-trigger': 'keyup[target.value.length > 0]', 
                'hx-on':"htmx:afterRequest: actualizarCampos(event.detail.response)",
            })
        )
        
        self.fields['concept_value'] = forms.DecimalField(
            required=False,
            label="",
            max_digits=10,
            decimal_places=2,
            widget=forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'id': f"{id_payroll}-value", 
                'name': f"{id_payroll}-value",
            })
        )
        
        self.fields['payroll_concept'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idconcepto'], f"{item['codigo']} - {item['nombreconcepto']}")
                for item in Conceptosdenomina.objects.filter(id_empresa_id=id_empresa)
                .order_by('codigo')
                .values('idconcepto', 'nombreconcepto', 'codigo')
            ],
            
            label="",
            widget=forms.Select(attrs={
                'id': f"{id_payroll}-concept", 
                'name': f"{id_payroll}-concept",
                'class': 'form-select form-select-sm',
                'data-control': 'select2',
                'data-dropdown-parent': "#conceptsModal",
                
                
            })
        )
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.enctype = False
        
        # Definir el layout del formulario
        self.helper.layout = Layout(
            Hidden('id', id_payroll),  # Campo oculto para id_payroll
            Row(
                Column('payroll_concept', css_class='input-group-sm col-md-5'),
                Column('concept_quantity', css_class='form-group col-md-2'),
                Column('concept_value', css_class='form-group col-md-3'),
                Column(
                    Submit('delete', 'Eliminar', css_class='btn btn-danger btn-sm',
                            **{'hx-delete': reverse_lazy('payroll:delete_payroll', kwargs={'id': id}),
                                'hx-confirm': '¿Estás seguro de eliminar este concepto?',
                                'hx-swap':"outerHTML swap:1s"}),
                    css_class='col-md-2'
                ),
                css_class='row'
            )
        )