from datetime import date
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from apps.components.decorators import role_required
from apps.pila.services.payload_builder import build_payload_pila_minimo
from apps.pila.services.pila_cliente import (
    crear_planilla,
    descargar_archivo,
    descargar_payload_json,
    PilaServiceError,
)
from apps.pila.utils.parse_plano_txt import parse_plano_txt


@login_required
@role_required("accountant")
def liquidacion_pila(request):
    """
    Pantalla inicial para la liquidación PILA:
    - Toma la empresa actual desde la sesión (idempresa, nombre_empresa).
    - Permite escoger año, mes y tipo de planilla (E/K).
    - En POST genera el payload y crea la planilla en el microservicio PILA.
    """
    usuario = request.session.get("usuario", {})
    empresa_id = usuario.get("idempresa")
    empresa_nombre = usuario.get("nombre_empresa", "")

    today = date.today()
    current_year = today.year
    years = [current_year - 1, current_year, current_year + 1]

    months = [
        {"value": "01", "label": "Enero"},
        {"value": "02", "label": "Febrero"},
        {"value": "03", "label": "Marzo"},
        {"value": "04", "label": "Abril"},
        {"value": "05", "label": "Mayo"},
        {"value": "06", "label": "Junio"},
        {"value": "07", "label": "Julio"},
        {"value": "08", "label": "Agosto"},
        {"value": "09", "label": "Septiembre"},
        {"value": "10", "label": "Octubre"},
        {"value": "11", "label": "Noviembre"},
        {"value": "12", "label": "Diciembre"},
    ]

    plan_types = [
        {"value": "E", "label": "E - Empleados"},
        {"value": "K", "label": "K - Estudiantes (Planilla K)"},
    ]

    contexto = {
        "empresa_id": empresa_id,
        "empresa_nombre": empresa_nombre,
        "years": years,
        "months": months,
        "plan_types": plan_types,
    }

    if request.method == "POST":
        year = request.POST.get("year")
        month = request.POST.get("month")
        tipo_planilla = request.POST.get("tipo_planilla")

        contexto.update(
            {
                "selected_year": year,
                "selected_month": month,
                "selected_tipo_planilla": tipo_planilla,
            }
        )

        if not empresa_id:
            messages.error(request, "No hay empresa seleccionada en la sesión.")
        elif not (year and month and tipo_planilla):
            messages.error(request, "Debe seleccionar año, mes y tipo de planilla.")
        else:
            periodo = f"{year}-{month}"
            try:
                payload = build_payload_pila_minimo(
                    empresa_id_interno=empresa_id,
                    periodo=periodo,
                )

                respuesta = crear_planilla(payload, force=True)

                messages.success(
                    request,
                    f"Planilla PILA generada y enviada correctamente para el periodo {periodo}.",
                )
                contexto["resultado_planilla"] = respuesta
                contexto["planilla_id"] = respuesta.get("planilla_id")
                contexto["periodo"] = periodo
                contexto["tipo_planilla"] = tipo_planilla
            except PilaServiceError as e:
                messages.error(
                    request,
                    f"Error del servicio PILA: {e}",
                )
            except Exception as e:  # noqa: BLE001
                messages.error(
                    request,
                    f"Error al generar el payload o crear la planilla: {e}",
                )

    return render(request, "./payroll/liquidacion_pila.html", contexto)


@login_required
@role_required("accountant")
def descargar_pila_txt(request: HttpRequest, planilla_id: int) -> HttpResponse:
    """
    Descarga el archivo TXT PILA generado por el microservicio.
    """
    tipo_planilla = request.GET.get("tipo_planilla") or None

    try:
        contenido = descargar_archivo(planilla_id, tipo_planilla=tipo_planilla)
    except PilaServiceError as e:
        messages.error(request, f"Error al descargar archivo PILA: {e}")
        return redirect("payroll:pila_liquidacion")
    except Exception as e:  # noqa: BLE001
        messages.error(request, f"Error inesperado al descargar archivo PILA: {e}")
        return redirect("payroll:pila_liquidacion")

    sufijo = f"_{tipo_planilla}" if tipo_planilla else ""
    filename = f"PILA_{planilla_id}{sufijo}.txt"

    response = HttpResponse(
        contenido,
        content_type="text/plain; charset=iso-8859-1",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Content-Length"] = len(contenido)
    return response


def _get_planilla_txt_filas(planilla_id: int, tipo_planilla: str | None):
    """Obtiene el TXT del microservicio y lo parsea en filas para grid/Excel."""
    contenido = descargar_archivo(planilla_id, tipo_planilla=tipo_planilla)
    return parse_plano_txt(contenido)


@login_required
@role_required("accountant")
def vista_plano_pila(request: HttpRequest, planilla_id: int):
    """
    Muestra el contenido del plano TXT PILA en una grid (DataTable).
    Incluye botón para descargar en Excel.
    """
    tipo_planilla = request.GET.get("tipo_planilla") or None
    try:
        filas = _get_planilla_txt_filas(planilla_id, tipo_planilla)
    except PilaServiceError as e:
        messages.error(request, f"Error al obtener plano PILA: {e}")
        return redirect("payroll:pila_liquidacion")
    except Exception as e:  # noqa: BLE001
        messages.error(request, f"Error inesperado: {e}")
        return redirect("payroll:pila_liquidacion")

    encabezado = next((f for f in filas if f.get("tipo") == "01"), None)
    filas_detalle = sorted(
        [f for f in filas if f.get("tipo") == "02"],
        key=lambda f: (f.get("primer_apellido") or "", f.get("segundo_apellido") or "", f.get("primer_nombre") or ""),
    )

    contexto = {
        "planilla_id": planilla_id,
        "tipo_planilla": tipo_planilla,
        "encabezado": encabezado,
        "filas": filas_detalle,
    }
    return render(request, "./payroll/vista_plano_pila.html", contexto)


@login_required
@role_required("accountant")
def descargar_pila_json(request: HttpRequest, planilla_id: int) -> HttpResponse:
    """
    Descarga el payload JSON generado en la liquidación de esta planilla PILA.
    """
    try:
        contenido = descargar_payload_json(planilla_id)
    except PilaServiceError as e:
        messages.error(request, f"Error al obtener JSON PILA: {e}")
        return redirect("payroll:pila_liquidacion")
    except Exception as e:
        messages.error(request, f"Error inesperado: {e}")
        return redirect("payroll:pila_liquidacion")

    response = HttpResponse(
        contenido,
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="PILA_payload.json"'
    return response


@login_required
@role_required("accountant")
def descargar_pila_excel(request: HttpRequest, planilla_id: int) -> HttpResponse:
    """
    Descarga el contenido del plano TXT PILA en formato Excel (.xlsx).
    """
    tipo_planilla = request.GET.get("tipo_planilla") or None
    try:
        filas = _get_planilla_txt_filas(planilla_id, tipo_planilla)
    except PilaServiceError as e:
        messages.error(request, f"Error al obtener plano PILA: {e}")
        return redirect("payroll:pila_liquidacion")
    except Exception as e:  # noqa: BLE001
        messages.error(request, f"Error inesperado: {e}")
        return redirect("payroll:pila_liquidacion")

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError:
        messages.error(request, "No está disponible la exportación a Excel (openpyxl).")
        from django.urls import reverse
        url = reverse("payroll:pila_vista_txt", args=[planilla_id])
        if tipo_planilla:
            url += f"?tipo_planilla={tipo_planilla}"
        return redirect(url)

    wb = Workbook()
    # Hoja encabezado (solo filas tipo 01)
    filas_01 = [f for f in filas if f.get("tipo") == "01"]
    filas_02 = sorted(
        [f for f in filas if f.get("tipo") == "02"],
        key=lambda f: (f.get("primer_apellido") or "", f.get("segundo_apellido") or "", f.get("primer_nombre") or ""),
    )

    if filas_01:
        ws1 = wb.active
        ws1.title = "Encabezado"
        headers_01 = ["tipo", "secuencia", "razon_social", "tipo_doc", "nit", "tipo_planilla", "periodo_pago", "total_cotizantes", "valor_total_nomina"]
        ws1.append(headers_01)
        for row in filas_01:
            ws1.append([str(row.get(h, "")) for h in headers_01])
        for cell in ws1[1]:
            cell.font = Font(bold=True)

    headers_02 = [
        "num_linea", "tipo", "secuencia", "tipo_doc", "numero_doc",
        "primer_apellido", "segundo_apellido", "primer_nombre", "segundo_nombre",
        "marca_ing", "marca_ret", "fecha_ingreso", "fecha_retiro", "marca_vsp", "marca_vst",
        "dias_pension", "dias_salud", "dias_arl", "dias_caja",
        "salario_basico", "ibc_pension", "ibc_salud", "ibc_arl", "ibc_caja",
        "marca_sln", "marca_ige", "marca_lma", "marca_vac_lr",
        "cod_afp", "cod_eps", "cod_ccf",
        "tarifa_arl", "centro_trabajo",
    ]
    if filas_01:
        ws2 = wb.create_sheet("Detalle", index=1)
    else:
        ws2 = wb.active
        ws2.title = "Detalle"
    ws2.append(headers_02)
    for row in filas_02:
        ws2.append([str(row.get(h, "")) for h in headers_02])
    for cell in ws2[1]:
        cell.font = Font(bold=True)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    sufijo = f"_{tipo_planilla}" if tipo_planilla else ""
    filename = f"PILA_plano_{planilla_id}{sufijo}.xlsx"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
