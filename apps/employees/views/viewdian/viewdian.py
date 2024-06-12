from django.shortcuts import render,redirect
from apps.employees.models import Ingresosyretenciones




def viewdian(request):
    ide = request.session.get('idempleado', {})
    
    # Realizar una única consulta y usar el resultado para ambas necesidades
    reten = Ingresosyretenciones.objects.filter(idempleado=ide)
    years_query = reten.values('anoacumular').first()
    
    years = years_query['anoacumular'] if years_query else None
    
    return render(request, 'employees/viewdian.html', {
        'reten': reten,
        'years': years,
    })
