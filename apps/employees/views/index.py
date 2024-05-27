from django.shortcuts import render, redirect, get_object_or_404
from apps.components.decorators import custom_login_required ,custom_permission
from django.db.models import Sum, F, Value, CharField
from apps.companies.models import Contratos,Contratosemp
from django.db.models.functions import Concat
from datetime import datetime
from apps.components.datacompanies import datos_cliente



@custom_login_required
@custom_permission('employees')
def index_employees(request):
    usuario = request.session.get('usuario', {})
    
    request.session['empleado'] = datos_empleado(usuario['id'])
    request.session['cliente'] = datos_cliente()
    
    return render(request, './employees/index.html')
    


def datos_empleado(id_empleado):
    if id_empleado == 0:
        return None
    else:
        contrato = Contratos.objects.get(idempleado=id_empleado)
        
        empleado = Contratosemp.objects.filter(idempleado=contrato.idempleado_id).annotate(
            nombre_letras=Concat(F('pnombre'), Value(' '), F('snombre'), Value(' '), 
                                    F('papellido'), Value(' '), F('sapellido'), output_field=CharField())
                                    ).values('nombre_letras').first()
            
        info_empleado = {
            'nombre_completo': empleado['nombre_letras'], 
            'fechainiciocontrato': contrato.fechainiciocontrato.strftime('%Y-%m-%d'), # Convertir a cadena
            'cargo': contrato.cargo, 
            'tipo_contrato': contrato.tipocontrato.idtipocontrato,
            'nombre_contrato': contrato.tipocontrato.tipocontrato,
            'docidentidad': contrato.idempleado.docidentidad ,
            'salario': contrato.salario,
            'idc': contrato.idcontrato,
            'ide': contrato.idempleado_id
        }
        return info_empleado





