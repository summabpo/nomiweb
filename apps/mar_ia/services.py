from django.db import connection
from datetime import datetime, timedelta


# -------------------------------------------------
# CONTRATO ACTIVO DEL EMPLEADO
# -------------------------------------------------
def get_active_contract(user):
    idempleado = getattr(user, "id_empleado_id", None)
    if not idempleado:
        return None

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT idcontrato
            FROM contratos
            WHERE idempleado_id = %s
              AND estadocontrato = 1
            ORDER BY fechainiciocontrato DESC
            LIMIT 1;
        """, [idempleado])
        row = cursor.fetchone()

    return row[0] if row else None


# -------------------------------------------------
# NÓMINAS DE LOS ÚLTIMOS 6 MESES
# -------------------------------------------------
def get_nominas_last_6_months(idcontrato):
    """
    Obtiene todas las nóminas de los últimos 6 meses basado en fechapago
    """
    if not idcontrato:
        return []

    # Calcular fecha límite (6 meses atrás)
    fecha_limite = datetime.now() - timedelta(days=180)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT
                cn.idnomina,
                cn.nombrenomina,
                cn.fechapago,
                cn.fechainicial,
                cn.fechafinal
            FROM nomina n
            JOIN crearnomina cn
              ON cn.idnomina = n.idnomina_id
            WHERE n.idcontrato_id = %s
              AND cn.estadonomina = FALSE
              AND (cn.fechapago >= %s OR cn.fechapago IS NULL)
            ORDER BY cn.fechapago DESC NULLS LAST, cn.idnomina DESC;
        """, [idcontrato, fecha_limite])
        rows = cursor.fetchall()

    return [
        {
            "idnomina": r[0],
            "nombrenomina": r[1],
            "fechapago": r[2],
            "fechainicial": r[3],
            "fechafinal": r[4]
        }
        for r in rows
    ]


# -------------------------------------------------
# RESUMEN POR NÓMINA (DEVENGOS/DESCUENTOS/NETO)
# -------------------------------------------------
def get_nomina_summary(idcontrato, idnomina):
    """
    Obtiene resumen de devengos, descuentos y neto para una nómina específica
    """
    if not (idcontrato and idnomina):
        return None

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                cn.idnomina,
                cn.nombrenomina,
                cn.fechapago,
                COALESCE(SUM(CASE WHEN n.valor > 0 THEN n.valor ELSE 0 END), 0) AS devengos,
                COALESCE(SUM(CASE WHEN n.valor < 0 THEN n.valor ELSE 0 END), 0) AS descuentos,
                COALESCE(SUM(COALESCE(n.valor,0)), 0) AS neto
            FROM crearnomina cn
            JOIN nomina n ON n.idnomina_id = cn.idnomina
            WHERE n.idcontrato_id = %s
              AND cn.idnomina = %s
              AND cn.estadonomina = FALSE
            GROUP BY cn.idnomina, cn.nombrenomina, cn.fechapago;
        """, [idcontrato, idnomina])
        row = cursor.fetchone()

    if not row:
        return None

    return {
        "idnomina": row[0],
        "nombrenomina": row[1],
        "fechapago": row[2],
        "devengos": int(row[3] or 0),
        "descuentos": int(row[4] or 0),
        "neto": int(row[5] or 0),
    }


# -------------------------------------------------
# CONCEPTOS TOP POR NÓMINA
# -------------------------------------------------
def get_top_concepts_by_nomina(idcontrato, idnomina, limit=15):
    """
    Obtiene los conceptos más importantes (por valor absoluto) de una nómina
    """
    if not (idcontrato and idnomina):
        return []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                c.nombreconcepto,
                SUM(COALESCE(n.valor,0)) AS total_valor
            FROM nomina n
            JOIN conceptosdenomina c
              ON c.idconcepto = n.idconcepto_id
            JOIN crearnomina cn
              ON cn.idnomina = n.idnomina_id
            WHERE n.idcontrato_id = %s
              AND n.idnomina_id = %s
              AND cn.estadonomina = FALSE
            GROUP BY c.nombreconcepto
            ORDER BY ABS(SUM(COALESCE(n.valor,0))) DESC
            LIMIT %s;
        """, [idcontrato, idnomina, limit])
        rows = cursor.fetchall()

    return [{"nombre": r[0], "valor": int(r[1] or 0)} for r in rows]


# -------------------------------------------------
# CONSTRUIR CONTEXTO DE 6 MESES PARA IA (MEJORADO)
# -------------------------------------------------
def build_6_months_payroll_context(user):
    """
    Construye un contexto completo con TODOS los conceptos pero optimizado en formato
    para reducir tokens sin perder información
    """
    idcontrato = get_active_contract(user)
    if not idcontrato:
        return "No se encontró un contrato activo para el empleado."

    nominas = get_nominas_last_6_months(idcontrato)
    if not nominas:
        return "No hay nóminas registradas en los últimos 6 meses."

    # Verificar si tiene salario integral
    tiene_salario_integral = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM nomina n
                JOIN conceptosdenomina c ON c.idconcepto = n.idconcepto_id
                WHERE n.idcontrato_id = %s
                  AND (c.nombreconcepto ILIKE '%%salario integral%%' OR c.salintegral = 1)
                LIMIT 1;
            """, [idcontrato])
            row = cursor.fetchone()
            if row and row[0]:
                tiene_salario_integral = row[0] > 0
    except Exception:
        tiene_salario_integral = False

    lines = [
        "=== NÓMINAS (6 MESES) ===",
        f"Total: {len(nominas)} nóminas",
        f"Tipo salario: {'SALARIO INTEGRAL' if tiene_salario_integral else 'Ordinario'}",
        "\n⚠️ FÓRMULAS DE CÁLCULO:",
        "- EPS/AFP: Base × (Porcentaje / 100)",
        "- FSP: (Base × 0.70) × (Porcentaje FSP / 100) - Solo si base > 4 SMMLV",
        "- En salario integral, descuentos NO son % del básico. Valores en nómina son correctos.\n"
    ]

    total_devengos = 0
    total_descuentos = 0
    total_neto = 0
    conceptos_globales = {}
    salario_integral_valor = None

    for nomina in nominas:
        resumen = get_nomina_summary(idcontrato, nomina["idnomina"])
        if not resumen:
            continue

        fecha_str = resumen["fechapago"].strftime("%Y-%m-%d") if resumen["fechapago"] else "Sin fecha"
        fecha_mes = resumen["fechapago"].strftime("%Y-%m") if resumen["fechapago"] else "Sin fecha"
        
        # Obtener TODOS los conceptos
        conceptos = get_top_concepts_by_nomina(idcontrato, resumen["idnomina"], limit=200)
        
        # Buscar salario integral y conceptos clave
        salario_integral_nom = None
        eps_valor = None
        afp_valor = None
        fsp_valor = None
        base_ss_estimada = None
        
        for c in conceptos:
            nombre_lower = c['nombre'].lower()
            if 'salario integral' in nombre_lower:
                salario_integral_nom = abs(c['valor'])
                salario_integral_valor = salario_integral_nom
                base_ss_estimada = salario_integral_nom
            elif 'eps' in nombre_lower and c['valor'] < 0:
                eps_valor = abs(c['valor'])
            elif 'afp' in nombre_lower and c['valor'] < 0:
                afp_valor = abs(c['valor'])
            elif 'fsp' in nombre_lower or 'fondo de solidaridad' in nombre_lower:
                if c['valor'] < 0:
                    fsp_valor = abs(c['valor'])
        
        # Formato compacto para la nómina
        lines.append(
            f"\n📋 {resumen['nombrenomina']} (ID:{resumen['idnomina']}, {fecha_str}, Mes:{fecha_mes}):"
        )
        
        if salario_integral_nom:
            lines.append(f"💰SalInt:${salario_integral_nom:,}")
            if eps_valor and base_ss_estimada:
                pct = (eps_valor / base_ss_estimada) * 100
                lines.append(f"🏥EPS:${eps_valor:,}({pct:.2f}% de base)")
            if afp_valor and base_ss_estimada:
                pct = (afp_valor / base_ss_estimada) * 100
                lines.append(f"💼AFP:${afp_valor:,}({pct:.2f}% de base)")
            if fsp_valor and base_ss_estimada:
                # Calcular porcentaje FSP sobre el 70% de la base
                base_70 = base_ss_estimada * 0.70
                pct_fsp = (fsp_valor / base_70) * 100 if base_70 > 0 else 0
                lines.append(f"💎FSP:${fsp_valor:,}({pct_fsp:.2f}% de 70% de base=${base_70:,.0f})")
        else:
            lines.append(f"💰Dev:${resumen['devengos']:,}")
            if eps_valor:
                lines.append(f"🏥EPS:${eps_valor:,}")
            if afp_valor:
                lines.append(f"💼AFP:${afp_valor:,}")
            if fsp_valor:
                lines.append(f"💎FSP:${fsp_valor:,}")
        
        lines.append(f"📉Desc:${abs(resumen['descuentos']):,} 💵Neto:${resumen['neto']:,}")

        # TODOS los conceptos pero en formato compacto
        if conceptos:
            devengos_list = []
            descuentos_list = []
            
            for c in conceptos:
                if c["valor"] > 0:
                    devengos_list.append(f"{c['nombre']}:${abs(c['valor']):,}")
                else:
                    descuentos_list.append(f"{c['nombre']}:${abs(c['valor']):,}")
                
                # Acumular para totales globales
                nombre_concepto = c['nombre']
                if nombre_concepto not in conceptos_globales:
                    conceptos_globales[nombre_concepto] = {
                        'total': 0,
                        'tipo': 'devengo' if c["valor"] > 0 else 'descuento',
                        'nominas': []
                    }
                conceptos_globales[nombre_concepto]['total'] += c['valor']
                conceptos_globales[nombre_concepto]['nominas'].append({
                    'nomina': resumen['nombrenomina'],
                    'valor': c['valor'],
                    'fecha': fecha_str
                })
            
            if devengos_list:
                lines.append(f"Devengos({len(devengos_list)}): {', '.join(devengos_list)}")
            if descuentos_list:
                lines.append(f"Descuentos({len(descuentos_list)}): {', '.join(descuentos_list)}")

        total_devengos += resumen["devengos"]
        total_descuentos += abs(resumen["descuentos"])
        total_neto += resumen["neto"]

    # Resumen de TODOS los conceptos acumulados
    if conceptos_globales:
        lines.append("\n=== CONCEPTOS ACUMULADOS (6 MESES) ===")
        conceptos_ordenados = sorted(
            conceptos_globales.items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )
        
        devengos_acum = []
        descuentos_acum = []
        
        for nombre, datos in conceptos_ordenados:
            tipo = "devengo" if datos['total'] > 0 else "descuento"
            valor_abs = abs(datos['total'])
            info = f"{nombre}:${valor_abs:,}({len(datos['nominas'])}nom)"
            
            if tipo == "devengo":
                devengos_acum.append(info)
            else:
                descuentos_acum.append(info)
        
        if devengos_acum:
            lines.append(f"Devengos({len(devengos_acum)}): {', '.join(devengos_acum)}")
        if descuentos_acum:
            lines.append(f"Descuentos({len(descuentos_acum)}): {', '.join(descuentos_acum)}")

    # Totales generales
    lines.append(
        f"\n=== TOTALES ==="
        f"\nDevengos:${total_devengos:,} Desc:${total_descuentos:,} Neto:${total_neto:,}"
        f"\nPromedio/mes:${total_neto // max(len(nominas), 1):,}"
    )
    
    if tiene_salario_integral and salario_integral_valor:
        lines.append(
            f"\n💰SalIntProm:${salario_integral_valor:,}"
            f"\n⚠️FSP se calcula: (Base × 0.70) × (Porcentaje FSP / 100)"
            f"\n⚠️En salario integral, descuentos NO son % del básico. Valores en nómina son correctos."
        )

    return "\n".join(lines)


# -------------------------------------------------
# ÚLTIMA NÓMINA: DEVENGOS / DESCUENTOS / NETO
# -------------------------------------------------
def get_last_nomina_net_summary(idcontrato):
    if not idcontrato:
        return None

    with connection.cursor() as cursor:
        cursor.execute("""
            WITH last_nom AS (
                SELECT cn.idnomina, cn.nombrenomina, cn.fechapago
                FROM nomina n
                JOIN crearnomina cn ON cn.idnomina = n.idnomina_id
                WHERE n.idcontrato_id = %s
                  AND cn.estadonomina = FALSE
                GROUP BY cn.idnomina, cn.nombrenomina, cn.fechapago
                ORDER BY cn.fechapago DESC NULLS LAST, cn.idnomina DESC
                LIMIT 1
            )
            SELECT
                ln.idnomina,
                ln.nombrenomina,
                COALESCE(SUM(CASE WHEN n.valor > 0 THEN n.valor ELSE 0 END), 0) AS devengos,
                COALESCE(SUM(CASE WHEN n.valor < 0 THEN n.valor ELSE 0 END), 0) AS descuentos,
                COALESCE(SUM(COALESCE(n.valor,0)), 0) AS neto
            FROM last_nom ln
            JOIN nomina n ON n.idnomina_id = ln.idnomina
            WHERE n.idcontrato_id = %s
            GROUP BY ln.idnomina, ln.nombrenomina;
        """, [idcontrato, idcontrato])
        row = cursor.fetchone()

    if not row:
        return None

    return {
        "idnomina": row[0],
        "nombrenomina": row[1],
        "devengos": int(row[2] or 0),
        "descuentos": int(row[3] or 0),
        "neto": int(row[4] or 0),
    }


def get_nomina_concepts_detail(idcontrato, idnomina, limit=40):
    if not (idcontrato and idnomina):
        return []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                c.nombreconcepto,
                SUM(COALESCE(n.valor,0)) AS total_valor
            FROM nomina n
            JOIN conceptosdenomina c
              ON c.idconcepto = n.idconcepto_id
            JOIN crearnomina cn
              ON cn.idnomina = n.idnomina_id
            WHERE n.idcontrato_id = %s
              AND n.idnomina_id = %s
              AND cn.estadonomina = FALSE
            GROUP BY c.nombreconcepto
            ORDER BY ABS(SUM(COALESCE(n.valor,0))) DESC
            LIMIT %s;
        """, [idcontrato, idnomina, limit])
        rows = cursor.fetchall()

    return [{"nombre": r[0], "valor": int(r[1] or 0)} for r in rows]


# Función legacy mantenida para compatibilidad
def build_last_payroll_summary_context(user):
    idcontrato = get_active_contract(user)
    if not idcontrato:
        return "No se encontró contrato activo."

    s = get_last_nomina_net_summary(idcontrato)
    if not s:
        return "No hay nómina grabada reciente."

    return (
        f"Última nómina grabada: {s['nombrenomina']} (ID {s['idnomina']}). "
        f"Devengos: {s['devengos']:,}. "
        f"Descuentos: {s['descuentos']:,}. "
        f"Neto pagado: {s['neto']:,}."
    )


# -------------------------------------------------
# CONTEXTO DE PRÉSTAMOS DEL EMPLEADO
# -------------------------------------------------
def build_loans_context(user):
    """
    Construye contexto completo de préstamos del empleado para la IA
    Los préstamos se identifican por el código 50 y el campo control contiene el idprestamo
    """
    idcontrato = get_active_contract(user)
    if not idcontrato:
        return "No se encontró un contrato activo para el empleado."

    # Obtener el id_empresa del contrato
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_empresa_id
            FROM contratos
            WHERE idcontrato = %s
            LIMIT 1;
        """, [idcontrato])
        empresa_row = cursor.fetchone()
        id_empresa = empresa_row[0] if empresa_row else None

    if not id_empresa:
        return "No se pudo obtener la empresa del contrato."

    # Obtener el concepto de préstamo (código 50) FILTRADO POR EMPRESA
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT idconcepto
            FROM conceptosdenomina
            WHERE codigo = 50
              AND id_empresa_id = %s
            LIMIT 1;
        """, [id_empresa])
        concepto_row = cursor.fetchone()
        idconcepto_prestamo = concepto_row[0] if concepto_row else None

    if not idconcepto_prestamo:
        return "No se encontró el concepto de préstamo en el sistema."

    # Obtener todos los préstamos activos desde la tabla prestamos
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.idprestamo,
                p.valorprestamo,
                p.fechaprestamo,
                p.cuotasprestamo,
                p.valorcuota,
                p.estadoprestamo
            FROM prestamos p
            WHERE p.idcontrato_id = %s
              AND p.estadoprestamo = TRUE
            ORDER BY p.fechaprestamo DESC;
        """, [idcontrato])
        prestamos_rows = cursor.fetchall()

    if not prestamos_rows:
        return "No tienes préstamos activos registrados."

    lines = [
        "=== INFORMACIÓN DE PRÉSTAMOS ===",
        f"Total de préstamos activos: {len(prestamos_rows)}\n"
    ]

    for prestamo_row in prestamos_rows:
        idprestamo = prestamo_row[0]
        valorprestamo = prestamo_row[1]
        fechaprestamo = prestamo_row[2]
        cuotasprestamo = prestamo_row[3]
        valorcuota = prestamo_row[4]
        estadoprestamo = prestamo_row[5]

        # Calcular total pagado desde nóminas (los valores son negativos porque son descuentos)
        # IMPORTANTE: control es IntegerField, no string, y debe compararse como entero
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(n.valor), 0) AS total_pagado,
                    COUNT(DISTINCT n.idnomina_id) AS nominas_con_descuento,
                    COUNT(*) AS registros_descuento
                FROM nomina n
                WHERE n.idcontrato_id = %s
                  AND n.control = %s
                  AND n.idconcepto_id = %s
            """, [idcontrato, idprestamo, idconcepto_prestamo])
            descuento_row = cursor.fetchone()

            total_pagado = int(descuento_row[0] or 0)  # Negativo (descuentos)
            nominas_con_descuento = descuento_row[1] or 0
            registros_descuento = descuento_row[2] or 0

        # Calcular saldo pendiente: valorprestamo + total_pagado (total_pagado es negativo)
        saldo_pendiente = valorprestamo + total_pagado

        # Obtener nóminas donde se descontó
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT
                    cn.idnomina,
                    cn.nombrenomina,
                    cn.fechapago,
                    SUM(n.valor) AS total_descontado
                FROM nomina n
                JOIN crearnomina cn ON cn.idnomina = n.idnomina_id
                WHERE n.idcontrato_id = %s
                  AND n.control = %s
                  AND n.idconcepto_id = %s
                  AND cn.estadonomina = FALSE
                GROUP BY cn.idnomina, cn.nombrenomina, cn.fechapago
                ORDER BY cn.fechapago DESC NULLS LAST, cn.idnomina DESC;
            """, [idcontrato, idprestamo, idconcepto_prestamo])
            nominas_descuento = cursor.fetchall()

        fecha_prestamo_str = fechaprestamo.strftime("%Y-%m-%d") if fechaprestamo else "Sin fecha"

        lines.append(
            f"\n💰 PRÉSTAMO ID: {idprestamo}\n"
            f"   Fecha préstamo: {fecha_prestamo_str}\n"
            f"   Valor del préstamo: ${valorprestamo:,}\n"
            f"   Cuotas totales: {cuotasprestamo or 'No definido'}\n"
            f"   Valor cuota: ${valorcuota:,}\n"
            f"   Total pagado: ${abs(total_pagado):,}\n"
            f"   Saldo pendiente: ${saldo_pendiente:,}\n"
            f"   Nóminas con descuento: {nominas_con_descuento}\n"
        )

        if nominas_descuento:
            lines.append("   Nóminas donde se ha descontado:")
            for nom_desc in nominas_descuento:
                idnomina = nom_desc[0]
                nombrenomina = nom_desc[1]
                fechapago = nom_desc[2]
                total_desc = int(nom_desc[3] or 0)
                fecha_pago_str = fechapago.strftime("%Y-%m-%d") if fechapago else "Sin fecha"
                lines.append(
                    f"     • {nombrenomina} (ID: {idnomina}, Fecha: {fecha_pago_str}): "
                    f"${abs(total_desc):,}"
                )
        else:
            lines.append("   (Aún no se ha descontado en ninguna nómina)")

        lines.append("")  # Línea en blanco entre préstamos

    return "\n".join(lines)


# -------------------------------------------------
# CONTEXTO DE LIBRANZAS DEL EMPLEADO
# -------------------------------------------------
def build_libranzas_context(user):
    """
    Construye contexto completo de libranzas del empleado para la IA
    Similar a préstamos pero para libranzas (código 51)
    """
    idcontrato = get_active_contract(user)
    if not idcontrato:
        return "No se encontró un contrato activo para el empleado."

    # Obtener el concepto de libranza (código 51)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT idconcepto
            FROM conceptosdenomina
            WHERE codigo = 51
            LIMIT 1;
        """, [])
        concepto_row = cursor.fetchone()
        idconcepto_libranza = concepto_row[0] if concepto_row else None

    if not idconcepto_libranza:
        return "No se encontró el concepto de libranza en el sistema."

    # Obtener todas las libranzas activas (identificadas por el campo control en nomina)
    # Similar a préstamos, las libranzas se identifican por el campo control
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT
                n.control AS idlibranza,
                MIN(cn.fechapago) AS fecha_inicio,
                MAX(cn.fechapago) AS fecha_ultimo_pago
            FROM nomina n
            JOIN crearnomina cn ON cn.idnomina = n.idnomina_id
            WHERE n.idcontrato_id = %s
              AND n.idconcepto_id = %s
              AND n.control IS NOT NULL
              AND cn.estadonomina = FALSE
            GROUP BY n.control
            ORDER BY MIN(cn.fechapago) DESC;
        """, [idcontrato, idconcepto_libranza])
        libranzas_rows = cursor.fetchall()

    if not libranzas_rows:
        return "No tienes libranzas activas registradas."

    lines = [
        "=== INFORMACIÓN DE LIBRANZAS ===",
        f"Total de libranzas activas: {len(libranzas_rows)}\n"
    ]

    for libranza_row in libranzas_rows:
        idlibranza = libranza_row[0]
        fecha_inicio = libranza_row[1]
        fecha_ultimo_pago = libranza_row[2]

        # Calcular total descontado y saldo
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(n.valor), 0) AS total_descontado,
                    COUNT(DISTINCT n.idnomina_id) AS nominas_con_descuento,
                    COUNT(*) AS registros_descuento
                FROM nomina n
                WHERE n.idcontrato_id = %s
                  AND n.control = %s
                  AND n.idconcepto_id = %s
            """, [idcontrato, idlibranza, idconcepto_libranza])
            descuento_row = cursor.fetchone()

            total_descontado = int(descuento_row[0] or 0)  # Negativo (descuentos)
            nominas_con_descuento = descuento_row[1] or 0
            registros_descuento = descuento_row[2] or 0

        # Obtener nóminas donde se descontó
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT
                    cn.idnomina,
                    cn.nombrenomina,
                    cn.fechapago,
                    SUM(n.valor) AS total_descontado
                FROM nomina n
                JOIN crearnomina cn ON cn.idnomina = n.idnomina_id
                WHERE n.idcontrato_id = %s
                  AND n.control = %s
                  AND n.idconcepto_id = %s
                  AND cn.estadonomina = FALSE
                GROUP BY cn.idnomina, cn.nombrenomina, cn.fechapago
                ORDER BY cn.fechapago DESC NULLS LAST, cn.idnomina DESC;
            """, [idcontrato, idlibranza, idconcepto_libranza])
            nominas_descuento = cursor.fetchall()

        fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else "Sin fecha"
        fecha_ultimo_str = fecha_ultimo_pago.strftime("%Y-%m-%d") if fecha_ultimo_pago else "Sin fecha"

        lines.append(
            f"\n💳 LIBRANZA ID: {idlibranza}\n"
            f"   Fecha inicio: {fecha_inicio_str}\n"
            f"   Último descuento: {fecha_ultimo_str}\n"
            f"   Total descontado: ${abs(total_descontado):,}\n"
            f"   Nóminas con descuento: {nominas_con_descuento}\n"
        )

        if nominas_descuento:
            lines.append("   Nóminas donde se ha descontado:")
            for nom_desc in nominas_descuento:
                idnomina = nom_desc[0]
                nombrenomina = nom_desc[1]
                fechapago = nom_desc[2]
                total_desc = int(nom_desc[3] or 0)
                fecha_pago_str = fechapago.strftime("%Y-%m-%d") if fechapago else "Sin fecha"
                lines.append(
                    f"     • {nombrenomina} (ID: {idnomina}, Fecha: {fecha_pago_str}): "
                    f"${abs(total_desc):,}"
                )
        else:
            lines.append("   (Aún no se ha descontado en ninguna nómina)")

        lines.append("")  # Línea en blanco entre libranzas

    return "\n".join(lines)


# -------------------------------------------------
# CONTEXTO DE CONTRATO Y DATOS DEL EMPLEADO
# -------------------------------------------------
def build_contract_employee_context(user):
    """
    Construye contexto con información del contrato activo y datos del empleado
    """
    idcontrato = get_active_contract(user)
    if not idcontrato:
        return "No se encontró un contrato activo para el empleado."

    with connection.cursor() as cursor:
        # Obtener información del contrato y empleado
        cursor.execute("""
            SELECT 
                -- Contrato
                c.idcontrato,                    -- 0
                c.fechainiciocontrato,           -- 1
                c.fechafincontrato,              -- 2
                c.salario,                       -- 3
                c.estadocontrato,                -- 4
                c.cuentanomina,                  -- 5
                c.tipocuentanomina,              -- 6
                c.auxiliotransporte,             -- 7
                c.dependientes,                  -- 8
                c.jornada,                       -- 9
                -- Cargo
                car.nombrecargo,                 -- 10
                -- Tipo contrato
                tc.tipocontrato,                 -- 11
                -- Tipo nómina
                tn.tipodenomina,                 -- 12
                -- Banco
                b.nombanco,                      -- 13
                -- Empleado
                ce.idempleado,                   -- 14
                ce.pnombre,                      -- 15
                ce.snombre,                      -- 16
                ce.papellido,                    -- 17
                ce.sapellido,                    -- 18
                ce.docidentidad,                 -- 19
                ce.email,                        -- 20
                ce.telefonoempleado,             -- 21
                ce.celular,                      -- 22
                ce.direccionempleado,            -- 23
                ce.profesion,                    -- 24
                ce.niveleducativo,               -- 25
                -- EPS
                eps.entidad AS nombre_eps,       -- 26
                -- AFP
                afp.entidad AS nombre_afp,       -- 27
                -- CCF
                ccf.entidad AS nombre_ccf,       -- 28
                -- Fondo cesantías
                fc.entidad AS nombre_fondo_cesantias  -- 29
            FROM contratos c
            JOIN contratosemp ce ON ce.idempleado = c.idempleado_id
            LEFT JOIN cargos car ON car.idcargo = c.cargo_id
            LEFT JOIN tipocontrato tc ON tc.idtipocontrato = c.tipocontrato_id
            LEFT JOIN tipodenomina tn ON tn.idtiponomina = c.tiponomina_id
            LEFT JOIN bancos b ON b.idbanco = c.bancocuenta_id
            LEFT JOIN entidadessegsocial eps ON eps.identidad = c.codeps_id
            LEFT JOIN entidadessegsocial afp ON afp.identidad = c.codafp_id
            LEFT JOIN entidadessegsocial ccf ON ccf.identidad = c.codccf_id
            LEFT JOIN entidadessegsocial fc ON fc.identidad = c.fondocesantias_id
            WHERE c.idcontrato = %s;
        """, [idcontrato])
        row = cursor.fetchone()

    if not row:
        return "No se encontró información del contrato."

    # Procesar datos
    fechainicio = row[1].strftime("%Y-%m-%d") if row[1] else "No definida"
    fechafin = row[2].strftime("%Y-%m-%d") if row[2] else "Indefinido"
    estadocontrato = "Activo" if row[4] == 1 else "Retirado" if row[4] == 2 else "Desconocido"
    
    nombre_completo = f"{row[15] or ''} {row[16] or ''} {row[17] or ''} {row[18] or ''}".strip()
    
    aux_transporte = "Sí" if row[7] else "No"

    lines = [
        "=== INFORMACIÓN DEL CONTRATO Y EMPLEADO ===",
        f"\n👤 DATOS DEL EMPLEADO:",
        f"   Nombre completo: {nombre_completo}",
        f"   Documento: {row[19] or 'No registrado'}",
        f"   Email: {row[20] or 'No registrado'}",
        f"   Teléfono: {row[21] or 'No registrado'}",
        f"   Celular: {row[22] or 'No registrado'}",
        f"   Dirección: {row[23] or 'No registrada'}",
        f"   Profesión: {row[24] or 'No registrada'}",
        f"   Nivel educativo: {row[25] or 'No registrado'}",
        
        f"\n📋 DATOS DEL CONTRATO (ID: {row[0]}):",
        f"   Estado: {estadocontrato}",
        f"   Cargo: {row[10] or 'No definido'}",
        f"   Tipo de contrato: {row[11] or 'No definido'}",
        f"   Tipo de nómina: {row[12] or 'No definido'}",
        f"   Fecha inicio: {fechainicio}",
        f"   Fecha fin: {fechafin}",
        f"   Salario: ${row[3]:,}" if row[3] else "   Salario: No definido",
        f"   Auxilio de transporte: {aux_transporte}",
        f"   Dependientes: {row[8] or 0}",
        f"   Jornada: {row[9] or 'No definida'}",
        
        f"\n🏦 INFORMACIÓN BANCARIA:",
        f"   Banco: {row[13] or 'No registrado'}",
        f"   Cuenta nómina: {row[5] or 'No registrada'}",
        f"   Tipo de cuenta: {row[6] or 'No registrado'}",
        
        f"\n🏥 ENTIDADES DE SEGURIDAD SOCIAL:",
        f"   EPS: {row[26] or 'No registrada'}",
        f"   AFP (Pensión): {row[27] or 'No registrada'}",
        f"   CCF: {row[28] or 'No registrada'}",
        f"   Fondo de cesantías: {row[29] or 'No registrado'}"
    ]

    return "\n".join(lines)