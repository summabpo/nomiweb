
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Centrotrabajo , Empresa 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.workplaceForm import workplaceForm
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required


@login_required
@role_required('company')
def workplace(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    if request.method == 'POST':
        form = workplaceForm(request.POST)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa = idempresa)
        
            centro_trabajo = Centrotrabajo.objects.create(
                nombrecentrotrabajo= form.cleaned_data['nombrecentrotrabajo'] ,
                tarifaarl= form.cleaned_data['tarifaarl'] ,
                id_empresa = empresa 
            )
            centro_trabajo.save()
            
            messages.success(request, 'El Centro de Trabajo ha sido añadido con éxito.')
            return redirect('companies:workplace')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
    else:
        centrotrabajos = Centrotrabajo.objects.filter(id_empresa_id = idempresa ).order_by('centrotrabajo')
        form = workplaceForm()
    
    return render(request, './companies/workplace.html',
                    {
                        'centrotrabajos':centrotrabajos,
                        'form':form,
                    })
