from django.shortcuts import render, redirect
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, ButtonHolder
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import User



class CompanyForms(forms.Form):
    idempresa = forms.ChoiceField(
        label='Seleccione una Empresa',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        id = kwargs.pop('id', None)
        user = User.objects.get(id=id)
        super().__init__(*args, **kwargs)

        self.fields['idempresa'].choices = [('', '----------')] + [
            (emp.idempresa, emp.nombreempresa) for emp in user.id_empresa.all()
        ]

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'

        for field_name in ['idempresa']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'data-control': 'select2',
                    'class': 'form-select',
                })

        self.helper.layout = Layout(
            Row(
                Column('idempresa', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            ),
            ButtonHolder(
                Submit('submit', 'Seleccionar Empresa', css_class='btn btn-light-info col-md-12 mb-0')
            )
        )




@login_required
@role_required('accountant')
def select_company(request):
    usuario = request.session.get('usuario', {})
    user = User.objects.get(id = usuario['id'] )
    empresas = user.id_empresa.all()
    
    if empresas.count() == 1:
        unica_empresa = empresas.first()
        usuario['idempresa'] = unica_empresa.idempresa
        request.session['usuario'] = usuario
        return redirect('payroll:index_payroll')
    
    if request.method == 'POST':
        form = CompanyForms(request.POST, id=request.user.id)
        if form.is_valid():
            empresa_id = form.cleaned_data['idempresa']
            usuario['idempresa'] = empresa_id
            usuario['pass'] = True
            request.session['usuario'] = usuario
            return redirect('payroll:index_payroll')  # Redirige a donde necesites
    else:
        form = CompanyForms(id=request.user.id)
    
    return render(request, './payroll/select_company.html', {'form': form})
    
    





