from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Anos



class FilterForm(forms.Form):
    # Definir los choices para los años (2015-2024)
    #AÑO_CHOICES = [('', '--------------')] + [(str(year), str(year)) for year in range(2024, 2014, -1)]

    
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
    
    # Cambiar los campos a ChoiceField
    #año = forms.ChoiceField(choices=AÑO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    mes = forms.ChoiceField(choices=MES_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['año'] = forms.ChoiceField(
            choices=[('', '----------')] + [(n.ano, n.ano) for n in Anos.objects.all().order_by('-ano')],
        )
        
        
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_estudiocandidato'
        self.helper.form_class = 'container'
        
        self.fields['año'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
        
        self.fields['mes'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
        
        self.helper.layout = Layout(
            Row(
                Column('año', css_class='form-group mb-0'),
                Column('mes', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Buscar' ,css_class='btn btn-light-success'),
        )


class FiltercompleteForm(forms.Form):
    # Definir los choices para los años (2015-2024)
    #AÑO_CHOICES = [('', '--------------')] + [(str(year), str(year)) for year in range(2024, 2014, -1)]

    
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
    
    liquidation__CHOICES = [
        ('', '--------------'),
        ('1', 'Pagos efectivamente hechos'),
        ('2', 'Calculando Salario al 100%'),
    ]
    
    # Cambiar los campos a ChoiceField
    #año = forms.ChoiceField(choices=AÑO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    mes = forms.ChoiceField(choices=MES_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    liquidation = forms.ChoiceField(choices=liquidation__CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['año'] = forms.ChoiceField(
            choices=[('', '----------')] + [(n.ano, n.ano) for n in Anos.objects.all().order_by('-ano')],
        )
        
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_estudiocandidato'
        self.helper.form_class = 'container'
        
        self.fields['año'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
        
        self.fields['mes'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
        
        self.fields['liquidation'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            
        })
        
        self.helper.layout = Layout(
            Row(
                Column('año', css_class='form-group mb-0'),
                Column('mes', css_class='form-group mb-0'),
                Column('liquidation', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Buscar' ,css_class='btn btn-light-success'),
        )
