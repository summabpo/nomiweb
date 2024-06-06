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
    request.session['idempleado'] = usuario['id']

    return render(request, './employees/index.html')
    


def datos_empleado(id_empleado):
    if id_empleado == 0:
        return None
    else:
        try:
            contrato = Contratos.objects.get(idempleado=id_empleado, estadocontrato=1)
            empleado = Contratosemp.objects.filter(idempleado=contrato.idempleado_id).annotate(
                nombre_letras=Concat(F('pnombre'), Value(' '), F('snombre'), Value(' '), 
                                        F('papellido'), Value(' '), F('sapellido'), output_field=CharField())
            ).values('nombre_letras').first()

            info_empleado = {
                'nombre_completo': empleado['nombre_letras'],
                'correo': contrato.idempleado.email,
                'ide': contrato.idempleado_id ,
                'idc': contrato.idcontrato,
            }
            return info_empleado

        except Contratos.DoesNotExist:
            return {'error': 'El contrato no existe'}
        except Exception as e:
            return {'error': str(e)}






