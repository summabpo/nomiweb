from django.shortcuts import render
from apps.companies.models import Liquidacion
from apps.companies.forms.AbstractConceptForm import AbstractConceptForm
from apps.companies.models import Nomina
from apps.components.humani import format_value



def abstractconcept(request):
    # Obtener los parámetros de búsqueda del request.GET
    sconcept = request.GET.get('sconcept')
    payroll = request.GET.get('payroll')
    employee = request.GET.get('employee')
    month = request.GET.get('month')
    year = request.GET.get('year')

    # Aplicar filtros a la consulta de Liquidacio    
    
    
    if any([employee, payroll, sconcept, month, year]):
        nomina = Nomina.objects.filter(idcontrato__estadocontrato = 2 )
        if sconcept:
            nomina = nomina.filter(nombreconcepto = sconcept )
        
        if payroll:
            nomina = nomina.filter(idnomina__idnomina=payroll)
        
        if employee:
            nomina = nomina.filter(idempleado__idempleado = employee)
        
        if month:
            nomina = nomina.filter(mesacumular=month)
        
        if year:    
            nomina = nomina.filter(anoacumular=year)
    else :
        nomina = {}
    #Crear una instancia del formulario de filtro para enviar al template
    
    
    form = AbstractConceptForm()

    # Renderizar el template con los resultados filtrados y el formulario
    return render(request, 'companies/abstractconcept.html', {
        'liquidaciones': nomina,
        'form': form,
    })