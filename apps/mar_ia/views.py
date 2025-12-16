from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from openai import OpenAIError, APIError, APITimeoutError
import json
import re
import logging

from .services import (
    get_active_contract,
    get_last_nomina_net_summary,
    get_nomina_concepts_detail,
    build_6_months_payroll_context,
    build_loans_context,  # Agregar esta importación
    build_libranzas_context,
    build_contract_employee_context,
)
from .openai_client import client
from .models import MarIaConsulta  # Importar el modelo

logger = logging.getLogger(__name__)

# Constantes de configuración
MAX_QUESTION_LENGTH = 100
MAX_TOKENS_PER_SESSION = 20000
MAX_TOKENS_PER_REQUEST = 1000

# Solo mantener regex para consultas MUY básicas y rápidas
PAGO_ULTIMA_REGEX = re.compile(r"^(cu(a|á)nto.*pag.*(última|ultima|último|ultimo)|última quincena|ultima quincena)$", re.I)
CONCEPTOS_ULTIMA_REGEX = re.compile(r"^(conceptos|desglose|detalle).*(última|ultima|último|ultimo)", re.I)


def save_consulta_to_db(user, pregunta, respuesta, tipo_respuesta='ia', tokens_usados=0, error_tipo=None, idcontrato=None):
    """
    Guarda la consulta en la base de datos para análisis
    Se ejecuta de forma silenciosa para no bloquear la respuesta
    """
    try:
        MarIaConsulta.objects.create(
            user=user,
            pregunta=pregunta[:500] if len(pregunta) > 500 else pregunta,
            respuesta=respuesta[:5000] if len(respuesta) > 5000 else respuesta,
            tokens_usados=tokens_usados,
            tipo_respuesta=tipo_respuesta,
            error_tipo=error_tipo,
            idcontrato=idcontrato
        )
    except Exception as e:
        # No fallar la respuesta si hay error guardando
        logger.error(f"Error guardando consulta MAR-IA en BD: {str(e)}")


def get_session_tokens(request):
    """Obtiene el contador de tokens usado en esta sesión"""
    return request.session.get('mar_ia_tokens_used', 0)


def add_session_tokens(request, tokens_used):
    """Agrega tokens usados a la sesión"""
    current = get_session_tokens(request)
    request.session['mar_ia_tokens_used'] = current + tokens_used
    request.session.modified = True


def reset_session_tokens(request):
    """Resetea el contador de tokens (útil para testing o reset manual)"""
    if 'mar_ia_tokens_used' in request.session:
        del request.session['mar_ia_tokens_used']
        request.session.modified = True


@csrf_exempt
@require_POST
@login_required
def chat_api(request):
    # Validar JSON
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        error_msg = "No pude leer tu mensaje. Intenta de nuevo."
        save_consulta_to_db(
            request.user,
            body.get("question", "")[:500] if body else "",
            error_msg,
            tipo_respuesta='error',
            error_tipo='invalid_json'
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "invalid_json"
        }, status=400)

    pregunta = (body.get("question") or "").strip()
    
    # Validar que la pregunta no esté vacía
    if not pregunta:
        error_msg = "Por favor, escribe una pregunta."
        save_consulta_to_db(
            request.user,
            "",
            error_msg,
            tipo_respuesta='error',
            error_tipo='empty_question'
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "empty_question"
        }, status=400)
    
    # Validar longitud de pregunta
    if len(pregunta) > MAX_QUESTION_LENGTH:
        error_msg = f"Tu pregunta es muy larga. Por favor, limítala a {MAX_QUESTION_LENGTH} caracteres."
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            error_msg,
            tipo_respuesta='error',
            error_tipo='question_too_long'
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "question_too_long",
            "max_length": MAX_QUESTION_LENGTH,
            "current_length": len(pregunta)
        }, status=400)

    # Validar límite de tokens por sesión
    tokens_used = get_session_tokens(request)
    if tokens_used >= MAX_TOKENS_PER_SESSION:
        error_msg = (
            f"Has alcanzado el límite de uso para esta sesión. "
            f"Por favor, recarga la página o inicia sesión nuevamente."
        )
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            error_msg,
            tipo_respuesta='error',
            error_tipo='session_limit_exceeded'
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "session_limit_exceeded",
            "tokens_used": tokens_used,
            "max_tokens": MAX_TOKENS_PER_SESSION
        }, status=429)

    # Obtener contrato activo
    idcontrato = get_active_contract(request.user)
    if not idcontrato:
        error_msg = "No se encontró un contrato activo asociado a tu cuenta."
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            error_msg,
            tipo_respuesta='error',
            error_tipo='no_active_contract'
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "no_active_contract"
        })

    # NIVEL 1: Solo respuestas directas para consultas MUY básicas (sin tokens)
    pregunta_lower = pregunta.lower().strip()
    
    # Solo si pregunta EXACTAMENTE por la última nómina
    if PAGO_ULTIMA_REGEX.match(pregunta_lower):
        resumen = get_last_nomina_net_summary(idcontrato)
        if not resumen:
            respuesta = "No encontré una nómina grabada reciente."
            save_consulta_to_db(
                request.user,
                pregunta[:500],
                respuesta,
                tipo_respuesta='directa',
                idcontrato=idcontrato
            )
            return JsonResponse({
                "answer": respuesta
            })

        respuesta = (
            f"En tu última quincena ({resumen['nombrenomina']}), "
            f"el neto pagado fue **${resumen['neto']:,}**. "
            f"Devengos: ${resumen['devengos']:,} · "
            f"Descuentos: ${resumen['descuentos']:,}."
        )
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            respuesta,
            tipo_respuesta='directa',
            idcontrato=idcontrato
        )
        return JsonResponse({
            "answer": respuesta
        })

    # Solo si pregunta EXACTAMENTE por conceptos de la última nómina
    if CONCEPTOS_ULTIMA_REGEX.match(pregunta_lower):
        resumen = get_last_nomina_net_summary(idcontrato)
        if not resumen:
            respuesta = "No encontré una nómina grabada reciente para sacar el desglose."
            save_consulta_to_db(
                request.user,
                pregunta[:500],
                respuesta,
                tipo_respuesta='directa',
                idcontrato=idcontrato
            )
            return JsonResponse({
                "answer": respuesta
            })

        conceptos = get_nomina_concepts_detail(idcontrato, resumen["idnomina"], limit=40)
        if not conceptos:
            respuesta = "No encontré conceptos para esa nómina."
            save_consulta_to_db(
                request.user,
                pregunta[:500],
                respuesta,
                tipo_respuesta='directa',
                idcontrato=idcontrato
            )
            return JsonResponse({
                "answer": respuesta
            })

        lines = [f"Desglose de conceptos en **{resumen['nombrenomina']}** (ID {resumen['idnomina']}):"]
        for c in conceptos:
            lines.append(f"• {c['nombre']}: ${c['valor']:,}")

        respuesta = "\n".join(lines)
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            respuesta,
            tipo_respuesta='directa',
            idcontrato=idcontrato
        )
        return JsonResponse({"answer": respuesta})

    # NIVEL 2: Todo lo demás va a la IA con contexto completo
    try:
        contexto_nominas = build_6_months_payroll_context(request.user)
        contexto_prestamos = build_loans_context(request.user)  # Agregar esta línea
        contexto_libranzas = build_libranzas_context(request.user)
        contexto_contrato = build_contract_employee_context(request.user)
        
        # Combinar todos los contextos
        contexto_completo = f"{contexto_nominas}\n\n{contexto_prestamos}\n\n{contexto_libranzas}\n\n{contexto_contrato}"
        
        # Preparar mensajes para OpenAI con instrucciones mejoradas
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres MAR-IA, un asistente especializado en nómina, préstamos, libranzas y contratos.\n\n"
                    "INFORMACIÓN CRÍTICA SOBRE SALARIO INTEGRAL:\n"
                    "- Si el empleado tiene SALARIO INTEGRAL, los descuentos (EPS, AFP, etc.) NO se calculan "
                    "como un porcentaje simple del salario básico.\n"
                    "- En salario integral, el salario ya incluye todas las prestaciones sociales, por lo que "
                    "los descuentos se calculan sobre el salario integral completo según normativa específica.\n"
                    "- Si ves 'Salario Integral' en los conceptos, los valores de descuentos mostrados son "
                    "los correctos y NO debes recalcularlos como porcentaje del salario básico.\n\n"
                    "FÓRMULAS DE CÁLCULO DE DESCUENTOS:\n"
                    "1. EPS (Salud): Se calcula como un porcentaje de la base de seguridad social.\n"
                    "   - En salario integral: sobre el salario integral ajustado por factor integral.\n"
                    "   - El porcentaje típico es alrededor del 4% pero puede variar.\n\n"
                    "2. AFP (Pensión): Se calcula como un porcentaje de la base de seguridad social.\n"
                    "   - Similar a EPS, sobre la base de seguridad social.\n"
                    "   - El porcentaje típico es alrededor del 4% pero puede variar.\n\n"
                    "3. FSP (Fondo de Solidaridad Pensional):\n"
                    "   - Se calcula como un porcentaje sobre el 70% de la base de seguridad social.\n"
                    "   - Fórmula: FSP = (Base de Seguridad Social × 0.70) × (Porcentaje FSP / 100)\n"
                    "   - El porcentaje FSP varía según rangos de salario (entre 4 y 20+ salarios mínimos).\n"
                    "   - Solo se aplica si la base supera 4 salarios mínimos.\n"
                    "   - Ejemplo: Si base es $9,252,888 y FSP es 1%, entonces:\n"
                    "     FSP = ($9,252,888 × 0.70) × 0.01 = $6,477,021.6 × 0.01 = $64,770\n\n"
                    "IMPORTANTE:\n"
                    "- Los valores mostrados en las nóminas son los correctos y ya están calculados.\n"
                    "- Si te preguntan cómo se calculó un descuento, usa las fórmulas anteriores.\n"
                    "- Para FSP, SIEMPRE menciona que se calcula sobre el 70% de la base.\n\n"
                    "Tienes acceso a información completa de:\n"
                    "1. Las nóminas de los últimos 6 meses, incluyendo TODOS los conceptos\n"
                    "2. Los préstamos activos del empleado (con saldo pendiente y cuotas pagadas)\n"  # Actualizar esta línea
                    "3. Las libranzas activas del empleado\n"
                    "4. Información del contrato laboral y datos personales\n\n"
                    "INSTRUCCIONES:\n"
                    "1. Usa SOLO la información proporcionada en el contexto.\n"
                    "2. Para preguntas sobre períodos específicos, filtra las nóminas por fecha.\n"
                    "3. Para preguntas sobre conceptos específicos, busca ese concepto en todas las nóminas.\n"
                    "4. Para preguntas sobre CÓMO SE CALCULÓ un descuento:\n"
                    "   - Identifica si es salario integral o no\n"
                    "   - Para FSP: explica que es (Base × 0.70) × (Porcentaje FSP / 100)\n"
                    "   - Para EPS/AFP: explica que es Base × (Porcentaje / 100)\n"
                    "   - Usa los valores reales de las nóminas para mostrar el cálculo\n"
                    "5. Para preguntas sobre PRÉSTAMOS, usa la información de préstamos proporcionada.\n"  # Agregar esta línea
                    "6. Para preguntas sobre libranzas, usa la información de libranzas proporcionada.\n"
                    "7. Para preguntas sobre el contrato o datos personales, usa la información del contrato proporcionada.\n"
                    "8. Si un concepto no aparece en el contexto, di claramente que no se encontró.\n"
                    "9. Responde de forma clara, amigable y profesional.\n"
                    "10. Incluye montos formateados con separadores de miles (ej: $1,500,000).\n"
                    "11. Si la pregunta es sobre un período más largo de 6 meses, indica que solo tienes "
                    "información de los últimos 6 meses."
                )
            },
            {
                "role": "system",
                "content": contexto_completo
            },
            {
                "role": "user",
                "content": pregunta
            }
        ]

        # Llamar a OpenAI con límite de tokens
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            max_tokens=MAX_TOKENS_PER_REQUEST,
        )

        # Obtener respuesta y tokens usados
        answer = response.choices[0].message.content
        tokens_used_in_request = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        # Actualizar contador de sesión
        add_session_tokens(request, tokens_used_in_request)
        
        # Guardar en BD para análisis
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            answer[:5000] if len(answer) > 5000 else answer,
            tipo_respuesta='ia',
            tokens_usados=tokens_used_in_request,
            idcontrato=idcontrato
        )
        
        # Log para monitoreo
        logger.info(
            f"MAR-IA request - User: {request.user.id}, "
            f"Question: {pregunta[:50]}, "
            f"Tokens used: {tokens_used_in_request}, "
            f"Session total: {get_session_tokens(request)}"
        )

        return JsonResponse({
            "answer": answer,
            "tokens_used": tokens_used_in_request,
            "session_tokens_remaining": max(0, MAX_TOKENS_PER_SESSION - get_session_tokens(request))
        })

    except APITimeoutError:
        logger.error(f"OpenAI timeout for user {request.user.id}")
        error_msg = "El servicio está tardando más de lo esperado. Por favor, intenta de nuevo en un momento."
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            error_msg,
            tipo_respuesta='error',
            error_tipo='timeout',
            idcontrato=idcontrato
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "timeout"
        }, status=504)

    except APIError as e:
        logger.error(f"OpenAI API error for user {request.user.id}: {str(e)}")
        error_msg = "Hubo un problema al procesar tu pregunta. Por favor, intenta de nuevo más tarde."
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            error_msg,
            tipo_respuesta='error',
            error_tipo='api_error',
            idcontrato=idcontrato
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "api_error"
        }, status=500)

    except OpenAIError as e:
        logger.error(f"OpenAI error for user {request.user.id}: {str(e)}")
        error_msg = "Ocurrió un error inesperado. Por favor, intenta de nuevo."
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            error_msg,
            tipo_respuesta='error',
            error_tipo='openai_error',
            idcontrato=idcontrato
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "openai_error"
        }, status=500)

    except Exception as e:
        logger.exception(f"Unexpected error in MAR-IA chat for user {request.user.id}: {str(e)}")
        error_msg = "Ocurrió un error inesperado. Por favor, contacta al administrador si el problema persiste."
        save_consulta_to_db(
            request.user,
            pregunta[:500],
            error_msg,
            tipo_respuesta='error',
            error_tipo='unexpected_error',
            idcontrato=idcontrato
        )
        return JsonResponse({
            "answer": error_msg,
            "error": "unexpected_error"
        }, status=500)