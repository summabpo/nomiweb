from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from apps.companies.models import Contratosemp , Vacaciones ,Contratos 
from apps.employees.models import EmpVacaciones, Vacaciones, Contratos, Festivos, Contratosemp , Tipoavacaus




def vacation_request(request):
    # Obtener la lista de empleados
    vacaciones = EmpVacaciones.objects.all().order_by('-id_sol_vac').values('idcontrato__idempleado__docidentidad', 'idcontrato__idempleado__sapellido', 'idcontrato__idempleado__papellido', 
                'idcontrato__idempleado__pnombre', 'idcontrato__idempleado__snombre', 'idcontrato__idempleado__idempleado', 
                'tipovac', 'fechainicialvac','fechafinalvac','estado','idcontrato__idcontrato') [:20]
    
    context ={ 
            'vacaciones' : vacaciones,
        }
    
    return render(request, './companies/vacation_request.html', context)