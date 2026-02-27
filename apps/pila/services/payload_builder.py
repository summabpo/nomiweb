# nomiweb/apps/pila/services/payload_builder.py

from datetime import date
import calendar
from decimal import Decimal
from django.db import connection
from datetime import timedelta
from math import ceil
from apps.common.models import Empresa


def _redondear_ibc(valor: Decimal | float | int | str) -> int:
    """
    Redondea el IBC al peso superior más cercano según Decreto 1990 de 2016.
    """
    if valor is None:
        return 0
    if isinstance(valor, Decimal):
        return int(ceil(float(valor)))
    if isinstance(valor, str):
        try:
            return int(ceil(float(valor)))
        except (ValueError, TypeError):
            return 0
    return int(ceil(float(valor)))


_MESES = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12,
}
_MESES_INV = {v: k for k, v in _MESES.items()}


def _codigo_centro_trabajo_from_tarifa_arl(tarifa_arl):
    """
    Mapeo tarifa ARL → código centro de trabajo (campo 62 TXT, pos 390-398).
    0.522 → 0, 4.350 → 1, 2.436 → 3, 6.960 → 5; otro → 0.
    """
    if tarifa_arl is None:
        return 0
    try:
        v = float(str(tarifa_arl).strip())
        if abs(v - 0.522) < 0.01:
            return 0
        if abs(v - 4.350) < 0.01:
            return 1
        if abs(v - 2.436) < 0.01:
            return 3
        if abs(v - 6.960) < 0.01:
            return 5
    except (ValueError, TypeError):
        pass
    return 0


def _clase_riesgo_from_tarifa_arl(tarifa_arl):
    """
    Mapeo tarifa ARL (%) → clase de riesgo (campo 78 TXT, pos 513).
    0.522 → "1", 1.044 → "2", 2.436 → "3", 4.350 → "4", 6.960 → "5"; otro → "1".
    """
    if tarifa_arl is None:
        return "1"
    try:
        v = float(str(tarifa_arl).strip())
        if abs(v - 0.522) < 0.01:
            return "1"
        if abs(v - 1.044) < 0.01:
            return "2"
        if abs(v - 2.436) < 0.01:
            return "3"
        if abs(v - 4.350) < 0.01:
            return "4"
        if abs(v - 6.960) < 0.01:
            return "5"
    except (ValueError, TypeError):
        pass
    return "1"


def build_payload_pila_minimo(*, empresa_id_interno: int, periodo: str) -> dict:
    """
    Payload mínimo v1 (loop real por contratos con movimiento).
    - empresa_id_interno: idempresa en tu BD
    - periodo: 'YYYY-MM'
    """
    hoy = date.today().isoformat()

    ano = int(periodo.split("-")[0])
    mes_num = int(periodo.split("-")[1])
    mesacumular = _MESES_INV.get(mes_num)
    if not mesacumular:
        raise ValueError(f"Mes inválido en periodo={periodo}")

    # Parámetros PILA (smmlv, factor_integral, etc.) para usarlos en el loop
    params_pila = _get_parametros_pila(periodo)

    # Empresa: datos reales (ORM solo lectura, managed=False ok)
    empresa = Empresa.objects.only(
        "empresa_exonerada",
        "nit",
        "dv",
        "nombreempresa",
        "tipodoc",
        "tipoaportante",
        "claseaportante",
        "tipo_presentacion_planilla",
        "arl"
    ).get(idempresa=empresa_id_interno)
    empresa_flags = {"empresa_exonerada": bool(empresa.empresa_exonerada)}

    # 1) Contratos con movimiento en el mes/año
    ids_contrato = _get_contratos_con_movimiento_mes(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano
    )

    # 2) Ficha contratos (doc, nombres, salario, tipo cotizante, entidades, fechas)
    rows = _get_ficha_contratos(
        empresa_id=empresa_id_interno,
        ids_contrato=ids_contrato
    )

    # 3) IBC por contrato (indicadores 6/16/17) - mes actual
    ibc_map = _get_ibc_por_contrato_mes(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato
    )
    
    # 3.1) IBC del mes anterior (para novedades VAC, IGE, IRL, LMA)
    ibc_map_anterior = _get_ibc_mes_anterior(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato
    )

    # 3.2) VST por contrato (indicador 29) para línea NORMAL: IBC = salario + VST
    vst_map = _get_vst_por_contrato_mes(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato
    )

    # 4) Armar empleados reales con múltiples registros si tienen novedades
    empleados = []
    for row in rows:
        idcontrato = int(row["idcontrato"])

        tipo_cot = str(row["tipo_cotizante"]).zfill(2)
        subtipo_cot = str(row["subtipo_cotizante"]).zfill(2)
        flags_tc = _get_flags_tipo_cotizante(tipo_cot)

        # --- Días base (mes comercial) ---
        dias_base = _dias_base_contrato_mes(
            fechainicio=row["fechainiciocontrato"],
            fechafin=row["fechafincontrato"],
            mesacumular=mesacumular,
            ano=ano
        )

        # --- Novedades del mes ---
        novedades_ing_ret = _novedades_ing_ret_mes(
            row["fechainiciocontrato"],
            row["fechafincontrato"],
            mesacumular,
            ano
        )
        
        novedades_vac = _novedades_vacaciones_mes(
            empresa_id=empresa_id_interno,
            idcontrato=idcontrato,
            mesacumular=mesacumular,
            ano=ano
        )
        
        novedades_incap = _novedades_incapacidades_mes(
            empresa_id=empresa_id_interno,
            idcontrato=idcontrato,
            mesacumular=mesacumular,
            ano=ano
        )
        
        novedad_vsp = _get_vsp_mes(
            idcontrato=idcontrato,
            mesacumular=mesacumular,
            ano=ano
        )
        
        # --- IBC mes actual y anterior ---
        ibc_actual = ibc_map.get(idcontrato, {"salud_pension": Decimal("0"), "arl": Decimal("0"), "caja": Decimal("0")})
        ibc_anterior = ibc_map_anterior.get(idcontrato, {"salud_pension": Decimal("0"), "arl": Decimal("0"), "caja": Decimal("0")})
        
        # --- VST y salario para línea NORMAL ---
        vst = vst_map.get(idcontrato, 0)
        salario_contrato = int(row["salario_basico"] or 0)

        # --- Generar registros (uno o múltiples líneas tipo 02) ---
        # Fecha del primer día del mes para VST (si aplica)
        fecha_mes_ini = date(ano, mes_num, 1)
        
        salario_integral = (row["tiposalario_id"] == 2)
        factor_integral = params_pila.get("factor_integral", 0.7)

        registros = _generar_registros_empleado(
            dias_base=dias_base,
            novedades_vac=novedades_vac,
            novedades_incap=novedades_incap,
            novedad_vsp=novedad_vsp,
            novedades_ing_ret=novedades_ing_ret,
            ibc_actual=ibc_actual,
            ibc_anterior=ibc_anterior,
            vst=vst,
            salario_contrato=salario_contrato,
            fecha_periodo=fecha_mes_ini,
            salario_integral=salario_integral,
            factor_integral=factor_integral,
        )

        # Aplica pensión cuando subtipo está en blanco/0/00 o cuando subtipo == "12". Si subtipo tiene otro valor (ej. 01, 03): exonerado, tarifa 0, días AFP 0, IBC 0.
        aplica_pension = bool(
            flags_tc.get("aplica_pension", True)
            and (subtipo_cot in ("", "0", "00", "12"))
        )
        if not aplica_pension:
            for reg in registros:
                reg.setdefault("dias", {})["pension"] = 0
                reg.setdefault("ibc", {})["pension"] = "0"

        # --- Datos comunes del empleado ---
        empleado_base = {
            "id_empleado": idcontrato,
            "tipo_doc": row["tipo_doc"],
            "num_doc": row["num_doc"],
            "primer_apellido": row["primer_apellido"] or "",
            "segundo_apellido": row["segundo_apellido"] or "",
            "primer_nombre": row["primer_nombre"] or "",
            "segundo_nombre": row["segundo_nombre"] or "",
            "cod_departamento": row["cod_departamento"] or "",
            "cod_municipio": row["cod_municipio"] or "",
            "tipo_cotizante": tipo_cot,
            "subtipo_cotizante": subtipo_cot,
            "salario_basico": str(row["salario_basico"] or 0),

            "entidades": {
                "eps": row["eps_codigo"],
                "afp": row["afp_codigo"],
                "arl": row["arl_codigo"],
                "caja": row["ccf_codigo"],
            },

            "flags": {
                **flags_tc,
                "aplica_pension": aplica_pension,  # Solo True si subtipo_cotizante == "12"
                "salario_integral": (row["tiposalario_id"] == 2),
            },

            "tarifas": {
                "arl": str(row["tarifa_arl"]) if row["tarifa_arl"] else None
            },
            "codigo_centro_trabajo": _codigo_centro_trabajo_from_tarifa_arl(row.get("tarifa_arl")),
            "clase_riesgo": _clase_riesgo_from_tarifa_arl(row.get("tarifa_arl")),
            "actividad_economica_arl": row.get("actividad_economica_arl") or "",
            
            "registros": registros  # Array de registros (líneas tipo 02)
        }

        empleados.append(empleado_base)

    # Obtener código ARL de la empresa
    codigo_arl_empresa = ""
    if empresa.arl:
        codigo_arl_empresa = empresa.arl.codigo or ""
    
    payload = {
        "empresa": {
            "id_interno": empresa_id_interno,
            "nit": empresa.nit or "",  # NIT sin DV
            "dv": empresa.dv or "",  # Dígito de verificación separado
            "razon_social": empresa.nombreempresa or "",
            "sucursal": "",  # En blanco: tipo presentación única
            "tipo_documento_aportante": empresa.tipodoc or "NI",
            "tipo_aportante": str(empresa.tipoaportante or "1").zfill(2),  # 01=Empleador
            "clase_aportante": empresa.claseaportante or "A",
            "tipo_presentacion_planilla": empresa.tipo_presentacion_planilla or "U",  # U=única, S=sucursal
            "codigo_arl": codigo_arl_empresa,  # Código ARL de la empresa (6 caracteres)
            "flags": empresa_flags,
        },
        "periodo": periodo,
        "planilla": {
            "tipo_planilla": "E",
            "numero_interno": f"NW-EMP{empresa_id_interno}-{periodo}",
            "fecha_generacion": hoy,
        },
        "empleados": empleados,
        "meta": {
            "origen": "nomiweb",
            "version_payload": "1.0",
            "usuario": "admin@nomiweb.com.co",
        },
        "parametros": params_pila,
    }

    return payload


def _get_parametros_pila(periodo: str) -> dict:
    ano = int(periodo.split("-")[0])

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT salariominimo FROM public.salariominimoanual WHERE ano = %s",
            [ano],
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"No existe SMMLV para el año {ano}")
        smmlv = int(row[0])

        cursor.execute("SELECT valorfijo FROM public.conceptosfijos WHERE idfijo = 2")
        row = cursor.fetchone()
        if not row:
            raise ValueError("No existe conceptosfijos idfijo=2 (MAXIMO IBC EN SMLV)")
        tope_ibc_smmlv = int(Decimal(str(row[0])))

        # Factor integral: IBC = 70% del salario para tiposalario_id=2 (conceptosfijos idfijo=1)
        cursor.execute("SELECT valorfijo FROM public.conceptosfijos WHERE idfijo = 1")
        row = cursor.fetchone()
        factor_integral = float(row[0]) if row and row[0] is not None else 0.7
        # Si viene como porcentaje (ej: 70) convertir a decimal (0.7)
        if factor_integral >= 1:
            factor_integral = factor_integral / 100.0

        # EPS: idfijo 8 = empleado (4%), idfijo 18 = empresa cuando IBC > 10 SMLV (8.5%)
        cursor.execute("SELECT valorfijo FROM public.conceptosfijos WHERE idfijo = 8")
        row = cursor.fetchone()
        tasa_salud_emp = float(row[0]) / 100.0 if row and row[0] is not None else 0.04
        cursor.execute("SELECT valorfijo FROM public.conceptosfijos WHERE idfijo = 18")
        row = cursor.fetchone()
        tasa_salud_empl_ibc_mayor_10 = float(row[0]) / 100.0 if row and row[0] is not None else 0.085

        # Obtener porcentajes FSP desde conceptosfijos
        # idfijo 12: FSP 4-16 SMLV
        # idfijo 13: FSP 16-17 SMLV
        # idfijo 14: FSP 17-18 SMLV
        # idfijo 15: FSP 18-19 SMLV
        # idfijo 16: FSP 19-20 SMLV
        # idfijo 17: FSP >20 SMLV
        fsp_porcentajes = {}
        for idfijo, rango in [(12, "4-16"), (13, "16-17"), (14, "17-18"), (15, "18-19"), (16, "19-20"), (17, ">20")]:
            cursor.execute("SELECT valorfijo FROM public.conceptosfijos WHERE idfijo = %s", [idfijo])
            row = cursor.fetchone()
            if row:
                # valorfijo viene como porcentaje (ej: 1.0000 = 1%)
                fsp_porcentajes[rango] = float(row[0]) / 100.0  # Convertir a decimal
            else:
                # Valores por defecto si no existen en BD
                valores_defecto = {
                    "4-16": 0.01,    # 1%
                    "16-17": 0.012,  # 1.2%
                    "17-18": 0.014,  # 1.4%
                    "18-19": 0.016,  # 1.6%
                    "19-20": 0.018,  # 1.8%
                    ">20": 0.02,     # 2%
                }
                fsp_porcentajes[rango] = valores_defecto.get(rango, 0.01)

    return {
        "smmlv": smmlv,
        "tope_ibc_smmlv": tope_ibc_smmlv,
        "dias_base": 30,
        "fsp_porcentajes": fsp_porcentajes,
        "factor_integral": factor_integral,
        "tasa_salud_emp": tasa_salud_emp,
        "tasa_salud_empl_ibc_mayor_10": tasa_salud_empl_ibc_mayor_10,
    }


def _get_flags_tipo_cotizante(tipo_cotizante: str) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT aplica_salud, aplica_pension, aplica_arl, aplica_caja
            FROM public.tiposdecotizantes
            WHERE tipocotizante = %s
            """,
            [tipo_cotizante],
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"No existe tiposdecotizantes.tipocotizante={tipo_cotizante}")

    return {
        "aplica_salud": bool(row[0]),
        "aplica_pension": bool(row[1]),
        "aplica_arl": bool(row[2]),
        "aplica_caja": bool(row[3]),
    }


def _get_contratos_con_movimiento_mes(empresa_id: int, mesacumular: str, ano: int) -> list[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT n.idcontrato_id
            FROM public.nomina n
            JOIN public.conceptosdenomina cd
              ON cd.idconcepto = n.idconcepto_id
            JOIN public.crearnomina cn
              ON cn.idnomina = n.idnomina_id
            JOIN public.anos a
              ON a.idano = cn.anoacumular_id
            WHERE cd.id_empresa_id = %s
              AND cn.id_empresa_id = %s
              AND cn.mesacumular = %s
              AND a.ano = %s
              AND cn.estadonomina = FALSE
              AND n.estadonomina = 2
            ORDER BY n.idcontrato_id
            """,
            [empresa_id, empresa_id, mesacumular, ano],
        )
        return [r[0] for r in cursor.fetchall()]


def _get_ficha_contratos(empresa_id: int, ids_contrato: list[int]) -> list[dict]:
    sql = """
    SELECT
      c.idcontrato,
      c.fechainiciocontrato,
      c.fechafincontrato,

      td.codigo                      AS tipo_doc,
      ce.docidentidad::text          AS num_doc,
      ce.pnombre                     AS primer_nombre,
      ce.snombre                     AS segundo_nombre,
      ce.papellido                   AS primer_apellido,
      ce.sapellido                   AS segundo_apellido,

      ciu.codciudad                  AS cod_departamento,
      ciu.coddepartamento            AS cod_municipio,

      c.salario::numeric             AS salario_basico,
      c.tiposalario_id               AS tiposalario_id,

      tc.tipocotizante               AS tipo_cotizante,
      st.subtipocotizante            AS subtipo_cotizante,

      eps.codigo                     AS eps_codigo,
      afp.codigo                     AS afp_codigo,
      ccf.codigo                     AS ccf_codigo,
      arl.codigo                     AS arl_codigo,

      ct.tarifaarl::numeric          AS tarifa_arl,
      ct.actividad_economica_arl     AS actividad_economica_arl

    FROM public.contratos c
    JOIN public.contratosemp ce
      ON ce.idempleado = c.idempleado_id
    JOIN public.tipodocumento td
      ON td.id_tipo_doc = ce.tipodocident_id

    LEFT JOIN public.ciudades ciu
      ON ciu.idciudad = c.ciudadcontratacion_id

    LEFT JOIN public.centrotrabajo ct
      ON ct.centrotrabajo = c.centrotrabajo_id

    JOIN public.tiposdecotizantes tc
      ON tc.tipocotizante = c.tipocotizante_id
    JOIN public.subtipocotizantes st
      ON st.subtipocotizante = c.subtipocotizante_id

    JOIN public.entidadessegsocial eps
      ON eps.identidad = c.codeps_id
    LEFT JOIN public.entidadessegsocial afp
      ON afp.identidad = c.codafp_id
    LEFT JOIN public.entidadessegsocial ccf
      ON ccf.identidad = c.codccf_id

    JOIN public.empresa e
      ON e.idempresa = c.id_empresa_id
    JOIN public.entidadessegsocial arl
      ON arl.identidad = e.arl_id

    WHERE c.id_empresa_id = %s
      AND c.idcontrato = ANY(%s)
    ORDER BY c.idcontrato;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [empresa_id, ids_contrato])
        cols = [c[0] for c in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _get_ibc_por_contrato_mes(
    empresa_id: int,
    mesacumular: str,
    ano: int,
    ids_contrato: list[int],
) -> dict[int, dict]:
    sql = """
    SELECT
      n.idcontrato_id,
      SUM(CASE WHEN cdi.indicador_id = 6  THEN COALESCE(n.valor,0) ELSE 0 END) AS ibc_salud_pension,
      SUM(CASE WHEN cdi.indicador_id = 16 THEN COALESCE(n.valor,0) ELSE 0 END) AS ibc_arl,
      SUM(CASE WHEN cdi.indicador_id = 17 THEN COALESCE(n.valor,0) ELSE 0 END) AS ibc_caja
    FROM public.nomina n
    JOIN public.crearnomina cn ON cn.idnomina = n.idnomina_id
    JOIN public.anos a ON a.idano = cn.anoacumular_id
    JOIN public.conceptosdenomina cd ON cd.idconcepto = n.idconcepto_id
    JOIN public.conceptosdenomina_indicador cdi ON cdi.conceptosdenomina_id = cd.idconcepto
    WHERE cn.id_empresa_id = %s
      AND cd.id_empresa_id = %s
      AND cn.mesacumular = %s
      AND a.ano = %s
      AND cn.estadonomina = FALSE
      AND n.estadonomina = 2
      AND n.idcontrato_id = ANY(%s)
      AND cdi.indicador_id IN (6,16,17)
    GROUP BY n.idcontrato_id
    ORDER BY n.idcontrato_id;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [empresa_id, empresa_id, mesacumular, ano, ids_contrato])
        rows = cursor.fetchall()

    out = {}
    for idcontrato, ibc_ss, ibc_arl, ibc_caja in rows:
        out[int(idcontrato)] = {
            "salud_pension": Decimal(str(ibc_ss or 0)),
            "arl": Decimal(str(ibc_arl or 0)),
            "caja": Decimal(str(ibc_caja or 0)),
        }
    return out


def _get_ibc_mes_anterior(
    empresa_id: int,
    mesacumular: str,
    ano: int,
    ids_contrato: list[int],
) -> dict[int, dict]:
    """
    Calcula IBC del mes anterior (para novedades VAC, IGE, IRL, LMA)
    """
    # Calcular mes anterior
    mes_num = _MESES[mesacumular.upper().strip()]
    if mes_num == 1:
        mes_anterior_num = 12
        ano_anterior = ano - 1
    else:
        mes_anterior_num = mes_num - 1
        ano_anterior = ano
    
    mesacumular_anterior = _MESES_INV.get(mes_anterior_num)
    
    # Reutilizar la misma función pero con mes anterior
    return _get_ibc_por_contrato_mes(
        empresa_id=empresa_id,
        mesacumular=mesacumular_anterior,
        ano=ano_anterior,
        ids_contrato=ids_contrato
    )


def _get_vst_por_contrato_mes(
    empresa_id: int,
    mesacumular: str,
    ano: int,
    ids_contrato: list[int],
) -> dict[int, int]:
    """
    VST = suma de nomina.valor donde idconcepto tiene indicador_id=29
    (Variación transitoria de salario PILA).
    Misma lógica relacional que _get_ibc_por_contrato_mes con conceptosdenomina_indicador.
    Retorna dict {idcontrato: valor_vst}
    """
    sql = """
    SELECT
      n.idcontrato_id,
      COALESCE(SUM(n.valor), 0)::int AS vst
    FROM public.nomina n
    JOIN public.crearnomina cn ON cn.idnomina = n.idnomina_id
    JOIN public.anos a ON a.idano = cn.anoacumular_id
    JOIN public.conceptosdenomina cd ON cd.idconcepto = n.idconcepto_id
    JOIN public.conceptosdenomina_indicador cdi ON cdi.conceptosdenomina_id = cd.idconcepto
    WHERE cn.id_empresa_id = %s
      AND cd.id_empresa_id = %s
      AND cn.mesacumular = %s
      AND a.ano = %s
      AND cn.estadonomina = FALSE
      AND n.estadonomina = 2
      AND n.idcontrato_id = ANY(%s)
      AND cdi.indicador_id = 29
    GROUP BY n.idcontrato_id
    ORDER BY n.idcontrato_id;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [empresa_id, empresa_id, mesacumular, ano, ids_contrato])
        rows = cursor.fetchall()

    return {int(r[0]): int(r[1] or 0) for r in rows}


def _dias_base_contrato_mes(
    fechainicio: date | None,
    fechafin: date | None,
    mesacumular: str,
    ano: int,
) -> int:
    """
    Mes comercial PILA: 1..30.
    """
    if not fechainicio:
        return 0

    mes_num = _MESES[mesacumular.upper().strip()]
    ini_mes = date(ano, mes_num, 1)
    fin_mes = date(ano, mes_num, 30)  # PILA mes comercial

    ini = max(fechainicio, ini_mes)
    fin = fin_mes if fechafin is None else min(fechafin, fin_mes)

    if fin < ini:
        return 0

    dias = (fin - ini).days + 1
    return _cap_30(dias)


def _dias_vacaciones_en_mes_por_tipo(
    empresa_id: int,
    idcontrato: int,
    mesacumular: str,
    ano: int,
) -> dict[int, int]:
    """
    Overlap con mes calendario real para eventos; luego ARL se limita a 30 por _dias_arl_mes.
    """
    mes_num = _MESES[mesacumular.upper().strip()]
    last_day = calendar.monthrange(ano, mes_num)[1]
    ini_mes = date(ano, mes_num, 1)
    fin_mes = date(ano, mes_num, last_day)

    sql = """
    SELECT
      v.tipovac_id,
      SUM(
        GREATEST(
          0,
          (LEAST(v.ultimodiavac, %s) - GREATEST(v.fechainicialvac, %s) + 1)
        )
      )::int AS dias_en_mes
    FROM public.vacaciones v
    WHERE v.id_empresa_id = %s
      AND v.idcontrato_id = %s
      AND v.fechainicialvac IS NOT NULL
      AND v.ultimodiavac IS NOT NULL
      AND v.fechainicialvac <= %s
      AND v.ultimodiavac >= %s
    GROUP BY v.tipovac_id;
    """

    out = {}
    with connection.cursor() as cursor:
        cursor.execute(sql, [fin_mes, ini_mes, empresa_id, idcontrato, fin_mes, ini_mes])
        for tipovac_id, dias_en_mes in cursor.fetchall():
            out[int(tipovac_id)] = int(dias_en_mes or 0)

    return out


def _dias_arl_mes(dias_base_mes: int, dias_vac_tipo: dict[int, int]) -> int:
    """
    ARL descuenta ausencias: 1,4,5
    """
    dias_aus = (
        int(dias_vac_tipo.get(1, 0)) +
        int(dias_vac_tipo.get(4, 0)) +
        int(dias_vac_tipo.get(5, 0))
    )
    dias = dias_base_mes - dias_aus
    return _cap_30(dias)


def _build_dias_por_subsistema(dias_base: int, dias_arl: int) -> dict:
    return {
        "salud": dias_base,
        "pension": dias_base,
        "caja": dias_base,
        "arl": dias_arl,
    }


def _cap_30(dias: int) -> int:
    if dias < 0:
        return 0
    if dias > 30:
        return 30
    return dias

def _novedades_ing_ret_mes(
    fechainicio: date | None,
    fechafin: date | None,
    mesacumular: str,
    ano: int,
) -> list[dict]:
    """
    Retorna lista de novedades tipo ING/RET si caen dentro del mes PILA (mes comercial 1..30).
    """
    mes_num = _MESES[mesacumular.upper().strip()]
    ini_mes = date(ano, mes_num, 1)
    fin_mes = date(ano, mes_num, 30)

    novs = []

    if fechainicio and ini_mes <= fechainicio <= fin_mes:
        novs.append({
            "codigo": "ING",
            "fecha_desde": fechainicio.isoformat(),
            "fecha_hasta": fechainicio.isoformat(),
            "dias": 1,
        })

    if fechafin and ini_mes <= fechafin <= fin_mes:
        novs.append({
            "codigo": "RET",
            "fecha_desde": fechafin.isoformat(),
            "fecha_hasta": fechafin.isoformat(),
            "dias": 1,
        })

    return novs

def _novedades_vacaciones_mes(
    empresa_id: int,
    idcontrato: int,
    mesacumular: str,
    ano: int,
) -> list[dict]:

    mes_num = _MESES[mesacumular.upper().strip()]
    ini_mes = date(ano, mes_num, 1)
    fin_mes = date(ano, mes_num, 30)  # mes comercial PILA

    sql = """
    SELECT
        v.tipovac_id,
        v.fechainicialvac,
        v.ultimodiavac
    FROM public.vacaciones v
    JOIN public.contratos c
      ON c.idcontrato = v.idcontrato_id
    WHERE c.id_empresa_id = %s
      AND v.idcontrato_id = %s
      AND v.tipovac_id IN (1,4,5)
      AND v.fechainicialvac IS NOT NULL
      AND v.ultimodiavac IS NOT NULL
      AND v.fechainicialvac <= %s
      AND v.ultimodiavac >= %s
    ORDER BY v.fechainicialvac;
    """

    out = []

    # ✅ cursor EXISTE solo dentro de este bloque
    with connection.cursor() as cursor:
        cursor.execute(sql, [empresa_id, idcontrato, fin_mes, ini_mes])
        rows = cursor.fetchall()

    for tipovac_id, f_ini, f_fin in rows:
        out.append({
            "codigo": {
                1: "VAC",
                4: "SLN",
                5: "SUSP",
            }.get(tipovac_id),
            "fecha_desde": max(f_ini, ini_mes).isoformat(),
            "fecha_hasta": min(f_fin, fin_mes).isoformat(),
            "dias": (min(f_fin, fin_mes) - max(f_ini, ini_mes)).days + 1,
        })

    return out

def _novedades_incapacidades_mes(
    empresa_id: int,
    idcontrato: int,
    mesacumular: str,
    ano: int,
) -> list[dict]:
    mes_num = _MESES[mesacumular.upper().strip()]
    ini_mes = date(ano, mes_num, 1)
    fin_mes = date(ano, mes_num, 30)

    cod_map = {"1": "IGE", "2": "IRL", "3": "LMA"}

    sql = """
    SELECT
      i.origenincap,
      i.fechainicial,
      i.dias
    FROM public.incapacidades i
    JOIN public.contratos c
      ON c.idcontrato = i.idcontrato_id
    WHERE c.id_empresa_id = %s
      AND i.idcontrato_id = %s
      AND i.fechainicial IS NOT NULL
      AND i.dias IS NOT NULL
      AND i.dias > 0
    ORDER BY i.fechainicial;
    """

    out = []
    with connection.cursor() as cursor:
        cursor.execute(sql, [empresa_id, idcontrato])
        rows = cursor.fetchall()

    for origen, fi, dias in rows:
        origen_s = str(origen).strip() if origen is not None else ""
        codigo = cod_map.get(origen_s)
        if not codigo:
            continue

        ff = fi + timedelta(days=int(dias) - 1)

        # recorte al mes PILA
        desde = max(fi, ini_mes)
        hasta = min(ff, fin_mes)
        d = (hasta - desde).days + 1
        if d <= 0:
            continue

        out.append({
            "codigo": codigo,
            "fecha_desde": desde.isoformat(),
            "fecha_hasta": hasta.isoformat(),
            "dias": int(d),
        })

    return out


def _get_vsp_mes(
    idcontrato: int,
    mesacumular: str,
    ano: int,
) -> dict | None:
    """
    Detecta si hay variación permanente de salario (VSP) en el mes
    desde la tabla nov_salarios
    """
    mes_num = _MESES[mesacumular.upper().strip()]
    ini_mes = date(ano, mes_num, 1)
    fin_mes = date(ano, mes_num, 30)
    
    sql = """
    SELECT
      ns.salarioactual,
      ns.nuevosalario,
      ns.fechanuevosalario,
      ns.tiposalario
    FROM public.nov_salarios ns
    WHERE ns.idcontrato_id = %s
      AND ns.fechanuevosalario IS NOT NULL
      AND ns.fechanuevosalario >= %s
      AND ns.fechanuevosalario <= %s
    ORDER BY ns.fechanuevosalario DESC
    LIMIT 1;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [idcontrato, ini_mes, fin_mes])
        row = cursor.fetchone()
    
    if not row:
        return None
    
    salario_actual, nuevo_salario, fecha_nuevo, tipo_salario = row
    
    return {
        "codigo": "VSP",
        "salario_anterior": int(salario_actual or 0),
        "salario_nuevo": int(nuevo_salario or 0),
        "diferencia": int((nuevo_salario or 0) - (salario_actual or 0)),
        "fecha_desde": fecha_nuevo.isoformat(),
        "tipo_salario": int(tipo_salario or 1)
    }


def _generar_registros_empleado(
    dias_base: int,
    novedades_vac: list[dict],
    novedades_incap: list[dict],
    novedad_vsp: dict | None,
    novedades_ing_ret: list[dict],
    ibc_actual: dict,
    ibc_anterior: dict,
    vst: int = 0,
    salario_contrato: int = 0,
    fecha_periodo: date | None = None,
    salario_integral: bool = False,
    factor_integral: float = 0.7,
) -> list[dict]:
    """
    Genera uno o más registros tipo 02 por empleado según novedades.
    
    Reglas:
    - Novedades que generan líneas separadas: VAC, IGE, IRL, LMA, SLN, VSP
    - Novedades que van en línea normal: ING, RET
    - Cada línea tiene sus propios días e IBC
    - Salario integral: IBC por línea = (70% salario [+ VST en NORMAL]) × (días de la línea / 30).
    """
    def _prorratear_ibc(ibc_base: float, dias: int) -> int:
        """IBC proporcional a los días cotizados (mes = 30). Decreto 1990 para IBC."""
        if dias <= 0:
            return 0
        return _redondear_ibc(ibc_base * dias / 30)

    registros = []
    dias_usados = 0

    # IBC base mensual para salario integral (70% = factor_integral); por línea se prorratea por días
    if salario_integral:
        ibc_integral_mes = salario_contrato * factor_integral  # sin VST para VAC/IGE/IRL/LMA
        ibc_vac_incap = None  # se arma por línea con _prorratear_ibc(ibc_integral_mes, dias)
    else:
        ibc_vac_incap = None  # usar ibc_anterior

    # 1. Líneas de vacaciones (IBC = salario básico proporcional a los días de vacaciones)
    for nov_vac in novedades_vac:
        if nov_vac["codigo"] == "VAC":  # Solo vacaciones tipo 1
            dias_vac = nov_vac["dias"]
            if salario_integral:
                ibc_pror = _prorratear_ibc(ibc_integral_mes, dias_vac)
                ibc_vac = {
                    "salud": str(ibc_pror),
                    "pension": str(ibc_pror),
                    "arl": str(ibc_pror),  # IBC riesgos = IBC salud; tarifa ARL 0% en microservicio
                    "parafiscales": str(ibc_pror),
                }
            else:
                # VAC: IBC = salario básico del empleado × (días vac / 30), no IBC mes anterior
                ibc_vac_pror = _prorratear_ibc(float(salario_contrato), dias_vac)
                ibc_vac = {
                    "salud": str(ibc_vac_pror),
                    "pension": str(ibc_vac_pror),
                    "arl": str(ibc_vac_pror),  # IBC riesgos = IBC salud; tarifa ARL 0% en microservicio
                    "parafiscales": str(ibc_vac_pror),
                }
            registros.append({
                "tipo_linea": "VAC",
                "dias": {
                    "salud": dias_vac,
                    "pension": dias_vac,
                    "arl": dias_vac,  # Mismos días que salud; tarifa ARL 0% evita cotización
                    "caja": dias_vac,
                },
                "ibc": ibc_vac,
                "novedades": [nov_vac],
            })
            dias_usados += dias_vac

    # 2. Líneas de incapacidades (IBC = salario básico proporcional a días de la novedad)
    for nov_incap in novedades_incap:
        dias_incap = nov_incap["dias"]
        if salario_integral:
            ibc_pror = _prorratear_ibc(ibc_integral_mes, dias_incap)
            ibc_incap = {
                "salud": str(ibc_pror),
                "pension": str(ibc_pror),
                "arl": str(ibc_pror),
                "parafiscales": str(ibc_pror),
            }
        else:
            # IGE/LMA/IRL/SLN: salario básico × (días novedad / 30), no IBC mes anterior
            ibc_pror_incap = _prorratear_ibc(float(salario_contrato), dias_incap)
            ibc_incap = {
                "salud": str(ibc_pror_incap),
                "pension": str(ibc_pror_incap),
                "arl": str(ibc_pror_incap),  # IBC riesgos = IBC salud; tarifa 0% solo IGE/LMA en microservicio
                "parafiscales": str(ibc_pror_incap),
            }
        # IGE/LMA/IRL: días ARL = días salud, IBC ARL = IBC salud; tarifa 0% solo IGE/LMA
        dias_arl_incap = dias_incap
        registros.append({
            "tipo_linea": nov_incap["codigo"],  # IGE, IRL, LMA
            "dias": {
                "salud": dias_incap,
                "pension": dias_incap,
                "arl": dias_arl_incap,
                "caja": dias_incap,
            },
            "ibc": ibc_incap,
            "novedades": [nov_incap],
        })
        dias_usados += dias_incap

    # 3. Línea de VSP (si aplica, con IBC mes actual; 0 días → IBC 0)
    if novedad_vsp:
        if salario_integral:
            ibc_vsp_val = _prorratear_ibc(ibc_integral_mes, 0)  # 0 días
            ibc_vsp = {
                "salud": str(ibc_vsp_val),
                "pension": str(ibc_vsp_val),
                "arl": str(ibc_vsp_val),
                "parafiscales": str(ibc_vsp_val),
            }
        else:
            ibc_vsp = {
                "salud": str(_redondear_ibc(ibc_actual["salud_pension"])),
                "pension": str(_redondear_ibc(ibc_actual["salud_pension"])),
                "arl": str(_redondear_ibc(ibc_actual["arl"])),
                "parafiscales": str(_redondear_ibc(ibc_actual["caja"])),
            }
        registros.append({
            "tipo_linea": "VSP",
            "dias": {
                "salud": 0,
                "pension": 0,
                "arl": 0,
                "caja": 0,
            },
            "ibc": ibc_vsp,
            "novedades": [novedad_vsp],
        })
    
    # 4. Línea normal (días trabajados con IBC mes actual o salario + VST)
    dias_normales = dias_base - dias_usados
    if dias_normales < 0:
        dias_normales = 0
    
    # Si no hay novedades que generen líneas separadas, crear una línea normal con todos los días
    if not registros:
        dias_normales = dias_base
    
    # Calcular IBC para línea normal
    novedades_normal = list(novedades_ing_ret)  # ING/RET van en línea normal

    if salario_integral:
        # Salario integral: IBC = (70% salario + VST) × (días cotizados / 30)
        ibc_base_integral = salario_contrato * factor_integral + vst
        ibc_pror_normal = _prorratear_ibc(ibc_base_integral, dias_normales)
        ibc_normal = {
            "salud": str(ibc_pror_normal),
            "pension": str(ibc_pror_normal),
            "arl": str(ibc_pror_normal),
            "parafiscales": str(ibc_pror_normal),
        }
        if vst > 0:
            fecha_vst = fecha_periodo.isoformat() if fecha_periodo else date.today().isoformat()
            novedades_normal.append({
                "codigo": "VST",
                "fecha_desde": fecha_vst,
                "fecha_hasta": fecha_vst,
                "dias": None,
                "valor_vst": vst,
            })
    elif vst > 0:
        # VST sin integral: IBC = (salario + VST) × (días normales / 30)
        ibc_base_vst = salario_contrato + vst
        ibc_pror_normal = _prorratear_ibc(ibc_base_vst, dias_normales)
        ibc_normal = {
            "salud": str(ibc_pror_normal),
            "pension": str(ibc_pror_normal),
            "arl": str(ibc_pror_normal),
            "parafiscales": str(ibc_pror_normal),
        }
        fecha_vst = fecha_periodo.isoformat() if fecha_periodo else date.today().isoformat()
        novedades_normal.append({
            "codigo": "VST",
            "fecha_desde": fecha_vst,
            "fecha_hasta": fecha_vst,
            "dias": None,
            "valor_vst": vst,
        })
    else:
        # Sin VST y no integral: IBC proporcional a días normales
        # Si hay múltiples líneas: salario básico × (días normales / 30)
        # Si solo línea normal (30 días): IBC del mes desde nómina (basesegsocial)
        if dias_normales < dias_base:
            # Múltiples líneas: salario básico proporcional a días
            ibc_pror = _prorratear_ibc(float(salario_contrato), dias_normales)
            ibc_normal = {
                "salud": str(ibc_pror),
                "pension": str(ibc_pror),
                "arl": str(ibc_pror),
                "parafiscales": str(ibc_pror),
            }
        else:
            # Solo línea normal (30 días): IBC completo del mes desde nómina
            ibc_normal = {
                "salud": str(_redondear_ibc(ibc_actual["salud_pension"])),
                "pension": str(_redondear_ibc(ibc_actual["salud_pension"])),
                "arl": str(_redondear_ibc(ibc_actual["arl"])),
                "parafiscales": str(_redondear_ibc(ibc_actual["caja"])),
            }
    
    # Línea normal siempre se crea (aunque tenga 0 días si hubo novedades)
    registros.append({
        "tipo_linea": "NORMAL",
        "dias": {
            "salud": dias_normales,
            "pension": dias_normales,
            "arl": dias_normales,
            "caja": dias_normales,
        },
        "ibc": ibc_normal,
        "novedades": novedades_normal,
    })
    
    return registros