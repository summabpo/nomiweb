from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class EditEmployeesForm(forms.Form):
    
    phone = forms.CharField(max_length=12, label='Phone',required=False)
    address = forms.CharField(max_length=100, label='Address',required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    
    

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        super(EditEmployeesForm, self).__init__(*args, **kwargs)
        self.fields['phone'].initial = initial.get('phone', '')
        self.fields['address'].initial = initial.get('address', '')
        
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('address', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('profile_picture', css_class='form-group col-md-12 mb-0'), 
                css_class='form-row' 
            ),
            Submit('submit', 'Guardar')
        )