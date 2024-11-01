from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column,Button , HTML
from apps.common.models import Costos,Sedes,Contratosemp,Anos

# Definir los choices para los años (2015-2024)
AÑO_CHOICES = [('', '--------------')] + [(str(year), str(year)) for year in range(2024, 2014, -1)]


# Definir los choices para los meses
MES_CHOICES = [
    ('', '--------------'),
    ('ENERO', 'Enero'),
    ('FEBRERO', 'Febrero'),
    ('MARZO', 'Marzo'),
    ('ABRIL', 'Abril'),
    ('MAYO', 'Mayo'),
    ('JUNIO', 'Junio'),
    ('JULIO', 'Julio'),
    ('AGOSTO', 'Agosto'),
    ('SEPTIEMBRE', 'Septiembre'),
    ('OCTUBRE', 'Octubre'),
    ('NOVIEMBRE', 'Noviembre'),
    ('DICIEMBRE', 'Diciembre')
]



class ReportFilterForm(forms.Form):
    # start_date = forms.DateField(
    #     required=True,
    #     label='Fecha Inicial',
    #     widget=forms.DateInput(attrs={'type': 'date'})
    # )
    # end_date = forms.DateField(
    #     required=True,
    #     label='Fecha Final',
    #     widget=forms.DateInput(attrs={'type': 'date'})
    # )
    
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

    
    
    # Cambiar los campos a ChoiceField
    
    mst_init = forms.ChoiceField(
        choices=MES_CHOICES,
        required=True,
        label='Mes Inicial',
        widget=forms.Select(attrs={'class': 'form-control'}))
    
    
    
    mst_end = forms.ChoiceField(
        choices=MES_CHOICES, 
        required=True,
        label='Mes Final',
        widget=forms.Select(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        year_init = cleaned_data.get('year_init')
        mst_init = cleaned_data.get('mst_init')
        year_end = cleaned_data.get('year_end')
        mst_end = cleaned_data.get('mst_end')

        # Validación básica para asegurarse de que el año inicial no sea mayor que el año final
        if year_init and year_end and int(year_init) > int(year_end):
            raise forms.ValidationError('El año inicial no puede ser mayor que el año final.')

        # Si los años son iguales, validamos los meses
        if year_init == year_end:
            months_order = [choice[0] for choice in MES_CHOICES if choice[0]]  # Obtenemos el orden de los meses
            if months_order.index(mst_init) > months_order.index(mst_end):
                raise forms.ValidationError('El mes inicial no puede ser mayor que el mes final en el mismo año.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        super().__init__(*args, **kwargs)        
        # Actualizar choices dinámicamente
        self.fields['employee'].choices = [('', '----------')] + [(idempleado, f"{papellido} {sapellido} {pnombre} {snombre} ") for idempleado, pnombre, snombre, papellido, sapellido in Contratosemp.objects.filter(id_empresa__idempresa = idempresa ).values_list('idempleado', 'pnombre', 'snombre', 'papellido', 'sapellido').order_by('papellido')]
        self.fields['cost_center'].choices = [('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.all()]
        self.fields['city'].choices = [('', '----------')] + [(ciudad.idsede, f"{ciudad.nombresede}") for ciudad in Sedes.objects.all().order_by('nombresede')]

        self.fields['year_init'] = forms.ChoiceField(
            choices=[('', '----------')] + [(anos.idano,anos.ano   ) for anos in Anos.objects.all().order_by('ano')], 
            label='Año Inicial' , 
            required=True ,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                }),
            )
        
        self.fields['year_end'] = forms.ChoiceField(
            choices=[('', '----------')] + [(anos.idano,anos.ano   ) for anos in Anos.objects.all().order_by('ano')], 
            label='Año Final' , 
            required=True ,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                }),
            )

        
        self.fields['mst_init'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
        
        
        self.fields['mst_end'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
        
        

        self.helper = FormHelper()
        self.helper.form_id = 'Filter_report'
        self.helper.layout = Layout(
            Row(
                HTML('<div class="text-gray-900">Los campos marcados con un <span class="text-danger">*</span> son obligatorios.</div><br>'),
                css_class='row'
            ),
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
                HTML('<div class="separator border-3 my-5"></div>'),
                css_class='row'
            ),
            Row(
                Column('year_init', css_class='form-group mb-0'),
                Column('mst_init', css_class='form-group mb-0'),
                Column('year_end', css_class='form-group mb-0'),
                Column('mst_end', css_class='form-group mb-0'),
                css_class='row'
            ),
            Row(
                HTML('<div class="separator border-3 my-5"></div>'),
                css_class='row'
            ),
            
            # Row(
            #     Column('start_date', css_class='form-group mb-0'),
            #     Column('end_date', css_class='form-group mb-0'),
            #     css_class='row'
            # year_init = forms.ChoiceField(choices=AÑO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
            # mst_init = forms.ChoiceField(choices=MES_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
            
            # year_end = forms.ChoiceField(choices=AÑO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
            # mst_end = forms.ChoiceField(choices=MES_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
            # ),
            Row(
                Column(
                    Submit('submit', 'Filtrar', css_class='btn btn-light-info w-100'),  # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                Column(
                    Button('button', 'Limpiar filtrado', css_class='btn btn-light-primary w-100', id='my-custom-button'), # 100% ancho de la columna
                    css_class='col-md-6'  # Ancho especificado
                ),
                css_class='row'
            ),
            
        )
