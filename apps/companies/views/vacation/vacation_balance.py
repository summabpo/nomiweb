from django.shortcuts import render
from apps.common.models import Contratos, Vacaciones, Conceptosfijos
from django.db.models import Q, Sum
from django.utils import timezone
from apps.components.utils import calcular_dias_360
from datetime import datetime
from django.http import HttpResponse 
from apps.components.generate_vacation_balance import generate_balance_excel
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

def calcular_vacaciones(contrato, concepto,fecha_actual):
    # Calcular las vacaciones disponibles
    total_vac_disf = Vacaciones.objects.filter(
        idcontrato=contrato.idcontrato
    ).filter(Q(tipovac='1') | Q(tipovac='2')).aggregate(Sum('diasvac'))['diasvac__sum'] or 0

    # Fecha actual y fecha inicial
    fecha_actual = fecha_actual
    fecha_inicial = contrato.fechainiciocontrato

    total_vac = (calcular_dias_360(fecha_inicial.strftime("%Y-%m-%d"), fecha_actual.strftime("%Y-%m-%d"))) * (concepto/100)
    saldo = total_vac - total_vac_disf

    return {
        "total_vac_disf": round(total_vac_disf, 2),
        "total_vac": round(total_vac, 2),
        "saldo": round(saldo, 2)
    }


def vacation_balance(request):
    """
    Vista que genera una visualización del saldo de vacaciones para todos los empleados de una empresa activa.

    Permite consultar, calcular y mostrar en una tabla el saldo de vacaciones para cada contrato activo.
    Usa una fecha de corte opcional recibida por GET y toma como base un valor fijo (porcentaje de acumulación mensual)
    que se obtiene del concepto fijo con ID 9 en la base de datos.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que puede incluir el parámetro GET 'fecha' (en formato YYYY-MM-DD).
        Si no se incluye, se usa la fecha actual del sistema.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'vacation_balance.html' con el contexto:
        - 'contratos_empleados': Lista de diccionarios con los datos de contratos y vacaciones calculadas.
        - 'date': Fecha de corte usada para el cálculo.
        - 'visual': Booleano que indica si se pasó una fecha manual o no.

    Notes
    -----
    - Se filtran contratos activos con tipos específicos (1 al 4).
    - Se calcula el valor diario del salario base para mostrar también el valor parcial.
    """


    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    acumulados = {}

    concepto = Conceptosfijos.objects.filter(idfijo=7).values_list('valorfijo', flat=True).first()
    valor_fijo = float(concepto)

    fecha_param = request.GET.get('fecha')
    if fecha_param:
        date = datetime.strptime(fecha_param, "%Y-%m-%d").date()
        visual = True
    else:
        date = timezone.now().date()
        visual = False

    # 🔹 Función para limpiar y construir el nombre completo sin "no data"
    def construir_nombre_completo(data):
        def limpiar(valor):
            if valor is None:
                return ''
            valor_str = str(valor).strip()
            return '' if valor_str.lower() == 'no data' else valor_str

        nombre_completo = [
            limpiar(data.get('idempleado__papellido')),
            limpiar(data.get('idempleado__sapellido')),
            limpiar(data.get('idempleado__pnombre')),
            limpiar(data.get('idempleado__snombre')),
        ]
        return " ".join(filter(None, nombre_completo))

    fecha_actual = timezone.now().date() if fecha_param is None else datetime.strptime(fecha_param, "%Y-%m-%d").date()

    if fecha_param:
        contratos_empleados = (
            Contratos.objects.prefetch_related('idempleado')
            .filter(
                estadocontrato=1,
                tipocontrato__idtipocontrato__in=[1, 2, 3, 4],
                id_empresa__idempresa=idempresa
            )
            .values(
                'idempleado__docidentidad',
                'idempleado__sapellido',
                'idempleado__papellido',
                'idempleado__pnombre',
                'idempleado__snombre',
                'idempleado__idempleado',
                'idcontrato',
                'fechainiciocontrato',
                'salario'
            )
            .order_by('idempleado__papellido')
        )

        acumulados = {
            data['idcontrato']: {
                'contrato': data['idcontrato'],
                'documento': data['idempleado__docidentidad'],
                'empleado': construir_nombre_completo(data),
                'fechacontrato': data['fechainiciocontrato'],
                'salario': data['salario'],
                'parcial': round(float(data['salario']) / 30, 2),
            }
            for data in contratos_empleados
        }

        for contrato_id in acumulados.keys():
            contrato = Contratos.objects.get(idcontrato=contrato_id)
            vacaciones_data = calcular_vacaciones(contrato, valor_fijo, fecha_actual)
            acumulados[contrato_id].update(vacaciones_data)

    context = {
        'contratos_empleados': list(acumulados.values()),
        'date': date,
        'visual': visual,
    }

    return render(request, './companies/vacation_balance.html', context)


@login_required
@role_required('company','accountant')
def vacation_balance_download(request):
    """
    Vista protegida que permite descargar el saldo de vacaciones de empleados en formato Excel.

    Utiliza una fecha pasada por GET (`date`) para generar un reporte a través de la función `generate_balance_excel`,
    y retorna un archivo `.xlsx` con el nombre `vacaciones_saldo_<fecha>.xlsx`.

    Decoradores
    -----------
    @login_required
    @role_required('company','accountant')

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que debe incluir el parámetro GET 'date' en formato 'YYYY-MM-DD'.

    Returns
    -------
    HttpResponse
        - Si el parámetro está presente y es válido, devuelve un archivo Excel con el saldo de vacaciones.
        - Si falta el parámetro o la fecha no es válida, devuelve una respuesta de error 400.

    Raises
    ------
    HttpResponse
        En caso de errores de parámetros o formato de fecha, se retorna una respuesta con estado 400.
    """


    date_str = request.GET.get('date')

    # Verificar si date está presente
    if not date_str:
        return HttpResponse("Faltan parámetros.", status=400)

    # Convertir el string a un objeto datetime
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return HttpResponse("Formato de fecha inválido. Use YYYY-MM-DD.", status=400)

    # Generar el archivo Excel
    excel_data = generate_balance_excel(date_str)

    fecha_str = date.strftime("%Y-%m-%d")
    filename = f"vacaciones_saldo_{fecha_str}.xlsx"

    # Crear la respuesta HTTP con el archivo adjunto
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response