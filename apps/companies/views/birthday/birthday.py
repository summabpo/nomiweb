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
    """
    Muestra los empleados que cumplen años en un mes específico o en todos los meses.

    Esta vista permite visualizar los empleados que cumplen años en un mes determinado o en todos los meses 
    de un año. Si se solicita la descarga, genera un archivo Excel con la lista de los empleados y sus fechas de nacimiento.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los parámetros 'mes' y 'descargar'.
        - 'mes' es el número del mes para filtrar los empleados (opcional, por defecto es 13 para todos los meses).
        - 'descargar' es un parámetro opcional que indica si se desea generar el archivo Excel de los empleados.

    Returns
    -------
    HttpResponse
        Si el parámetro 'descargar' está presente, devuelve un archivo Excel con los empleados que cumplen años.
        Si no, retorna una respuesta con la página de visualización de los empleados.

    See Also
    --------
    Contratosemp : Modelo que representa los datos de los empleados.
    generar_excel_cumpleanieros : Función que genera el archivo Excel con los empleados que cumplen años.
    role_required : Decorador personalizado que restringe el acceso según el rol.
    login_required : Decorador de Django que exige autenticación del usuario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` para acceder a esta vista.
    El parámetro 'mes' se debe proporcionar como un número del 1 al 12, donde 13 significa "todos los meses".
    """

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
