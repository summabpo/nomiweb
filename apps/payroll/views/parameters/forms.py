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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SGP'})
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
