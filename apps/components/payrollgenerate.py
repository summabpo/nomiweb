from django.db.models import F, Value, CharField, IntegerField
from apps.employees.models import Contratosemp, Contratos, Nomina ,Crearnomina
from django.db.models import Sum
from .datacompanies import datos_cliente


def genera_comprobante(idnomina, idcontrato):
    contrato = Contratos.objects.filter(idcontrato=idcontrato).first()
    crear = Crearnomina.objects.filter(idnomina=idnomina).first()
    datac = datos_cliente()
    
    if contrato:
        nombre_completo = f"{contrato.idempleado.papellido} {contrato.idempleado.sapellido} {contrato.idempleado.pnombre} {contrato.idempleado.snombre}"

        # Obtener datos de devengados y descuentos
        dataDevengado = Nomina.objects.filter(idcontrato=idcontrato, idnomina=idnomina, valor__gt=0).order_by('idconcepto')
        dataDescuento = Nomina.objects.filter(idcontrato=idcontrato, idnomina=idnomina, valor__lt=0).order_by('idconcepto')

        # Formatear valores con puntos para los miles en dataDevengado
        for item in dataDevengado:
            item.valor = "{:,}".format(int(item.valor)).replace(",", ".") # Aplica formato de separador de miles
            
        for item in dataDescuento:
            item.valor = "{:,}".format(int(item.valor)).replace(",", ".") # Aplica formato de separador de miles

        # Calcular la suma de todos los valores en dataDevengado
        sumadataDevengado = dataDevengado.aggregate(total=Sum('valor'))['total'] or 0
        
        sumadataDescuento = dataDescuento.aggregate(total=Sum('valor'))['total'] or 0
        
        total = sumadataDevengado + sumadataDescuento
        
        
        
        periodo = f" {crear.fechainicial} hasta: {crear.fechafinal}"
        
        context = {
            #empresa
            'empresa':datac['nombre_empresa'],
            'nit': datac['nit_empresa'],
            'web':datac['website_empresa'],
            'logo':datac['logo_empresa'],        
            # nomina y empleado 
            'nombre_completo': nombre_completo,
            'cc': contrato.idempleado.docidentidad,
            'idcon': idcontrato,
            'idnomi': idnomina,
            'fecha1': contrato.fechainiciocontrato,
            'cargo': contrato.cargo,
            'salario': contrato.salario,
            'cuenta': contrato.cuentanomina,
            'ccostos': contrato.idcosto.nomcosto,
            'periodos': periodo,
            'eps': contrato.eps,
            'pension': contrato.pension,
            'dataDevengado': dataDevengado,
            'dataDescuento': dataDescuento,
            'sumadataDevengado': "{:,}".format(int(sumadataDevengado)).replace(",", "."), # Formatear la suma con separador de miles
            'sumadataDescuento': "{:,}".format(int(sumadataDescuento)).replace(",", "."), 
            'total':"{:,}".format(int(total)).replace(",", "."),
            
        }
    else:
        context = {
            'nombre_completo': None,
            'cc': None,
            'idcon': None,
            'fecha1': None,
            'cargo': None,
            'dataDevengado': None,
            'dataDescuento': None,
            'sumadataDevengado': None,
        }

    return context