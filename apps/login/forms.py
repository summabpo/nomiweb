from django import forms


## login 
class LoginForm(forms.Form):
    username = forms.CharField(label="UserName", widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'exampleInputEmail1', 'placeholder': 'Ingresa tu usuario', 'required': True}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'exampleInputPassword1', 'placeholder': 'Contraseña', 'required': True}))
