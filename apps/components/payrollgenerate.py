from django.db.models import F, Value, CharField, IntegerField
from apps.employees.models import Contratosemp, Contratos, Nomina ,Crearnomina
from django.db.models import Sum
from .datacompanies import datos_cliente
from apps.components.humani import format_value ,format_value_float

def limitar_cadena(cadena, max_length=25):
    if len(cadena) > max_length:
        return cadena[:max_length-3] + '...'
    return cadena


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
            item.valor = format_value(item.valor) # Aplica formato de separador de mil
            item.cantidad = format_value_float(item.cantidad)
            item.nombreconcepto = limitar_cadena(item.nombreconcepto)
            
        for item in dataDescuento:
            item.valor = format_value(item.valor) # Aplica formato de separador de miles
            item.cantidad = format_value_float(item.cantidad)
            item.nombreconcepto = limitar_cadena(item.nombreconcepto)

        # Calcular la suma de todos los valores en dataDevengado
        sumadataDevengado = dataDevengado.aggregate(total=Sum('valor'))['total'] or 0
        
        sumadataDescuento = dataDescuento.aggregate(total=Sum('valor'))['total'] or 0
        
        total = sumadataDevengado + sumadataDescuento
        
        
        
        periodo = f" {crear.fechainicial} hasta: {crear.fechafinal}"
        centro = f"{contrato.idcosto.idcosto} - {contrato.idcosto.nomcosto}"
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
            'fecha1': str(contrato.fechainiciocontrato),
            'cargo': contrato.cargo,
            'salario': format_value(contrato.salario),
            'cuenta': contrato.cuentanomina,
            'ccostos': centro,
            'periodos': periodo,
            'eps': contrato.eps,
            'pension': contrato.pension,
            'dataDevengado': dataDevengado,
            'dataDescuento': dataDescuento,
            'sumadataDevengado': format_value(sumadataDevengado), # Formatear la suma con separador de miles
            'sumadataDescuento': format_value(sumadataDescuento), 
            'total':format_value(total),
            
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