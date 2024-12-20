from django.shortcuts import render
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

# Formulario 1 (y único, en este caso)
class FormularioUno(forms.Form):
    nombre = forms.CharField(max_length=100)
    edad = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'formulario_1'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='form-group col-md-6'),
                Column('edad', css_class='form-group col-md-6'),
                css_class='row'
            )
        )

# Vista que maneja ambos envíos de formulario 1
def vista_con_dos_formularios(request):
    form1 = FormularioUno()
    form2 = FormularioUno()


    if request.method == 'POST':
        # Procesar formulario 1 con submit_1
        if 'submit_1' in request.POST:
            form1 = FormularioUno(request.POST)
            if form1.is_valid():
                nombre = form1.cleaned_data['nombre']
                edad = form1.cleaned_data['edad']
                print(f"Formulario 1 procesado: {nombre}, {edad} años")
                
            else:
                form1 = FormularioUno()
        # Procesar formulario 1 con submit_2
        elif 'submit_2' in request.POST:
            form2 = FormularioUno(request.POST)
            if form2.is_valid():
                nombre = form2.cleaned_data['nombre']
                edad = form2.cleaned_data['edad']
                print(f"Formulario 1 procesado desde submit_2: {nombre}, {edad} años")
                
            else:
                form2 = FormularioUno()

    return render(request, 'mi_template.html', {'form1': form1,'form2': form2})
