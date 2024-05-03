from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Field

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Ingrese su nombre de usuario'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('username', wrapper_class='col-md-3'),
                    css_class='form-group row'
                ),
                Div(
                    Field('password', wrapper_class='col-md-3'),
                    css_class='form-group row'
                ),
                css_class='form-group'
            ),
            Submit('submit', 'Ingresar', css_class='btn btn-light-success')
        )
