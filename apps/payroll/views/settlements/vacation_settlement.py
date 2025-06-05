
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models  import Contratosemp , Vacaciones ,Contratos 
from apps.payroll.forms.VacationSettlementForm import VacationSettlementForm , BenefitFormSet

@login_required
@role_required('accountant')
def vacation_settlement(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    # Obtener la lista de empleados
    contratos_empleados = Contratos.objects\
        .select_related('idempleado') \
        .filter(estadocontrato=1 ,tipocontrato__idtipocontrato__in =[1,2,3,4] , id_empresa_id = idempresa ) \
        .values('idempleado__docidentidad','idempleado__sapellido', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre','idempleado__idempleado','idcontrato') 
    
    for emp in contratos_empleados:
        emp['idempleado__pnombre'] = '' if emp['idempleado__pnombre'] is None else emp['idempleado__pnombre']  
        emp['idempleado__snombre'] = '' if emp['idempleado__snombre'] is None else emp['idempleado__snombre']  
        emp['idempleado__papellido'] = '' if emp['idempleado__papellido'] is None else emp['idempleado__papellido']  
        emp['idempleado__sapellido'] = '' if emp['idempleado__sapellido'] is None else emp['idempleado__sapellido']  

    
    context = {
        'contratos_empleados': contratos_empleados,
    }

    return render(request, './payroll/vacation_settlement.html', context)
    

@login_required
@role_required('accountant')
def vacation_settlement_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = VacationSettlementForm(id_empresa=idempresa)
    formset = BenefitFormSet()

    data = {
        "conceptors": [
            (1, "Vacaciones Disfrutadas"),
            (2, "Vacaciones Compensadas"),
            (3, "Licencia Remunerada"),
            (4, "Licencia No Remunerada"),
            (5, "Suspension"),
        ]
    }

    if request.method == 'POST':
        novedad = request.POST.get("novedad")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        dias_c = request.POST.get("dias_c")
        dias_v = request.POST.get("dias_v")
        base = request.POST.get("base")
        valor = request.POST.get("valor")

        item = {
            "novedad": novedad,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "dias_c": dias_c,
            "dias_v": dias_v,
            "base": base,
            "valor": valor,
        }

        entries = request.session.get("settlement_entries", [])
        entries.append(item)
        request.session["settlement_entries"] = entries
        request.session.modified = True  # Asegura que Django guarde los cambios


    # Renderiza la página principal con todos los acumulados
    entries = request.session.get("settlement_entries", [])
    return render(request, './payroll/partials/vacation_settlement_add.html', {
        'form': form,
        'formset': formset,
        'data': data,
        
    })

@login_required
@role_required('accountant')
def vacation_modal_data(request,id,t):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    novedad = Vacaciones.objects.filter(idcontrato_id = id)

    if t == '1' : 
        titulo = 'Vacaciones'
        p = False
        novedad =  Vacaciones.objects.filter(idcontrato__idcontrato=id, tipovac__idvac__in=[1,2]) 
    else:
        novedad = Vacaciones.objects.filter(idcontrato__idcontrato=id, tipovac__idvac__in=[3,4,5])
        titulo = 'Ausensias'
        p = True

    data = {
        'titulo': titulo , 
        'pass': p ,
        'novedad' : novedad ,

    }
   
    return render(request, './payroll/partials/vacation_modal_data.html', {
        'data': data,
        
    })
