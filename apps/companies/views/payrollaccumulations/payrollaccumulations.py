from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Liquidacion
from apps.companies.forms.ReportFilterForm import ReportFilterForm
from django.contrib import messages



def payrollaccumulations(request):
    liquidaciones = None
    
    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            # Aplicar filtros a la consulta de Liquidacion
            liquidaciones = Liquidacion.objects.all()
            
            # Obtener los parámetros de búsqueda del request.GET
            employee = form.cleaned_data['employee']
            cost_center = form.cleaned_data['cost_center']
            city = form.cleaned_data['city']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
    

            if employee:
                liquidaciones = liquidaciones.filter(idempleado = employee )
            if cost_center:
                liquidaciones = liquidaciones.filter(idcontrato__idcosto = cost_center )
            if city:
                liquidaciones = liquidaciones.filter(idcontrato__idsede = city )
            if start_date:
                liquidaciones = liquidaciones.filter(fechainiciocontrato = start_date )
            if end_date:
                liquidaciones = liquidaciones.filter(fechafincontrato = end_date )
                
            return render(request, 'companies/payrollaccumulations.html', {
                    'liquidaciones': liquidaciones,
                    'form': form,
                })
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect('companies:payrollaccumulations')
    form = ReportFilterForm()

    # Renderizar el template con los resultados filtrados y el formulario
    return render(request, 'companies/payrollaccumulations.html', {
        'liquidaciones': liquidaciones,
        'form': form,
    })
