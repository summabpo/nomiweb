from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models import Costos,Empresa 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.CostcenterForm import CostcenterForm
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company')
def Costcenter(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    usuario = request.session.get('usuario', {})
    if request.method == 'POST':
        form = CostcenterForm(request.POST,idempresa = idempresa)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa=usuario['idempresa'])
            nuevo_costo = Costos(
                nomcosto=form.cleaned_data['nomcosto'],
                suficosto=form.cleaned_data['suficosto'],
                grupocontable=form.cleaned_data['grupocontable'],
                id_empresa = empresa
            )
            nuevo_costo.save()
            messages.success(request, 'El Centro de costos ha sido añadido con éxito.')
            return redirect('companies:costcenter')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
    else:
        costos = Costos.objects.filter(id_empresa__idempresa=usuario['idempresa'] ).exclude(grupocontable= 0 ,suficosto = 0 ).order_by('idcosto')
        form = CostcenterForm(idempresa = idempresa)
    
    return render(request, './companies/costcenter.html',
                    {
                        'costos':costos,
                        'form':form,
                    })
