from django.shortcuts import render
from apps.companies.models import Liquidacion
from apps.companies.forms.ReportFilterForm import ReportFilterForm
from apps.companies.forms.AbstractConceptForm import AbstractConceptForm



def payrollaccumulations(request):
    # Obtener los parámetros de búsqueda del request.GET
    employee = request.GET.get('employee')
    cost_center = request.GET.get('cost_center')
    city = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Aplicar filtros a la consulta de Liquidacion
    liquidaciones = Liquidacion.objects.all()

    if employee:
        print(employee)
    if cost_center:
        print(cost_center)
    if city:
        print(city)
    if start_date:
        print(start_date)
    if end_date:
        print(end_date)

    # Limitar los resultados a 10 registros como en tu ejemplo original
    liquidaciones = liquidaciones[:10]

    # Crear una instancia del formulario de filtro para enviar al template
    form = ReportFilterForm()

    # Renderizar el template con los resultados filtrados y el formulario
    return render(request, 'companies/payrollaccumulations.html', {
        'liquidaciones': liquidaciones,
        'form': form,
    })
