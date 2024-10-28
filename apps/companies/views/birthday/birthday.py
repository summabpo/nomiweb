from django.views import View
from django.shortcuts import render
from apps.common.models import Contratosemp
from django.http import HttpResponse
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company')
def birthday_view(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    # Obtener el mes de los parámetros GET, o usar el mes actual por defecto
    mes = int(request.GET.get('mes', datetime.now().month))
    
    # Filtrar empleados que cumplen años en el mes seleccionado
    cumpleanieros = Contratosemp.objects.filter(
        fechanac__month=mes,
        estadocontrato=1,
        id_empresa__idempresa=idempresa
    ).values('papellido', 'pnombre', 'snombre', 'sapellido', 'fechanac')    

    # Si el parámetro 'descargar' está presente en los GET, generar un archivo Excel
    if 'descargar' in request.GET:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Cumpleañeros'

        # Escribir encabezados
        sheet.append(['Nombre', 'Día', 'Mes'])

        # Escribir datos
        for empleado in cumpleanieros:
            nombre = f"{empleado.pnombre} {empleado.papellido}"
            dia = empleado.fechanac.day
            mes = empleado.fechanac.month
            sheet.append([nombre, dia, mes])
        
        # Generar respuesta HTTP con el archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="cumpleanieros.xlsx"'
        
        # Guardar el workbook en el response
        with BytesIO() as b:
            workbook.save(b)
            response.write(b.getvalue())
        
        return response
    
    # Crear una lista de meses
    meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    
    return render(request, 'companies/birthday.html', {'cumpleanieros': cumpleanieros, 'mes': mes, 'meses': meses})
