from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tiempos , Crearnomina
from django.http import HttpResponse
from django.urls import reverse
from apps.payroll.forms.SettlementForm import SettlementForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime , date
from django.db.models import Q
import pandas as pd

@login_required
@role_required('accountant')
def time_list(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    times = Tiempos.objects.filter(idempresa = idempresa) 
    
    return render(request, './payroll/time_list.html',{'times': times})


def formatear_fecha(valor):
    if isinstance(valor, datetime):   # Si ya es datetime
        return valor.date()
    if isinstance(valor, str) and '/' in valor:
        try:
            return datetime.strptime(valor, '%d/%m/%Y').date()
        except:
            return valor
    return valor

def time_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    nominas = Crearnomina.objects.filter(estadonomina=True, id_empresa_id=idempresa).order_by('-idnomina')
    
    
    if request.method == 'POST' and request.FILES.get('file'):
        errors = []
        file = request.FILES['file']
        idnomina = request.POST.get('idnomina')
        df = pd.read_excel(file, header=None)
        
        registros_validados = [] 
        
        print(df)
        print('---------')
        print(idnomina)
        
        for idx, fila in df.iterrows():
            print(f"\n🔹 Fila {idx + 1}\n")

            contrato         = fila[0]
            fecha_ingreso    = formatear_fecha(fila[1])
            fecha_salida     = formatear_fecha(fila[2])
            hora_ingreso     = fila[3]
            hora_salida      = fila[4]
            horas_extras     = fila[5]

            print(f"{'contrato'         :<18}: {contrato}")
            print(f"{'fecha_ingreso'    :<18}: {fecha_ingreso}")
            print(f"{'fecha_salida'     :<18}: {fecha_salida}")
            print(f"{'hora_ingreso'     :<18}: {hora_ingreso}")
            print(f"{'hora_salida'      :<18}: {hora_salida}")
            print(f"{'horas_extras'     :<18}: {horas_extras}")
    
        # try:
            
            
        #     if errors:
        #         return render(request, './companies/partials/disability_upload_errors.html', {
        #             'errors': errors
        #         })
                
        # except Exception as e:
        #     errors.append(f"Error general al procesar el archivo")

        # if errors:
        #     return render(request, './companies/partials/disability_upload_errors.html', {
        #         'errors': errors
        #     })
            
            
    return render(request, './payroll/partials/time_add.html',{'nominas':nominas})
