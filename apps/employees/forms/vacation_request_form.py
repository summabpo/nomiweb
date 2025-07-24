from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Contratos, Tipoavacaus
from django.urls import reverse

class EmpVacacionesForm(forms.Form):
    idcontrato = forms.ChoiceField(
        choices=[],
        label="Contrato",
        widget=forms.Select(attrs={
            'data-control': 'select2',
            'class': 'form-select',
        })
    )
    tipovac = forms.ChoiceField(
        choices=[('', '----------')] + [(nomina.idvac, nomina.nombrevacaus) for nomina in Tipoavacaus.objects.exclude(idvac=5).order_by('idvac')],
        label="Tipo de Solicitud",
        required=False,
        widget=forms.Select(attrs={
            'id': 'tipovac', 
            'data-control': 'select2',
            'data-tags': 'true',
            'class': 'form-select',
            'data-hide-search': 'true'
        })
    )
    fechainicialvac = forms.DateField(
        label='Fecha Inicial',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fechafinalvac = forms.DateField(
        label='Fecha Final',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
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
        edit =  kwargs.pop('edit', False)
        algun_id = kwargs.pop('algun_id',None)
        super(EmpVacacionesForm, self).__init__(*args, **kwargs)

        contratos_qs = Contratos.objects.filter(idempleado=idempleado, estadocontrato=1).order_by('idcontrato')

        self.fields['idcontrato'].choices = [('', '----------')] + [
            (contrato.idcontrato, f"{contrato.cargo} - {contrato.fechainiciocontrato.strftime('%d/%m/%Y')}")
            for contrato in contratos_qs
        ]

        # 👉 Selección automática si hay un solo contrato
        if contratos_qs.count() == 1:
            self.initial['idcontrato'] = contratos_qs.first().idcontrato

        self.fields['idcontrato'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true',
            'class': 'form-select',
            'data-placeholder': 'Seleccione un Contrato',
        })
    
        
        # Configuración de Crispy Forms
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_vacaciones'
        self.helper.enctype = 'multipart/form-data'
        
        if edit : 
            self.helper.attrs.update({
                'up-target': '#modal-content',
                'up-mode': 'replace',
                'up-layer': 'current',  # Clave para resolver el error
                'up-submit': reverse('employees:vacation_request_edit', kwargs={'id': algun_id}),
                'up-accept-location': reverse('employees:vacation_request_edit', kwargs={'id': algun_id}),
                'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
            })
        else : 
            self.helper.attrs.update({
                'up-target': '#modal-content',
                'up-mode': 'replace',
                'up-layer': 'current',  # Clave para resolver el error
                'up-submit': reverse('employees:vacation_request_add' ),
                'up-accept-location': reverse('employees:vacation_request_add'),
                'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
            })
        
        self.helper.layout = Layout(
            Row(
                Column('idcontrato', css_class='col-md-6 mb-3'),
                Column('tipovac', css_class='col-md-6 mb-3'),
            ),
            Row(
                Column('fechainicialvac', css_class='col-md-4 mb-3', css_id='fechainicialvac-column'),
                Column('fechafinalvac', css_class='col-md-4 mb-3', css_id='fechafinalvac-column'),
                Column('cuentasabados', css_class='col-md-4 mb-3', id='cuentasabados-column'),
            ),
            Row(
                Column('diasvac', css_class='col-md-12 mb-3', id='diasvac-column'),
            ),            
            Row(
                Column('comentarios', css_class='col-md-12 mb-3'),
            ),
        )
