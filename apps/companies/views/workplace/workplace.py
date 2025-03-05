
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Centrotrabajo , Empresa 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.workplaceForm import workplaceForm
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
@role_required('company')
def workplace(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    centrotrabajos = Centrotrabajo.objects.filter(id_empresa_id = idempresa ).order_by('centrotrabajo')
    form = workplaceForm()
    
    return render(request, './companies/workplace.html',
                    {
                        'centrotrabajos':centrotrabajos,
                        'form':form,
                    })
    
    
@login_required
@role_required('company')
def workplace_modal(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    if request.method == 'POST':
        form = workplaceForm(request.POST)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa=usuario['idempresa'])
            nuevo_centro_trabajo = Centrotrabajo(
                nombrecentrotrabajo=form.cleaned_data['nombrecentrotrabajo'] ,
                tarifaarl = form.cleaned_data['tarifaarl'] ,
                id_empresa = empresa
            )
            nuevo_centro_trabajo.save()
            return JsonResponse({'status': 'success', 'message': 'Centro de Trabajo creado exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = workplaceForm()    
    return render(request, './companies/partials/workplaceModal.html',
                    {
                        'form':form,
                    })
