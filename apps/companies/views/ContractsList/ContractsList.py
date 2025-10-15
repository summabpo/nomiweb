from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Contratos , Contratosemp , Ciudades
from apps.components.decorators import custom_login_required ,custom_permission
from openpyxl import Workbook
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from .generate_docu import generate_contract_excel,generate_contract_start_excel


@login_required
@role_required('company', 'accountant')
def startCompanies(request):
    """
    Muestra la lista de empleados activos con sus respectivos contratos.

    Esta vista recupera los contratos activos de los empleados de la empresa a la que el usuario pertenece,
    formatea la información y la presenta en una tabla. Los empleados son ordenados por apellido y se incluye
    información como el salario, el cargo, y la fecha de inicio del contrato.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la sesión del usuario.

    Returns
    -------
    render : HttpResponse
        Respuesta con la vista de la lista de empleados y sus contratos.

    See Also
    --------
    Contratos : Modelo que representa los contratos de los empleados.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """

    # --- Función auxiliar de limpieza ---
    def clean_value(value):
        """
        Limpia valores tipo texto que indiquen falta de datos.
        Ejemplo: 'no data', 'sin dato', 'n/a', 'none', 'ninguno'
        """
        if isinstance(value, str):
            if value.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"]:
                return ""
        return value

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    contratos_empleados = (
        Contratos.objects
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede', 'centrotrabajo')
        .order_by('idempleado__papellido')
        .filter(estadocontrato=1, id_empresa=idempresa)
        .values(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'fechainiciocontrato', 'cargo__nombrecargo', 'salario',
            'idcosto__nomcosto', 'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl',
            'idempleado__idempleado', 'idempleado__sapellido', 'idcontrato'
        )
    )

    empleados = []
    for contrato in contratos_empleados:
        empleado_data = {
            'documento': clean_value(contrato.get('idempleado__docidentidad', '')),
            'nombre': ' '.join(filter(None, map(clean_value, [
                contrato.get('idempleado__papellido', ''),
                contrato.get('idempleado__sapellido', ''),
                contrato.get('idempleado__pnombre', ''),
                contrato.get('idempleado__snombre', '')
            ]))),
            'fechainiciocontrato': clean_value(contrato.get('fechainiciocontrato', '')),
            'cargo': clean_value(contrato.get('cargo__nombrecargo', '')),
            'salario': f"{contrato['salario'] if contrato['salario'] is not None else 0:,.0f}".replace(',', '.'),
            'centrocostos': clean_value(contrato.get('idcosto__nomcosto', '')),
            'tipocontrato': clean_value(contrato.get('tipocontrato__tipocontrato', '')),
            'tarifaARL': clean_value(contrato.get('centrotrabajo__tarifaarl', '')),
            'idempleado': contrato.get('idempleado__idempleado', ''),
            'idcontrato': contrato.get('idcontrato', ''),
        }

        empleados.append(empleado_data)

    return render(request, './companies/ActiveList.html', {
        'empleados': empleados,
        'user': request.user
    })




@login_required
@role_required('company','accountant')
def exportar_excel0(request):
    """
    Exporta los contratos activos en formato Excel.

    Esta vista genera un archivo Excel con la información de los contratos activos de los empleados y lo
    devuelve como una respuesta HTTP para su descarga.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la sesión del usuario.

    Returns
    -------
    HttpResponse
        Respuesta HTTP que contiene el archivo Excel generado.

    See Also
    --------
    generate_contract_start_excel : Función que genera el archivo Excel con los contratos activos.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    excel_data = generate_contract_start_excel(idempresa)
    file_name = f"contratos_activos.xlsx"
    
    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

@login_required
@role_required('company','accountant')
def exportar_excel1(request):
    """
    Exporta los contratos activos con todos los campos en formato Excel.

    Esta vista genera un archivo Excel con toda la información disponible de los contratos activos de los empleados
    y lo devuelve como una respuesta HTTP para su descarga.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la sesión del usuario.

    Returns
    -------
    HttpResponse
        Respuesta HTTP que contiene el archivo Excel generado.

    See Also
    --------
    generate_contract_excel : Función que genera el archivo Excel con todos los campos de los contratos activos.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    excel_data = generate_contract_excel(idempresa)
    file_name = f"contratos_activos_todos_los_campos.xlsx"
    
    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response





@login_required
@role_required('company', 'accountant')
def exportar_excel2(request):
    """
    Exporta la información de las hojas de vida de los empleados activos en formato Excel.

    - Elimina cualquier texto 'no data' (sin importar mayúsculas/minúsculas).
    - Los campos sin información se dejan en blanco.
    - Incluye información básica y laboral de cada empleado activo.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')

    # Cachear las ciudades en un diccionario
    city_map = {c.idciudad: c.ciudad for c in Ciudades.objects.all()}

    # Consultar empleados activos
    empleados = Contratosemp.objects.filter(
        estadocontrato=1, id_empresa_id=idempresa
    ).values_list(
        'docidentidad', 'tipodocident__codigo', 'pnombre', 'snombre',
        'papellido', 'sapellido', 'fechanac', 'ciudadnacimiento',
        'telefonoempleado', 'direccionempleado', 'sexo', 'email',
        'ciudadresidencia', 'estadocivil', 'idempleado', 'paisnacimiento',
        'paisresidencia', 'celular', 'profesion', 'niveleducativo',
        'gruposanguineo', 'estatura', 'peso', 'fechaexpedicion',
        'ciudadexpedicion', 'dotpantalon', 'dotcamisa', 'dotzapatos',
        'estrato', 'numlibretamil', 'estadocontrato'
    )

    # Función de limpieza para cada valor
    def clean_value(value):
        if not value:
            return ""
        if isinstance(value, str) and value.strip().lower() == "no data":
            return ""
        return value

    # Crear libro de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Hojas de Vida"

    # Encabezados
    headers = [
        'Documento', 'Tipo Documento', 'Nombre Completo', 'Fecha Nacimiento', 'Ciudad Nacimiento',
        'Teléfono', 'Dirección', 'Sexo', 'Email', 'Ciudad Residencia', 'Estado Civil', 'ID Empleado',
        'País Nacimiento', 'País Residencia', 'Celular', 'Profesión', 'Nivel Educativo',
        'Grupo Sanguíneo', 'Estatura', 'Peso', 'Fecha Expedición', 'Ciudad Expedición',
        'Talla Pantalón', 'Talla Camisa', 'Talla Zapatos', 'Estrato', 'Libreta Militar',
        'Estado Contrato'
    ]
    ws.append(headers)

    # Procesar datos
    for emp in empleados:
        (
            doc, tipo_doc, pnom, snom, pap, sap, fechanac, ciudad_nac, tel,
            dir_emp, sexo, email, ciudad_res, estado_civil, idemp, pais_nac,
            pais_res, cel, profesion, nivel, grupo, estatura, peso,
            fechaexp, ciudad_exp, pant, cam, zap, estrato, libreta, estado_cto
        ) = emp

        
        def limpiar_texto(valor):
            if isinstance(valor, str) and valor.strip().lower() == "no data":
                return ""
            return valor or ""

        nombre = " ".join(filter(None, [
            limpiar_texto(pap),
            limpiar_texto(sap),
            limpiar_texto(pnom),
            limpiar_texto(snom)
        ])).strip()


        # Función para formatear fechas
        def format_date(value):
            if isinstance(value, datetime):
                return value.strftime('%Y-%m-%d')
            elif isinstance(value, str):
                try:
                    return datetime.strptime(value, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    return ''
            return ''

        fechanac_fmt = format_date(fechanac)
        fechaexp_fmt = format_date(fechaexp)

        # Resolver ciudades
        ciudad_nac_nom = city_map.get(ciudad_nac, '') if ciudad_nac else ''
        ciudad_res_nom = city_map.get(ciudad_res, '') if ciudad_res else ''
        ciudad_exp_nom = city_map.get(ciudad_exp, '') if ciudad_exp else ''

        # Construir fila con limpieza
        row = [clean_value(x) for x in [
            doc, tipo_doc, nombre, fechanac_fmt, ciudad_nac_nom,
            tel, dir_emp, sexo, email, ciudad_res_nom, estado_civil,
            idemp, pais_nac, pais_res, cel, profesion, nivel, grupo,
            estatura, peso, fechaexp_fmt, ciudad_exp_nom, pant, cam,
            zap, estrato, libreta, estado_cto
        ]]
        
        
        ws.append(row)

    # Ajustar ancho de columnas automáticamente
    for column_cells in ws.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = max_length + 2

    # Guardar en memoria y devolver como descarga
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="hojas_de_vida.xlsx"'
    return response






















































































