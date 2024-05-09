
from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Centrotrabajo
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.workplaceForm import workplaceForm
from django.contrib import messages


def workplace(request): 
    if request.method == 'POST':
        form = workplaceForm(request.POST)
        if form.is_valid():
            nombre_centrotrabajo = form.cleaned_data['nombrecentrotrabajo']
            tarifa_arl = form.cleaned_data['tarifaarl']
            
            centro_trabajo = Centrotrabajo.objects.create(
                nombrecentrotrabajo=nombre_centrotrabajo,
                tarifaarl=tarifa_arl
            )
            centro_trabajo.save()
            
            messages.success(request, 'El cargo ha sido añadido con éxito.')
            return redirect('companies:workplace')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
    else:
        centrotrabajos = Centrotrabajo.objects.all().order_by('centrotrabajo')
        form = workplaceForm()
    
    return render(request, './companies/workplace.html',
                    {
                        'centrotrabajos':centrotrabajos,
                        'form':form,
                    })
