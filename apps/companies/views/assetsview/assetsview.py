from django.shortcuts import render
from apps.companies.models import Contratos , Contratosemp ,Ciudades


def contractview(request,idcontrato): 
    contrato = Contratos.objects.get(idcontrato = idcontrato)
    
    return render(request, './companies/contractview.html',{'contrato': contrato })


def resumeview(request, idempleado):
    empleado = Contratosemp.objects.get(idempleado=idempleado)
    ciudadnacimiento = Ciudades.objects.get(idciudad=empleado.ciudadnacimiento) if empleado.ciudadnacimiento else None
    ciudadexpedicion = Ciudades.objects.get(idciudad=empleado.ciudadexpedicion) if empleado.ciudadexpedicion else None
    ciudadresidencia = Ciudades.objects.get(idciudad=empleado.ciudadresidencia) if empleado.ciudadresidencia else None

    empleados = {
        'docidentidad': empleado.docidentidad,
        'tipodocident': empleado.tipodocident,
        'pnombre': empleado.pnombre,
        'snombre': empleado.snombre,
        'papellido': empleado.papellido,
        'sapellido': empleado.sapellido,
        'fechanac': empleado.fechanac,
        'ciudadnacimiento': ciudadnacimiento.ciudad if ciudadnacimiento else None,
        'telefonoempleado': empleado.telefonoempleado,
        'direccionempleado': empleado.direccionempleado,
        'fotografiaempleado': empleado.fotografiaempleado,
        'sexo': empleado.sexo,
        'email': empleado.email,
        'ciudadresidencia': ciudadresidencia.ciudad if ciudadresidencia else None,
        'estadocivil': empleado.estadocivil,
        'idempleado': empleado.idempleado,
        'paisnacimiento': empleado.paisnacimiento,
        'paisresidencia': empleado.paisresidencia,
        'celular': empleado.celular,
        'profesion': empleado.profesion,
        'niveleducativo': empleado.niveleducativo,
        'gruposanguineo': empleado.gruposanguineo,
        'estatura': empleado.estatura,
        'peso': empleado.peso,
        'fechaexpedicion': empleado.fechaexpedicion,
        'ciudadexpedicion': ciudadexpedicion.ciudad if ciudadexpedicion else None,
        'dotpantalon': empleado.dotpantalon,
        'dotcamisa': empleado.dotcamisa,
        'dotzapatos': empleado.dotzapatos,
        'estrato': empleado.estrato,
        'numlibretamil': empleado.numlibretamil,
        'estadocontrato': empleado.estadocontrato,
        'formatohv': empleado.formatohv,
    }

    return render(request, './companies/resumeview.html', {'empleados': empleados })




