from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models import Empresa , Contratos , Conceptosdenomina , NeSumatorias , Indicador
from django.urls import reverse

TIPE_CHOICES = (
    ('', ''),
    ('EPS', 'EPS'),
    ('ARL', 'ARL'),
    ('CCF', 'CCF'),
    ('AFP', 'AFP'),
    ('PARAFISCALES', 'Parafiscales'),
)

TIPE_CONCEPTS = (
    ('', ''),
    ('1', 'Ingreso'),
    ('2', 'Deducción'),
)

class BanksForm(forms.Form):
    nombanco = forms.CharField(
        label='Nombre del Banco',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del banco'})
    )
    codbanco = forms.IntegerField(
        label='Código del Banco',
        widget=forms.NumberInput(attrs={'placeholder': 'Ingrese el código del banco', 'class': 'form-control'})
    )
    codach = forms.IntegerField(
        label='Código ACH',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ingrese el código ACH', 'class': 'form-control'})
    )
    digchequeo = forms.IntegerField(
        label='Dígito de Chequeo',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ingrese el dígito de chequeo', 'class': 'form-control'})
    )
    nitbanco = forms.CharField(
        label='NIT del Banco',
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese el NIT ', 'class': 'form-control'})
    )
    tamcorriente = forms.IntegerField(
        label='Tamaño Cuenta Corriente',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ingrese el tamaño', 'class': 'form-control'})
    )
    tamahorro = forms.IntegerField(
        label='Tamaño Cuenta de Ahorro',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ingrese el tamaño', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'

        # Diseño del formulario con Crispy Forms
        self.helper.layout = Layout(
            Row(
                Column('nombanco', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
            Row(
                Column('codbanco', css_class='form-group col-md-4 mb-0'),
                Column('codach', css_class='form-group col-md-4 mb-0'),
                Column('digchequeo', css_class='form-group col-md-4 mb-0'),
                css_class='row'
            ),
            Row(
                Column('nitbanco', css_class='form-group col-md-4 mb-0'),
                Column('tamcorriente', css_class='form-group col-md-4 mb-0'),
                Column('tamahorro', css_class='form-group col-md-4 mb-0'),
                css_class='row'
            ),
        )


class EntitiesForm(forms.Form):
    codigo = forms.CharField(
        label='Código',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el código'})
    )
    nit = forms.CharField(
        label='NIT',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el NIT de la entidad'})
    )
    entidad = forms.CharField(
        label='Nombre de la Entidad',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre de la entidad'})
    )
    tipoentidad = forms.ChoiceField(
        label='Tipo de Entidad',
        choices=TIPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    codsgp = forms.CharField(
        label='Código SGP',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SGP'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['tipoentidad'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            'data-hide-search': 'true',
            'data-placeholder':'seleccione un tipo de entidad',
        })
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_entitis'
        self.helper.enctype = 'multipart/form-data'

        # Diseño del formulario con Crispy Forms
        self.helper.layout = Layout(
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('nit', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('entidad', css_class='form-group col-md-5 mb-0'),
                Column('tipoentidad', css_class='form-group col-md-5 mb-0'),
                Column('codsgp', css_class='form-group col-md-2 mb-0'),
                css_class='row'
            ),
        )



class HolidaysForm(forms.Form):
    fecha = forms.DateField(
        label='Fecha',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Seleccione la fecha'})
    )
    descripcion = forms.CharField(
        label='Descripción',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese una descripción breve'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'

        # Diseño del formulario con Crispy Forms
        self.helper.layout = Layout(
            Row(
                Column('fecha', css_class='form-group col-md-6 mb-0'),
                Column('descripcion', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            )
        )




class FixedForm(forms.Form):
    conceptofijo = forms.CharField(
        label='Concepto fijo',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el concepto fijo'})
    )
    valorfijo = forms.DecimalField(
        label='Valor fijo',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor fijo'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'

        # Diseño del formulario con Crispy Forms
        self.helper.layout = Layout(
            Row(
                Column('conceptofijo', css_class='form-group col-md-6 mb-0'),
                Column('valorfijo', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            )
        )
        
        
class AnnualForm(forms.Form):
    salariominimo = forms.DecimalField(
        label='Salario mínimo',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el salario mínimo'})
    )
    auxtransporte = forms.DecimalField(
        label='Auxilio de transporte',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el auxilio de transporte'})
    )
    uvt = forms.DecimalField(
        label='UVT',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el valor de la UVT'})
    )
    ano = forms.IntegerField(
        label='Año',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el año'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'

        # Diseño del formulario con Crispy Forms
        self.helper.layout = Layout(
            Row(
                Column('salariominimo', css_class='form-group col-md-6 mb-0'),
                Column('auxtransporte', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('uvt', css_class='form-group col-md-6 mb-0'),
                Column('ano', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            )
        )
        

class PayrollConceptsForm(forms.Form):
    nombreconcepto = forms.CharField(
        label='Nombre del Concepto',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del concepto'})
    )
    multiplicadorconcepto = forms.DecimalField(
        label='Multiplicador',
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el multiplicador'})
    )
    
    tipoconcepto = forms.ChoiceField(
        label='Tipo de Concepto',
        choices=TIPE_CONCEPTS,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Ingrese el tipo de concepto'})
    )
    
    formula = forms.CharField(
        label='Fórmula',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la fórmula'})
    )
    
    codigo = forms.IntegerField(
        label='Código',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el código'})
    )
    
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tipoconcepto'].widget.attrs.update({
            'data-control': 'select2',
            'data-hide-search': 'true' ,
            'class': 'form-select',
            'data-dropdown-parent': '#kt_modal_maintenance',
            'data-placeholder':'seleccione un tipo de concepto',
        })
        
        
        self.fields['grupo_dian'] = forms.ChoiceField(
            choices= [('', '----------')] +  [(concepto.ne_id, f"{concepto.campo}") for concepto in NeSumatorias.objects.all()], 
            label='Grupo DIAN' ,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
                'data-allow-clear' : "true"  , 
                'data-dropdown-parent': '#kt_modal_maintenance',
                'data-placeholder':'seleccione un grupo DIAN',
            }), 
            required=False )
        
        
        self.fields['indicador'] = forms.ChoiceField(
            choices= [(concepto.id, f"{concepto.nombre}") for concepto in Indicador.objects.all()], 
            label='Indicador' ,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-close-on-select':"false",
                'data-placeholder':'seleccione un Indicador',
                'data-allow-clear' : "true"  , 
                'multiple':"multiple" , 
                'data-dropdown-parent': '#kt_modal_maintenance',
            }))
        
        
        
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_concepts'
        self.helper.enctype = 'multipart/form-data'
        self.helper.form_action = reverse('payroll:concepts_add')

        # Diseño del formulario con Crispy Forms
        self.helper.layout = Layout(
            Row(
                Column('nombreconcepto', css_class='form-group col-md-4 mb-0'),
                Column('multiplicadorconcepto', css_class='form-group col-md-4 mb-0'),
                Column('codigo', css_class='form-group col-md-4 mb-0'),
                
                css_class='row'
            ),
            Row(
                Column('formula', css_class='form-group col-md-6 mb-0'),
                Column('tipoconcepto', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('indicador', css_class='form-group col-md-6 mb-0'),
                Column('grupo_dian', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
        )