from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class chargesForm(forms.Form):
    nombrecargo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Nombre cargo'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nombrecargo', css_class='form-group mb-0'),
                css_class='row'
            ),
            Submit('submit', 'Guardar')
        )
    