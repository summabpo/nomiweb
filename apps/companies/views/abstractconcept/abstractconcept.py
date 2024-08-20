from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.forms.AbstractConceptForm import AbstractConceptForm
from apps.companies.models import Nomina
from apps.components.humani import format_value
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('entrepreneur')
def abstractconcept(request):
    
    if request.method == 'POST':
        form = AbstractConceptForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario
            sconcept = form.cleaned_data.get('sconcept')
            payroll = form.cleaned_data.get('payroll')
            employee = form.cleaned_data.get('employee')
            month = form.cleaned_data.get('month')
            year = form.cleaned_data.get('year')

            # Construir los filtros dinámicamente
            filters = {
                'nombreconcepto': sconcept,
                'idnomina__idnomina': int(payroll) if payroll else None,
                'idempleado__idempleado': employee,
                'mesacumular': month,
                'anoacumular': year,
            }
            
            
            # Eliminar filtros con valores vacíos
            filters = {k: v for k, v in filters.items() if v}
            
            
            
            # Filtrar los datos
            nominas = Nomina.objects.filter(**filters).order_by('-idnomina')
            nomina = nominas if nominas.exists() else None
            
            
            return render(request, 'companies/abstractconcept.html', {
                'liquidaciones': nominas,
                'form': form,
            })
            
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect('companies:abstractconcept')
    else :
        nomina = {}
    #Crear una instancia del formulario de filtro para enviar al template
    
    
    form = AbstractConceptForm()

    # Renderizar el template con los resultados filtrados y el formulario
    return render(request, 'companies/abstractconcept.html', {
        'liquidaciones': nomina,
        'form': form,
    })
