from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO
from apps.common.models import Contratosemp
from apps.components.decorators import role_required
from django.contrib.auth.decorators import login_required

# Constante de meses
MESES = {
    13: "Todos",
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

@login_required
@role_required('company')
def birthday_view(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')
    mes = int(request.GET.get('mes', 13))

    if mes == 13:
        cumpleanieros = Contratosemp.objects.filter(
            estadocontrato=1,
            id_empresa__idempresa=idempresa
        ).values('papellido', 'pnombre', 'snombre', 'sapellido', 'fechanac')
    
    else :
        # Filtrar empleados que cumplen años en el mes seleccionado
        cumpleanieros = Contratosemp.objects.filter(
            fechanac__month=mes,
            estadocontrato=1,
            id_empresa__idempresa=idempresa
        ).values('papellido', 'pnombre', 'snombre', 'sapellido', 'fechanac')    

    # Si se solicita descargar, generar el archivo Excel
    if 'descargar' in request.GET:
        response = generar_excel_cumpleanieros(cumpleanieros)
        return response

    return render(request, 'companies/birthday.html', {
        'cumpleanieros': cumpleanieros,
        'mes': mes,
        'meses': MESES
    })

def generar_excel_cumpleanieros(cumpleanieros):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Cumpleañeros'

    # Escribir encabezados
    sheet.append(['Nombre', 'Día', 'Mes'])

    # Escribir datos de empleados
    for empleado in cumpleanieros:
        nombre = f"{empleado['pnombre']} {empleado['snombre']} {empleado['papellido']} {empleado['sapellido']}"
        dia = empleado['fechanac'].day
        mes = empleado['fechanac'].month
        sheet.append([nombre, dia, mes])
    
    # Crear respuesta HTTP con el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="cumpleanieros.xlsx"'

    with BytesIO() as b:
        workbook.save(b)
        response.write(b.getvalue())
    
    return response
