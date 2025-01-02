from django.shortcuts import render
from apps.common.models import Contratos , Contratosemp ,Ciudades
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse




@login_required
@role_required('company','accountant')
def contractview(request): 
    
    resultados = {
        '1': 'Abono a cuenta',
        '2': 'Cheque',
        '3': 'Efectivo',
        '4': 'Falla'
    }
    
    
    dato = request.GET.get('dato')
    try:
        contrato = Contratos.objects.get(idcontrato = dato)  # Cambia la lógica según tu modelo
        # Usamos una función auxiliar para devolver '' si el campo es None
        def safe_get(value):
            return value if value is not None else ''

        response_data = {
            'idcontrato': safe_get(contrato.idcontrato),
            'dateinit': safe_get(contrato.fechainiciocontrato),
            'dateend': safe_get(contrato.fechafincontrato),
            'cargo': safe_get(contrato.cargo.nombrecargo),
            'lugartrabajo': safe_get(contrato.ciudadcontratacion.ciudad),
            'tipocontrato': safe_get(contrato.tipocontrato.tipocontrato),
            'modelo': safe_get(contrato.idmodelo.nombremodelo),
            'salario': safe_get(contrato.salario),
            'tiposalario': safe_get(contrato.tiposalario.tiposalario),
            'modalidadsalario': safe_get(contrato.salariovariable),
            'vivetrabajo': 'Si'if contrato.auxiliotransporte else 'No' ,
            'ciudadcontratacion': safe_get(contrato.ciudadcontratacion.ciudad),
            'bancocuenta': safe_get(contrato.bancocuenta.nombanco),
            'tipocuentanomina': safe_get(contrato.tipocuentanomina),
            'formapago' : resultados.get(contrato.formapago, 'Ninguna opción'),
            'cuentanomina': safe_get(contrato.cuentanomina),
            'nomcosto': safe_get(contrato.idcosto.nomcosto),
            'nomsubcosto': contrato.idsubcosto.nomsubcosto if contrato.idsubcosto else ' ' ,
            'eps': contrato.codeps.entidad if contrato.codeps else ' ' ,
            'fondocesantias': contrato.codafp.entidad if contrato.codafp else ' ' ,
            'pension': contrato.codccf.entidad if contrato.codccf.entidad else ' ',
            'nombrecentrotrabajo': safe_get(contrato.centrotrabajo.nombrecentrotrabajo),
            'nombresede': safe_get(contrato.idsede.nombresede),
            'tarifaarl': safe_get(contrato.centrotrabajo.tarifaarl),
            'cajacompensacion': safe_get(contrato.idsede.cajacompensacion),
            'tipocotizante': safe_get(contrato.tipocotizante.tipocotizante),
            'subtipocotizante': safe_get(contrato.subtipocotizante.subtipocotizante),
            'pensionado': safe_get(contrato.riesgo_pension),
        }
        return JsonResponse({'data': response_data})
    except Exception as e:
        return JsonResponse({'error': 'Falla de sistema'}, status=404)
    
    
    
    
    #return render(request, './companies/contractview.html',{'contrato': contrato })

@login_required
@role_required('company','accountant')
def resumeview(request):
    dato = request.GET.get('dato')
    try:
        empleado = Contratosemp.objects.get(idempleado=dato)
        response_data = {
            'docidentidad': empleado.docidentidad or '',
            'tipodocident': empleado.tipodocident.codigo or '',
            'pnombre': empleado.pnombre or '',
            'snombre': empleado.snombre or '',
            'papellido': empleado.papellido or '',
            'sapellido': empleado.sapellido or '',
            'fechanac': empleado.fechanac or '',
            'ciudadnacimiento': (empleado.ciudadnacimiento.ciudad if empleado.ciudadnacimiento else '') or '',
            'telefonoempleado': empleado.telefonoempleado or '',
            'direccionempleado': empleado.direccionempleado or '',
            'fotografiaempleado': empleado.fotografiaempleado or '',
            'sexo': empleado.sexo or '',
            'email': empleado.email or '',
            'ciudadresidencia': (empleado.ciudadresidencia.ciudad if empleado.ciudadresidencia else '') or '',
            'estadocivil': empleado.estadocivil or '',
            'idempleado': empleado.idempleado or '',
            'paisnacimiento': (empleado.paisnacimiento.pais if empleado.paisnacimiento else '') or '' ,
            'paisresidencia': (empleado.paisresidencia.pais if empleado.paisresidencia else '') or '' ,
            'celular': empleado.celular or '',
            'profesion': empleado.profesion or '',
            'niveleducativo': empleado.niveleducativo or '',
            'gruposanguineo': empleado.gruposanguineo or '',
            'estatura': empleado.estatura or '',
            'peso': empleado.peso or '',
            'fechaexpedicion': empleado.fechaexpedicion or '',
            'ciudadexpedicion': (empleado.ciudadexpedicion.ciudad if empleado.ciudadexpedicion else '') or '',
            'dotpantalon': empleado.dotpantalon or '',
            'dotcamisa': empleado.dotcamisa or '',
            'dotzapatos': empleado.dotzapatos or '',
            'estrato': empleado.estrato or '',
            'numlibretamil': empleado.numlibretamil or '',
            'estadocontrato': empleado.estadocontrato or '',
            'formatohv': empleado.formatohv or ''
        }
        return JsonResponse({'data': response_data})
        
    except Exception as e:
        return JsonResponse({'error': 'Falla de sistema'}, status=404)
    


