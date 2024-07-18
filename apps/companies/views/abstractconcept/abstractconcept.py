from django.shortcuts import render
from apps.companies.models import Liquidacion
from apps.companies.forms.AbstractConceptForm import AbstractConceptForm
from apps.companies.models import Nomina
from apps.components.humani import format_value



def abstractconcept(request):
    
    
    
    if request.method == 'POST':
        form = AbstractConceptForm(request.POST)
        if form.is_valid():
            nomina = Nomina.objects.filter(idcontrato__estadocontrato = 2 )[:20]
            
            sconcept = form.cleaned_data['sconcept']
            payroll = form.cleaned_data['payroll']
            employee = form.cleaned_data['employee']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']

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
    else :
        nomina = {}
    #Crear una instancia del formulario de filtro para enviar al template
    
    
    form = AbstractConceptForm()

    # Renderizar el template con los resultados filtrados y el formulario
    return render(request, 'companies/abstractconcept.html', {
        'liquidaciones': nomina,
        'form': form,
    })
