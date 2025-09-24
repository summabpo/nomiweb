from django.shortcuts import render, redirect, get_object_or_404
from apps.components.decorators import  role_required
from apps.common.models  import NovSalarios
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.companies.forms.updatesalaryForm import updatesalaryForm



@login_required
@role_required('company','accountant')
def update_salary(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    novsalarios = NovSalarios.objects.filter(idcontrato__id_empresa = idempresa )
    
    
    
    return render (request, './companies/update_salary.html',{'novsalarios':novsalarios})



@login_required
@role_required('company','accountant')
def update_salary_add(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    novsalarios = NovSalarios.objects.filter(idcontrato__id_empresa = idempresa )
    
    form = updatesalaryForm(idempresa = idempresa)
    
    return render (request, './companies/partials/update_salary_add.html',{'form':form})