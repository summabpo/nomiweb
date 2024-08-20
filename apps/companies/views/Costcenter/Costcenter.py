from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Costos
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.CostcenterForm import CostcenterForm
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('entrepreneur')
def Costcenter(request): 
    if request.method == 'POST':
        form = CostcenterForm(request.POST)
        if form.is_valid():
            nuevo_costo = Costos(
                nomcosto=form.cleaned_data['nomcosto'],
                suficosto=form.cleaned_data['suficosto'],
                grupocontable=form.cleaned_data['grupocontable']
            )
            nuevo_costo.save()
            messages.success(request, 'El Centro de costos ha sido añadido con éxito.')
            return redirect('companies:costcenter')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
    else:
        costos = Costos.objects.all().order_by('idcosto')
        form = CostcenterForm()
    
    return render(request, './companies/costcenter.html',
                    {
                        'costos':costos,
                        'form':form,
                    })
