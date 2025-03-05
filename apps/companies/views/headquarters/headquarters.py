
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Sedes ,Entidadessegsocial
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.headquartersForm import headquartersForm
from django.contrib import messages
from django.db import transaction

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
@role_required('company')
def headquarters(request): 
    usuario = request.session.get('usuario', {})
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    sedes = Sedes.objects.filter(id_empresa_id = idempresa).exclude(idsede=16).order_by('idsede')
    form = headquartersForm()
    return render(request, './companies/headquarters.html',
                    {
                        'sedes':sedes,
                        'form':form,
                    })
    
    
    
    

@login_required
@role_required('company')
def headquarters_modal(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    if request.method == 'POST':
        form = headquartersForm(request.POST)
        if form.is_valid():
            nombresede = form.cleaned_data['nombresede']
            cajacompensacion = form.cleaned_data['cajacompensacion']
            aux = Entidadessegsocial.objects.get(codigo=cajacompensacion)
            sede = Sedes(
                nombresede=nombresede,
                cajacompensacion=aux.entidad,
                codccf=aux.codigo,
                id_empresa_id = idempresa
            )
            sede.save()
            return JsonResponse({'status': 'success', 'message': 'Sede creada exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = headquartersForm()    
    return render(request, './companies/partials/headquartersModal.html',
                    {
                        'form':form,
                    })