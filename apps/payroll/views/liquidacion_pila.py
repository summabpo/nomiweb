from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from apps.components.decorators import role_required
from apps.pila.services.payload_builder import build_payload_pila_minimo
from apps.pila.services.pila_cliente import (
    crear_planilla,
    descargar_archivo,
    PilaServiceError,
)


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

                # Usamos force=True como en el comando de prueba para permitir recrear planilla si existe
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
    Reutiliza apps.pila.services.pila_cliente.descargar_archivo.
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



