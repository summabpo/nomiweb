from django.shortcuts import render
from apps.companies.models import Contratos , Contratosemp ,Ciudades
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('entrepreneur') 
def contractview(request,idcontrato): 
    contrato = Contratos.objects.get(idcontrato = idcontrato)
    
    return render(request, './companies/contractview.html',{'contrato': contrato })

@login_required
@role_required('entrepreneur')
def resumeview(request, idempleado):
    empleado = Contratosemp.objects.get(idempleado=idempleado)
    ciudadnacimiento = Ciudades.objects.get(idciudad=empleado.ciudadnacimiento) if empleado.ciudadnacimiento else None
    ciudadexpedicion = Ciudades.objects.get(idciudad=empleado.ciudadexpedicion) if empleado.ciudadexpedicion else None
    ciudadresidencia = Ciudades.objects.get(idciudad=empleado.ciudadresidencia) if empleado.ciudadresidencia else None

    empleados = {
        'docidentidad': empleado.docidentidad or '',
    'tipodocident': empleado.tipodocident or '',
    'pnombre': empleado.pnombre or '',
    'snombre': empleado.snombre or '',
    'papellido': empleado.papellido or '',
    'sapellido': empleado.sapellido or '',
    'fechanac': empleado.fechanac or '',
    'ciudadnacimiento': (ciudadnacimiento.ciudad if ciudadnacimiento else '') or '',
    'telefonoempleado': empleado.telefonoempleado or '',
    'direccionempleado': empleado.direccionempleado or '',
    'fotografiaempleado': empleado.fotografiaempleado or '',
    'sexo': empleado.sexo or '',
    'email': empleado.email or '',
    'ciudadresidencia': (ciudadresidencia.ciudad if ciudadresidencia else '') or '',
    'estadocivil': empleado.estadocivil or '',
    'idempleado': empleado.idempleado or '',
    'paisnacimiento': empleado.paisnacimiento or '',
    'paisresidencia': empleado.paisresidencia or '',
    'celular': empleado.celular or '',
    'profesion': empleado.profesion or '',
    'niveleducativo': empleado.niveleducativo or '',
    'gruposanguineo': empleado.gruposanguineo or '',
    'estatura': empleado.estatura or '',
    'peso': empleado.peso or '',
    'fechaexpedicion': empleado.fechaexpedicion or '',
    'ciudadexpedicion': (ciudadexpedicion.ciudad if ciudadexpedicion else '') or '',
    'dotpantalon': empleado.dotpantalon or '',
    'dotcamisa': empleado.dotcamisa or '',
    'dotzapatos': empleado.dotzapatos or '',
    'estrato': empleado.estrato or '',
    'numlibretamil': empleado.numlibretamil or '',
    'estadocontrato': empleado.estadocontrato or '',
    'formatohv': empleado.formatohv or ''
    }

    return render(request, './companies/resumeview.html', {'empleados': empleados })




