from django.shortcuts import render
from apps.common.models  import Nomina , Bancos , Contratos , Vacaciones ,NominaComprobantes
from apps.components.humani import format_value
from apps.components.format import formttex , formtnun
from django.http import JsonResponse
from django.http import HttpResponse
from apps.components.datacompanies import datos_cliente 
from datetime import datetime, timedelta
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.companies.forms.SuspensionForm import SuspensionForm
from django.urls import reverse
from apps.components.salary import salario_mes


@login_required
@role_required('company')
def suspension_list(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    vacaciones = Vacaciones.objects.filter(
        idcontrato__id_empresa=idempresa, 
        tipovac__idvac__in=[3, 4, 5]
    ).values(
        "idcontrato__idempleado__docidentidad",
        "idcontrato__idempleado__papellido",
        "idcontrato__idempleado__sapellido",
        "idcontrato__idempleado__pnombre",
        "idcontrato__idempleado__snombre",
        "idcontrato",
        "idvacaciones",
    ).order_by('-idvacaciones')
    
    # Limpiar "no data" y valores nulos
    vacaciones = [
        {
            k: (
                "" if (v is None or str(v).strip().lower() == "no data")
                else v
            )
            for k, v in vac.items()
        }
        for vac in vacaciones
    ]
    
    context = {
        'vacaciones': vacaciones
    }
    
    return render(request, './companies/suspension_list.html', context )



@login_required
@role_required('company','accountant')
def suspension_list_add(request):
    
    usuario = request.session.get('usuario', {})
    user_role = request.session.get('usuario', {}).get('rol')
    idempresa = usuario['idempresa']
    form = SuspensionForm(idempresa = idempresa)
    
    if request.method == 'POST':
        print(request.POST )
        form = SuspensionForm(request.POST , idempresa = idempresa)
        if form.is_valid():
            contract = form.cleaned_data['contract']
            initial_date_str = form.cleaned_data['initial_date']
            initial_date = datetime.strptime(initial_date_str, "%Y-%m-%d").date()
            type_vac = form.cleaned_data['absence_type']

            sus_days = int(form.cleaned_data['sus_days'])
            end_date = initial_date + timedelta(days=(sus_days - 1 )) 
            
            ibc = NominaComprobantes.objects.filter(idcontrato_id=contract).order_by('-idhistorico').first()

            if not ibc:
                ibc = Contratos.objects.get(idcontrato=contract)
            
            Vacaciones.objects.create(
                idcontrato_id = contract , 
                fechainicialvac = initial_date , 
                ultimodiavac = end_date ,
                diascalendario = sus_days ,
                diasvac = 0 ,
                basepago =  ibc.salario,
                tipovac_id = type_vac ,
            )
            
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'La Novedad fue registrada correctamente'    
            if user_role == 'accountant' : 
                response['X-Up-Location'] = reverse('companies:absences_resumen')   
            else : 
                response['X-Up-Location'] = reverse('companies:suspension_list')           
            return response
    
    
    return render(request, './companies/partials/suspension_list_add.html',{'form' : form})
