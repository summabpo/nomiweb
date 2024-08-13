from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.companies.models import Costos, Sedes, Contratosemp

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=True,
        label='Fecha Inicial',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=True,
        label='Fecha Final',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    employee = forms.ChoiceField(
        choices=[('', '----------')],
        label='Empleado',
        required=False,
        widget=forms.Select(attrs={'data-control': 'select2'})
    )
    
    cost_center = forms.ChoiceField(
        choices=[('', '----------')],
        label='Centro de Costos',
        required=False,
        widget=forms.Select(attrs={'data-control': 'select2'})
    )
    
    city = forms.ChoiceField(
        choices=[('', '----------')],
        label='Lugar de trabajo',
        required=False,
        widget=forms.Select(attrs={'data-control': 'select2'})
    )

    def clean(self):
        cleaned_data = super().clean()
        filled_fields_count = sum(1 for field in self.fields if cleaned_data.get(field))
        
        if filled_fields_count < 2:
            raise forms.ValidationError('Debe Seleccionar al menos dos campos.')
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        initial_data = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control'})
        
        # Actualizar choices dinámicamente
        self.fields['employee'].choices = [('', '----------')] + [(idempleado, f"{papellido} {sapellido} {pnombre} {snombre} ") for idempleado, pnombre, snombre, papellido, sapellido in Contratosemp.objects.values_list('idempleado', 'pnombre', 'snombre', 'papellido', 'sapellido').order_by('papellido')]
        self.fields['cost_center'].choices = [('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()]
        self.fields['city'].choices = [('', '----------')] + [(ciudad.idsede, f"{ciudad.nombresede}") for ciudad in Sedes.objects.all().order_by('nombresede')]

        # # Set initial values from kwargs if provided
        # self.fields['employee'].initial = initial_data.get('employee')
        # self.fields['cost_center'].initial = initial_data.get('cost_center')
        # self.fields['city'].initial = initial_data.get('city')
        # self.fields['start_date'].initial = initial_data.get('start_date')
        # self.fields['end_date'].initial = initial_data.get('end_date')

        self.helper = FormHelper()
        self.helper.form_id = 'Filter_report'
        self.helper.layout = Layout(
            Row(
                Column('employee', css_class='form-group mb-0'),
                Column('cost_center', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('city', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column('start_date', css_class='form-group mb-0'),
                Column('end_date', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                Column(
                    Submit('submit', 'Filtrar', css_class='btn btn-light-info w-100'),  # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                Column(
                    Submit('submit', 'Limpiar filtrado', css_class='btn btn-light-primary w-100'),  # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                css_class='row'
            )
        )
