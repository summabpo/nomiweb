from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.common.models import EditHistory
from apps.companies.forms.JobChangeForm import JobChangeForm

@login_required
@role_required('company','accountant')
def job_change(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    cargos = EditHistory.objects.filter( operation_type = 'update' , id_empresa = idempresa , description = 'job') 
    

    return render(request, "./companies/job_change.html",{'cargos':cargos})




@login_required
@role_required('company','accountant')
def job_change_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = JobChangeForm(idempresa = idempresa)
    if request.method == "POST":

        print('psot')
    

    return render(request, "./companies/partials/job_change_add.html",{'form':form})