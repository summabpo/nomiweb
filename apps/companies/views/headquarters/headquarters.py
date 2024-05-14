
from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Sedes ,Entidadessegsocial
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.headquartersForm import headquartersForm
from django.contrib import messages
from django.db import transaction


def headquarters(request): 
    if request.method == 'POST':
        form = headquartersForm(request.POST)
        if form.is_valid():
            try:
                nombresede = form.cleaned_data['nombresede']
                cajacompensacion = form.cleaned_data['cajacompensacion']
                aux = Entidadessegsocial.objects.get(codigo=cajacompensacion)
                
                with transaction.atomic():
                    sede = Sedes.objects.create(
                        nombresede=nombresede,
                        cajacompensacion=aux.entidad,
                        codccf=aux.codigo,
                    )
                    sede.save()
                
                messages.success(request, 'La sede ha sido añadida con éxito.')
                return redirect('companies:headquarters')
            except Exception as e:
                messages.error(request, 'Todo lo que podria salir mal , salio mal ')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
    else:
        sedes = Sedes.objects.all().order_by('idsede')
        form = headquartersForm()
    
    return render(request, './companies/headquarters.html',
                    {
                        'sedes':sedes,
                        'form':form,
                    })