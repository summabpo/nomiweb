from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Incapacidades
from apps.companies.forms.disabilitiesForm  import DisabilitiesForm



def disabilities(request):
    incapacidades = Incapacidades.objects.values(
        'idcontrato__idcontrato',
        'idempleado__docidentidad',
        'idempleado__pnombre',
        'idempleado__snombre',
        'idempleado__papellido',
        'idempleado__sapellido',
        'entidad',
        'coddiagnostico__coddiagnostico',
        'diagnostico',
        'prorroga',
        'fechainicial',
        'dias',
    ).order_by('-idincapacidad')
    
    
    form = DisabilitiesForm()
    
    
    return render (request, './companies/disabilities.html',
                    {
                      'incapacidades' :incapacidades,  
                      'form' :form,
                    })