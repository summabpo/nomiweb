# apps/pila/utils/parse_plano_txt.py
"""
Parsea el contenido TXT PILA (archivo tipo 2) en filas para grid/Excel.
Posiciones 1-based según LAYOUT_REGISTRO_02.md y ARCHIVO_TIPO2_ENCABEZADO.md.
"""


def _slice(line: str, start: int, end: int) -> str:
    """Extrae substring 1-based (start y end inclusive)."""
    if not line or end < start:
        return ""
    return line[start - 1 : end].strip()


def parse_linea_01(line: str) -> dict:
    """Parsea registro tipo 01 (encabezado, 359 caracteres)."""
    if len(line) < 359:
        return {"tipo": "01", "error": "Longitud < 359", "raw": line}
    return {
        "tipo": "01",
        "secuencia": _slice(line, 3, 7),
        "razon_social": _slice(line, 8, 207),
        "tipo_doc": _slice(line, 208, 209),
        "nit": _slice(line, 210, 225),
        "tipo_planilla": _slice(line, 227, 227),
        "periodo_pago": _slice(line, 305, 311),
        "total_cotizantes": _slice(line, 339, 343),
        "valor_total_nomina": _slice(line, 344, 355),
    }


def parse_linea_02(line: str, num_linea: int) -> dict:
    """Parsea registro tipo 02 (detalle, 693 caracteres)."""
    if len(line) < 693:
        return {"num_linea": num_linea, "tipo": "02", "error": "Longitud < 693", "raw": line[:200]}
    return {
        "num_linea": num_linea,
        "tipo": "02",
        "secuencia": _slice(line, 3, 7),
        "tipo_doc": _slice(line, 8, 9),
        "numero_doc": _slice(line, 10, 17),
        "tipo_cotizante": _slice(line, 18, 19),
        "subtipo_cotizante": _slice(line, 20, 21),
        "cod_departamento": _slice(line, 32, 33),
        "cod_municipio": _slice(line, 34, 36),
        "primer_apellido": _slice(line, 37, 56),
        "segundo_apellido": _slice(line, 57, 86),
        "primer_nombre": _slice(line, 87, 106),
        "segundo_nombre": _slice(line, 107, 136),
        "marca_ing": _slice(line, 137, 137),
        "marca_ret": _slice(line, 138, 138),
        "marca_vsp": _slice(line, 143, 143),
        "marca_vst": _slice(line, 145, 145),
        "marca_sln": _slice(line, 146, 146),
        "marca_ige": _slice(line, 147, 147),
        "marca_lma": _slice(line, 148, 148),
        "marca_vac_lr": _slice(line, 149, 149),
        "fecha_ingreso": _slice(line, 515, 524),
        "fecha_retiro": _slice(line, 525, 534),
        "dias_pension": _slice(line, 184, 185),
        "dias_salud": _slice(line, 186, 187),
        "dias_arl": _slice(line, 188, 189),
        "dias_caja": _slice(line, 190, 191),
        "salario_basico": _slice(line, 192, 200),
        "ibc_pension": _slice(line, 202, 210),
        "ibc_salud": _slice(line, 211, 219),
        "ibc_arl": _slice(line, 220, 228),
        "ibc_caja": _slice(line, 229, 237),
        "cod_afp": _slice(line, 154, 159),
        "cod_eps": _slice(line, 166, 171),
        "cod_ccf": _slice(line, 178, 183),
    }


def parse_plano_txt(contenido_bytes: bytes) -> list[dict]:
    """
    Decodifica el TXT (ISO-8859-1) y devuelve lista de filas parseadas.
    Primera fila: encabezado (01). Resto: detalle (02).
    """
    try:
        texto = contenido_bytes.decode("iso-8859-1")
    except Exception:
        texto = contenido_bytes.decode("utf-8", errors="replace")
    lineas = [ln for ln in texto.replace("\r\n", "\n").replace("\r", "\n").split("\n") if ln.strip()]
    filas = []
    for i, ln in enumerate(lineas):
        num = i + 1
        if len(ln) == 359:
            filas.append(parse_linea_01(ln))
        elif len(ln) == 693:
            filas.append(parse_linea_02(ln, num))
        else:
            filas.append({"num_linea": num, "tipo": "?", "error": f"Longitud {len(ln)}", "raw": ln[:80]})
    return filas
