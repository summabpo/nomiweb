# nomiweb/apps/pila/services/pila_client.py
import requests
from django.conf import settings


class PilaServiceError(Exception):
    pass


def _timeouts():
    connect = int(getattr(settings, "PILA_TIMEOUT_CONNECT", 3))
    read = int(getattr(settings, "PILA_TIMEOUT_READ", 15))
    return (connect, read)


def _headers():
    token = getattr(settings, "PILA_SERVICE_TOKEN", "")
    if not token:
        raise PilaServiceError("Falta PILA_SERVICE_TOKEN en settings/.env")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def crear_planilla(payload: dict, force: bool = False) -> dict:
    base = getattr(settings, "PILA_BASE_URL", "").rstrip("/")
    if not base:
        raise PilaServiceError("Falta PILA_BASE_URL in settings/.env")

    url = f"{base}/api/v1/pila/planillas/"
    if force:
        url += "?force=1"
    r = requests.post(url, json=payload, headers=_headers(), timeout=_timeouts())

    # Errores HTTP (400/401/409/500) con mensaje
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:
            detail = {"detail": r.text}
        raise PilaServiceError(f"PILA {r.status_code}: {detail}")

    return r.json()


def consultar_planilla(planilla_id: int) -> dict:
    base = getattr(settings, "PILA_BASE_URL", "").rstrip("/")
    url = f"{base}/api/v1/pila/planillas/{planilla_id}/"
    r = requests.get(url, headers=_headers(), timeout=_timeouts())

    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:
            detail = {"detail": r.text}
        raise PilaServiceError(f"PILA {r.status_code}: {detail}")

    return r.json()


def descargar_archivo(planilla_id: int, tipo_planilla: str | None = None) -> bytes:
    """
    Descarga el archivo TXT PILA.
    tipo_planilla: "K" para solo estudiantes, "E" para solo no estudiantes, None para todos.
    """
    base = getattr(settings, "PILA_BASE_URL", "").rstrip("/")
    url = f"{base}/api/v1/pila/planillas/{planilla_id}/archivo/"
    if tipo_planilla and tipo_planilla.upper() in ("K", "E"):
        url += f"?tipo_planilla={tipo_planilla.upper()}"
    r = requests.get(url, headers=_headers(), timeout=_timeouts())

    if r.status_code >= 400:
        raise PilaServiceError(f"PILA {r.status_code}: {r.text}")

    return r.content