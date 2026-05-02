# nomiweb/apps/pila/services/payload_builder.py

from datetime import date
import calendar
import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)
from django.db import connection
from datetime import timedelta
from apps.common.models import Empresa


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


def _ultimo_dia_mes_pila(ano: int, mes_num: int) -> int:
    """
    Último día del mes para construir fechas válidas.
    PILA usa mes comercial 1..30, pero febrero tiene 28/29 días: no se puede usar date(ano, 2, 30).
    """
    return min(30, calendar.monthrange(ano, mes_num)[1])


def build_payload_pila_minimo(*, empresa_id_interno: int, periodo: str) -> dict:
    """
    Payload mínimo v1 (loop real por contratos con movimiento).
    - empresa_id_interno: idempresa en tu BD
    - periodo: 'YYYY-MM'

    Nómina cerrada: crearnomina.estadonomina = FALSE. Líneas definitivas: nomina.estadonomina = 2.
    """
    hoy = date.today().isoformat()

    ano = int(periodo.split("-")[0])
    mes_num = int(periodo.split("-")[1])
    mesacumular = _MESES_INV.get(mes_num)
    if not mesacumular:
        raise ValueError(f"Mes inválido en periodo={periodo}")

    # Parámetros generales PILA (incluye SMMLV, tope IBC y factor salarial integral)
    parametros_pila = _get_parametros_pila(periodo)

    # Empresa: datos reales (ORM solo lectura, managed=False ok)
    empresa = Empresa.objects.only(
        "empresa_exonerada",
        "ige100",
        "nit",
        "dv",
        "nombreempresa",
        "tipodoc",
        "tipoaportante",
        "claseaportante",
        "tipo_presentacion_planilla",
        "arl",
        "codigo_sucursal",
        "nombre_sucursal",
    ).get(idempresa=empresa_id_interno)
    empresa_flags = {"empresa_exonerada": bool(empresa.empresa_exonerada)}

    # Incapacidades: 100% si ige100=SI, si no => 2/3 (66,67%)
    ige100_val = (empresa.ige100 or "").strip().upper()
    factor_incapacidad = Decimal("1") if ige100_val == "SI" else (Decimal("2") / Decimal("3"))

    smmlv_dec = Decimal(str(parametros_pila["smmlv"]))

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

    # 3.0) Exceso Ley 1393: si IBC < 60% total ingresos, exceso = 0.6*total - IBC. Se suma a salud, pensión, ARL
    exceso_ley_1393 = _get_exceso_ley_1393_por_contrato(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato,
        ibc_map=ibc_map,
    )
    for idc, exc in exceso_ley_1393.items():
        if idc in ibc_map and exc > 0:
            ibc_map[idc]["salud_pension"] += exc
            ibc_map[idc]["arl"] += exc
            # CCF/SENA/ICBF: NO se agrega el exceso (Ley 1393 solo aplica a salud, pensión, ARL)

    # 3.2) VST por contrato (indicador 29) para línea NORMAL: si VST > 0, registrar novedad
    vst_map = _get_vst_por_contrato_mes(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato,
    )

    # 3.1) IBC del mes anterior (para novedades VAC, IGE, IRL, LMA)
    ibc_map_anterior = _get_ibc_mes_anterior(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato
    )
    # Aplicar exceso Ley 1393 al mes anterior (para líneas de novedad)
    exceso_anterior = _get_exceso_ley_1393_mes_anterior(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato,
        ibc_map_anterior=ibc_map_anterior,
    )
    for idc, exc in exceso_anterior.items():
        if idc in ibc_map_anterior and exc > 0:
            ibc_map_anterior[idc]["salud_pension"] += exc
            ibc_map_anterior[idc]["arl"] += exc

    # 4) Armar empleados reales con múltiples registros si tienen novedades
    empleados = []
    for row in rows:
        idcontrato = int(row["idcontrato"])

        tipo_cot = str(row["tipo_cotizante"]).zfill(2)
        subtipo_cot = str(row["subtipo_cotizante"]).zfill(2)
        flags_tc = _get_flags_tipo_cotizante(tipo_cot)
        salario_integral_flag = (row["tiposalario_id"] == 2)

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

        # Ajuste por salario integral: aplicar factor conceptosfijos.idfijo=1
        factor_integral = parametros_pila.get("factor_integral")
        if salario_integral_flag and factor_integral:
            factor_dec = Decimal(str(factor_integral))
            ibc_actual = _ajustar_ibc_salario_integral(ibc_actual, factor_dec)
            ibc_anterior = _ajustar_ibc_salario_integral(ibc_anterior, factor_dec)

        # --- Generar registros (uno o múltiples líneas tipo 02) ---
        vst = vst_map.get(idcontrato, Decimal("0"))
        salario_contrato = int(row["salario_basico"] or 0)

        fecha_periodo = date(ano, mes_num, 1)
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
            fecha_periodo=fecha_periodo,
            factor_incapacidad=factor_incapacidad,
            smmlv=smmlv_dec,
        )

        clase_riesgo = _tarifa_arl_a_clase_riesgo(row.get("tarifa_arl"))
        # Campo 62 TXT: centrotrabajo.codigo_operador si viene informado; si no, centrotrabajo_id del contrato
        codigo_centro_trabajo = row.get("codigo_centro_trabajo")

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
            "clase_riesgo": clase_riesgo,
            "codigo_centro_trabajo": codigo_centro_trabajo,  # ct.codigo_operador o fallback centrotrabajo_id

            "entidades": {
                "eps": row["eps_codigo"],
                "afp": row["afp_codigo"],
                "arl": row["arl_codigo"],
                "caja": row["ccf_codigo"],
            },

            "flags": {
                **flags_tc,
                "salario_integral": salario_integral_flag,
            },

            "tarifas": {
                "arl": str(row["tarifa_arl"]) if row["tarifa_arl"] else None
            },
            "actividad_economica_arl": row.get("actividad_economica_arl") or "",
            "exceso_ley_1393": int(exceso_ley_1393.get(idcontrato, Decimal("0"))),
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
            "sucursal": "",  # En blanco: tipo presentación única (legacy)
            "tipo_documento_aportante": empresa.tipodoc or "NI",
            "tipo_aportante": str(empresa.tipoaportante or "1").zfill(2),  # 01=Empleador
            "clase_aportante": empresa.claseaportante or "A",
            "tipo_presentacion_planilla": empresa.tipo_presentacion_planilla or "U",  # U=única, S=sucursal
            "codigo_arl": codigo_arl_empresa,  # Código ARL de la empresa (6 caracteres)
            "codigo_sucursal": (empresa.codigo_sucursal or ""),  # PILA encabezado campo 12
            "nombre_sucursal": (empresa.nombre_sucursal or ""),  # PILA encabezado campo 13
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
        "parametros": parametros_pila,
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

        # Factor salarial integral (ej. 70%): conceptosfijos.idfijo = 1
        cursor.execute("SELECT valorfijo FROM public.conceptosfijos WHERE idfijo = 1")
        row = cursor.fetchone()
        if not row:
            raise ValueError("No existe conceptosfijos idfijo=1 (FACTOR SALARIO INTEGRAL)")
        factor_integral = Decimal(str(row[0])) / Decimal("100")

    return {
        "smmlv": smmlv,
        "tope_ibc_smmlv": tope_ibc_smmlv,
        "dias_base": 30,
        # En el payload debe ser JSON‑serializable (float). Para cálculos internos
        # se convierte de nuevo a Decimal.
        "factor_integral": float(factor_integral),
    }


def _ajustar_ibc_salario_integral(ibc: dict, factor_integral: Decimal) -> dict:
    """
    Aplica el factor de salario integral al IBC por subsistema.
    """
    return {
        "salud_pension": (ibc["salud_pension"] * factor_integral),
        "arl": (ibc["arl"] * factor_integral),
        "caja": (ibc["caja"] * factor_integral),
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


# Tarifa ARL % -> clase_riesgo (1-5) para PILA campo 78 pos 513
# codigo_centro_trabajo (campo 62): centrotrabajo.codigo_operador si existe; si no, centrotrabajo_id
_TARIFA_ARL_A_CLASE = {
    Decimal("0.522"): "1",
    Decimal("1.044"): "2",
    Decimal("2.436"): "3",
    Decimal("4.350"): "4",
    Decimal("6.960"): "5",
}


def _tarifa_arl_a_clase_riesgo(tarifa) -> str:
    """Tarifa ARL (porcentaje) -> clase_riesgo "1"-"5"."""
    if tarifa is None:
        return "1"
    t = Decimal(str(tarifa)).quantize(Decimal("0.001"))
    for k, clase in _TARIFA_ARL_A_CLASE.items():
        if abs(t - k) < Decimal("0.001"):
            return clase
    return "1"


def _get_contratos_con_movimiento_mes(empresa_id: int, mesacumular: str, ano: int) -> list[int]:
    """
    Contratos con líneas de nómina en el periodo.
    El alcance es por empresa del contrato y de la liquidación (no por conceptosdenomina.id_empresa_id),
    para no excluir empleados cuyos conceptos no repiten id_empresa (p. ej. liquidación vs nómina regular).
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT n.idcontrato_id
            FROM public.nomina n
            JOIN public.crearnomina cn
              ON cn.idnomina = n.idnomina_id
            JOIN public.anos a
              ON a.idano = cn.anoacumular_id
            JOIN public.contratos c
              ON c.idcontrato = n.idcontrato_id
             AND c.id_empresa_id = %s
            WHERE cn.id_empresa_id = %s
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
      ct.actividad_economica_arl     AS actividad_economica_arl,

      CASE
        WHEN ct.codigo_operador IS NOT NULL
             AND NULLIF(BTRIM(ct.codigo_operador::text), '') IS NOT NULL
        THEN CAST(NULLIF(BTRIM(ct.codigo_operador::text), '') AS INTEGER)
        ELSE c.centrotrabajo_id
      END                            AS codigo_centro_trabajo

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
    """
    IBC por contrato para el mes de liquidación, desglosado por subsistema.

    Cuando nomina.control coincide con vacaciones.idvacaciones (ausentismo que cruza meses),
    el valor de la línea se prorratea a los días que caen dentro del mes en liquidación:
        valor × GREATEST(0, dias_en_mes) / diasvac
    Si no hay vínculo con vacaciones (control nulo o sin coincidencia), se suma el valor completo.
    El prorrateо aplica a los tres subsistemas (salud/pensión, ARL, CCF) por igual.
    Filtrado siempre por id_empresa_id en contratos y vacaciones.
    """
    mes_num = _MESES[mesacumular.upper().strip()]
    ini_mes = date(ano, mes_num, 1)
    fin_mes = date(ano, mes_num, calendar.monthrange(ano, mes_num)[1])

    sql = """
    SELECT
      n.idcontrato_id,
      SUM(CASE WHEN cdi.indicador_id = 6 THEN
        CASE
          WHEN v.idvacaciones IS NOT NULL AND COALESCE(v.diasvac, 0) > 0
          THEN ROUND(
            COALESCE(n.valor, 0)::numeric
            * GREATEST(0, (LEAST(v.ultimodiavac, %s) - GREATEST(v.fechainicialvac, %s))::int + 1)
            / v.diasvac::numeric
          )
          ELSE COALESCE(n.valor, 0)
        END
      ELSE 0 END) AS ibc_salud_pension,
      SUM(CASE WHEN cdi.indicador_id = 16 THEN
        CASE
          WHEN v.idvacaciones IS NOT NULL AND COALESCE(v.diasvac, 0) > 0
          THEN ROUND(
            COALESCE(n.valor, 0)::numeric
            * GREATEST(0, (LEAST(v.ultimodiavac, %s) - GREATEST(v.fechainicialvac, %s))::int + 1)
            / v.diasvac::numeric
          )
          ELSE COALESCE(n.valor, 0)
        END
      ELSE 0 END) AS ibc_arl,
      SUM(CASE WHEN cdi.indicador_id = 17 THEN
        CASE
          WHEN v.idvacaciones IS NOT NULL AND COALESCE(v.diasvac, 0) > 0
          THEN ROUND(
            COALESCE(n.valor, 0)::numeric
            * GREATEST(0, (LEAST(v.ultimodiavac, %s) - GREATEST(v.fechainicialvac, %s))::int + 1)
            / v.diasvac::numeric
          )
          ELSE COALESCE(n.valor, 0)
        END
      ELSE 0 END) AS ibc_caja
    FROM public.nomina n
    JOIN public.crearnomina cn ON cn.idnomina = n.idnomina_id
    JOIN public.anos a ON a.idano = cn.anoacumular_id
    JOIN public.contratos c ON c.idcontrato = n.idcontrato_id AND c.id_empresa_id = %s
    JOIN public.conceptosdenomina cd ON cd.idconcepto = n.idconcepto_id
    JOIN public.conceptosdenomina_indicador cdi ON cdi.conceptosdenomina_id = cd.idconcepto
    LEFT JOIN public.vacaciones v
           ON v.idvacaciones = n.control
          AND v.id_empresa_id = %s
    WHERE cn.id_empresa_id = %s
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
        cursor.execute(
            sql,
            [
                fin_mes, ini_mes,   # prorrateо ind. 6
                fin_mes, ini_mes,   # prorrateo ind. 16
                fin_mes, ini_mes,   # prorrateo ind. 17
                empresa_id,         # JOIN contratos
                empresa_id,         # LEFT JOIN vacaciones
                empresa_id,         # WHERE cn.id_empresa_id
                mesacumular, ano, ids_contrato,
            ],
        )
        rows = cursor.fetchall()

    out = {}
    for idcontrato, ibc_ss, ibc_arl, ibc_caja in rows:
        out[int(idcontrato)] = {
            "salud_pension": Decimal(str(ibc_ss or 0)),
            "arl": Decimal(str(ibc_arl or 0)),
            "caja": Decimal(str(ibc_caja or 0)),
        }
    return out


def _get_vst_por_contrato_mes(
    empresa_id: int,
    mesacumular: str,
    ano: int,
    ids_contrato: list[int],
) -> dict[int, Decimal]:
    """
    VST = suma de nomina.valor donde idconcepto tiene indicador_id=29
    (Variación transitoria de salario PILA).
    Cada línea de nomina se cuenta una sola vez (EXISTS), aunque el concepto tenga más indicadores.
    Retorna dict {idcontrato: valor_vst}
    """
    if not ids_contrato:
        return {}
    sql = """
    SELECT
      n.idcontrato_id,
      COALESCE(SUM(
        CASE
          WHEN EXISTS (
            SELECT 1
            FROM public.conceptosdenomina_indicador cdi
            WHERE cdi.conceptosdenomina_id = cd.idconcepto
              AND cdi.indicador_id = 29
          )
          THEN COALESCE(n.valor, 0)
          ELSE 0
        END
      ), 0) AS vst
    FROM public.nomina n
    JOIN public.crearnomina cn ON cn.idnomina = n.idnomina_id
    JOIN public.anos a ON a.idano = cn.anoacumular_id
    JOIN public.contratos c ON c.idcontrato = n.idcontrato_id AND c.id_empresa_id = %s
    JOIN public.conceptosdenomina cd ON cd.idconcepto = n.idconcepto_id
    WHERE cn.id_empresa_id = %s
      AND cn.mesacumular = %s
      AND a.ano = %s
      AND cn.estadonomina = FALSE
      AND n.estadonomina = 2
      AND n.idcontrato_id = ANY(%s)
    GROUP BY n.idcontrato_id;
    """
    out = {c: Decimal("0") for c in ids_contrato}
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [empresa_id, empresa_id, mesacumular, ano, ids_contrato])
            for idc, vst in cursor.fetchall():
                out[int(idc)] = Decimal(str(vst or 0))
    except Exception:
        logger.exception(
            "PILA: falló _get_vst_por_contrato_mes (empresa_id=%s mes=%s año=%s contratos=%s)",
            empresa_id,
            mesacumular,
            ano,
            ids_contrato[:20],
        )
    return out


def _get_exceso_ley_1393_por_contrato(
    empresa_id: int,
    mesacumular: str,
    ano: int,
    ids_contrato: list[int],
    ibc_map: dict[int, dict],
) -> dict[int, Decimal]:
    """
    Ley 1393 art. 30: si IBC < 60% del total ingresos, hay exceso.
    exceso_ley_1393 = max(0, 0.6 * total_ingresos - IBC).
    total_ingresos = suma de conceptos vinculados al indicador base1393 (id=12).
    Se suma al IBC de salud, pensión y ARL (NO a SENA, ICBF, CCF).
    Salario integral: no aplica (se excluye).
    """
    out = {c: Decimal("0") for c in ids_contrato}
    sql = """
    SELECT
      n.idcontrato_id,
      COALESCE(SUM(CASE WHEN COALESCE(n.valor,0) > 0 THEN n.valor ELSE 0 END), 0) AS total_ingresos
    FROM public.nomina n
    JOIN public.crearnomina cn ON cn.idnomina = n.idnomina_id
    JOIN public.anos a ON a.idano = cn.anoacumular_id
    JOIN public.contratos c ON c.idcontrato = n.idcontrato_id AND c.id_empresa_id = %s
    JOIN public.conceptosdenomina cd ON cd.idconcepto = n.idconcepto_id
    JOIN public.conceptosdenomina_indicador cdi ON cdi.conceptosdenomina_id = cd.idconcepto AND cdi.indicador_id = 12
    WHERE cn.id_empresa_id = %s
      AND cn.mesacumular = %s
      AND a.ano = %s
      AND cn.estadonomina = FALSE
      AND n.estadonomina = 2
      AND n.idcontrato_id = ANY(%s)
    GROUP BY n.idcontrato_id;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [empresa_id, empresa_id, mesacumular, ano, ids_contrato])
            for idc, total_ing in cursor.fetchall():
                if idc not in ibc_map:
                    continue
                ibc_sp = ibc_map[int(idc)]["salud_pension"]
                total_ing = Decimal(str(total_ing or 0))
                ibc_min = total_ing * Decimal("0.6")
                if ibc_sp < ibc_min:
                    exc = (ibc_min - ibc_sp).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                    out[int(idc)] = exc

        # Excluir salario integral
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT idcontrato FROM public.contratos WHERE tiposalario_id = 2 AND idcontrato = ANY(%s)",
                [ids_contrato],
            )
            for (idc,) in cursor.fetchall():
                out[int(idc)] = Decimal("0")
    except Exception:
        pass
    return out


def _get_exceso_ley_1393_mes_anterior(
    empresa_id: int,
    mesacumular: str,
    ano: int,
    ids_contrato: list[int],
    ibc_map_anterior: dict[int, dict],
) -> dict[int, Decimal]:
    """Exceso Ley 1393 para el mes anterior (para líneas de novedad VAC, IGE, etc.)."""
    mes_num = _MESES[mesacumular.upper().strip()]
    if mes_num == 1:
        mes_anterior_num, ano_anterior = 12, ano - 1
    else:
        mes_anterior_num, ano_anterior = mes_num - 1, ano
    mesacumular_anterior = _MESES_INV.get(mes_anterior_num)
    return _get_exceso_ley_1393_por_contrato(
        empresa_id=empresa_id,
        mesacumular=mesacumular_anterior,
        ano=ano_anterior,
        ids_contrato=ids_contrato,
        ibc_map=ibc_map_anterior,
    )


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


def _dias_base_contrato_mes(
    fechainicio: date | None,
    fechafin: date | None,
    mesacumular: str,
    ano: int,
) -> int:
    """
    Mes comercial PILA: 1..30.
    Si el contrato abarca todo el mes (del día 1 al último día del mes), se reportan 30 días.
    Si no, se reportan los días calendario del rango (máximo 30).
    """
    if not fechainicio:
        return 0

    mes_num = _MESES[mesacumular.upper().strip()]
    ini_mes = date(ano, mes_num, 1)
    last_day_real = calendar.monthrange(ano, mes_num)[1]

    # Recorte del rango al mes real (evita contar días fuera del mes real)
    ini = max(fechainicio, ini_mes)
    fin_mes_real = date(ano, mes_num, last_day_real)
    fin_real_date = fin_mes_real if fechafin is None else min(fechafin, fin_mes_real)
    if fin_real_date < ini:
        return 0

    # En PILA se contabiliza el "mes comercial" hasta el día 30:
    # si el contrato llega al final del mes real (o no tiene fin), se extiende a 30.
    fin_pila_day = 30 if fin_real_date == fin_mes_real else fin_real_date.day

    # Mes completo en PILA = 30 días cotizados (Error 382 exige 30 en los 4 subsistemas)
    if ini == ini_mes and fin_real_date == fin_mes_real:
        return 30

    dias = fin_pila_day - ini.day + 1
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
    fin_mes = date(ano, mes_num, _ultimo_dia_mes_pila(ano, mes_num))

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
    fin_mes = date(ano, mes_num, _ultimo_dia_mes_pila(ano, mes_num))  # mes comercial PILA (feb 28/29)

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
                5: "SLN",
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
    fin_mes = date(ano, mes_num, _ultimo_dia_mes_pila(ano, mes_num))

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
    fin_mes = date(ano, mes_num, _ultimo_dia_mes_pila(ano, mes_num))
    
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
    vst: Decimal = Decimal("0"),
    salario_contrato: int = 0,
    fecha_periodo: date | None = None,
    factor_incapacidad: Decimal = Decimal("1"),
    smmlv: Decimal = Decimal("0"),
) -> list[dict]:
    """
    Genera uno o más registros tipo 02 por empleado según novedades.
    
    Reglas:
    - Novedades que generan líneas separadas: VAC, IGE, IRL, LMA, SLN, VSP
    - Novedades que van en línea normal: ING, RET
    - Cada línea tiene sus propios días e IBC
    """
    registros = []
    dias_usados = 0
    
    # 1. Líneas de vacaciones, SLN y SUSP
    # Regla IBC por subsistema:
    # - Salud, pensión, ARL: IBC mes anterior (último salario reportado antes de la novedad)
    # - CCF (parafiscales): VAC = IBC mes actual proporcional por días; SLN/SUSP = 0 (sin pago)
    for nov_vac in novedades_vac:
        if nov_vac["codigo"] == "VAC":  # Solo vacaciones tipo 1
            dias_vac = nov_vac["dias"]
            # CCF: IBC mes ACTUAL proporcional (valor pagado por esos días)
            ibc_ccf_vac = int((ibc_actual["caja"] * Decimal(dias_vac) / Decimal(30)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            # Salud / pensión / ARL: IBC mes ANTERIOR proporcional por días (dias/30)
            factor_vac = Decimal(dias_vac) / Decimal(30)
            ibc_vac_salud = int((ibc_anterior["salud_pension"] * factor_vac).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            ibc_vac_pension = ibc_vac_salud
            # ARL: Aportesenlinea EXIGE que días e IBC de ARL sean IGUALES a salud/pensión
            # aunque no se cobra ARL (tarifa/cotización=0). La novedad VAC indica al operador que no cobre.
            ibc_vac_arl = ibc_vac_salud
            registros.append({
                "tipo_linea": "VAC",
                "dias": {
                    "salud": dias_vac,
                    "pension": dias_vac,
                    "arl": dias_vac,
                    "caja": dias_vac,
                },
                "ibc": {
                    "salud": str(ibc_vac_salud),
                    "pension": str(ibc_vac_pension),
                    "arl": str(ibc_vac_arl),
                    "parafiscales": str(ibc_ccf_vac),
                },
                "novedades": [nov_vac],
            })
            dias_usados += dias_vac
        elif nov_vac["codigo"] in ("SLN", "SUSP"):
            dias_nov = nov_vac["dias"]
            # CCF: IBC = 0 (sin pago remunerado, sin base para caja)
            # ARL: Aportesenlinea EXIGE días e IBC iguales a salud (novedad SLN indica no cobro)
            registros.append({
                "tipo_linea": nov_vac["codigo"],
                "dias": {
                    "salud": dias_nov,
                    "pension": dias_nov,
                    "arl": dias_nov,
                    "caja": dias_nov,
                },
                "ibc": {
                    "salud": str(ibc_anterior["salud_pension"]),
                    "pension": str(ibc_anterior["salud_pension"]),
                    "arl": str(ibc_anterior["salud_pension"]),
                    "parafiscales": "0",
                },
                "novedades": [nov_vac],
            })
            dias_usados += dias_nov
    
    # 2. Líneas de incapacidades (IGE, IRL, LMA) con salario proporcional por días
    for nov_incap in novedades_incap:
        dias_incap = nov_incap["dias"]
        factor_dias = Decimal(dias_incap) / Decimal(30)

        # Incapacidades: base seg social del mes anterior = indicador 6
        # (en el payload se guarda como ibc_anterior["salud_pension"]).
        #
        # Regla por tipo:
        # - IGE: 100% si empresa.ige100=SI, si NO => 2/3
        # - IRL y LMA: siempre 100%
        ibc_mes_anterior_base = ibc_anterior.get("salud_pension", Decimal("0"))
        factor_aplicar = factor_incapacidad if nov_incap.get("codigo") == "IGE" else Decimal("1")
        ibc_ajustado_mes = ibc_mes_anterior_base * factor_aplicar

        ibc_calc = ibc_ajustado_mes * factor_dias
        smmlv_prop = smmlv * factor_dias
        ibc_final = ibc_calc if ibc_calc >= smmlv_prop else smmlv_prop

        ibc_incap_valor = int(ibc_final.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        registros.append({
            "tipo_linea": nov_incap["codigo"],  # IGE, IRL, LMA
            "dias": {
                "salud": dias_incap,
                "pension": dias_incap,
                "arl": dias_incap,
                "caja": dias_incap,
            },
            "ibc": {
                "salud": str(ibc_incap_valor),
                "pension": str(ibc_incap_valor),
                "arl": str(ibc_incap_valor),
                "parafiscales": str(ibc_incap_valor),
            },
            "novedades": [nov_incap],
        })
        dias_usados += dias_incap
    
    # 3. Línea de VSP (si aplica, con IBC mes actual)
    if novedad_vsp:
        # VSP puede ir en línea separada o junto con días normales
        # Por ahora la ponemos separada
        registros.append({
            "tipo_linea": "VSP",
            "dias": {
                "salud": 0,
                "pension": 0,
                "arl": 0,
                "caja": 0,
            },
            "ibc": {
                "salud": str(ibc_actual["salud_pension"]),
                "pension": str(ibc_actual["salud_pension"]),
                "arl": str(ibc_actual["arl"]),
                "parafiscales": str(ibc_actual["caja"]),
            },
            "novedades": [novedad_vsp],
        })
    
    # 4. Línea normal (días trabajados con IBC mes actual)
    dias_normales = dias_base - dias_usados
    if dias_normales < 0:
        dias_normales = 0
    
    # Si no hay novedades que generen líneas separadas, crear una línea normal con todos los días
    if not registros:
        dias_normales = dias_base

    # VST (línea NORMAL):
    # - Si suma(indicador 29) > 0: novedad VST con ese valor e IBC = salario_básico×(días/30)+VST (VST sin prorratear).
    # - Si no hay ind.29 pero IBC(ind.6) > salario contractual: VST = diferencia (tolerancia 1 $).
    novedades_normal = list(novedades_ing_ret)  # ING/RET van en línea normal
    ibc_sp = ibc_actual.get("salud_pension", Decimal("0"))
    vst_valor = max(Decimal("0"), vst)
    # Tolerancia por redondeo: el validor puede exigir VST cuando IBC > salario,
    # pero diferencias "menores" (ej. 1 peso) pueden ser solo efecto de redondeos.
    tolerancia_vst = Decimal("1")
    if vst_valor <= 0 and salario_contrato > 0 and ibc_sp > salario_contrato:
        # VST no en indicador 29 pero IBC > salario (ej. VST incluida en basesegsocial)
        diff = ibc_sp - Decimal(str(salario_contrato))
        if diff <= tolerancia_vst:
            vst_valor = Decimal("0")
        else:
            vst_valor = diff

    if vst_valor > 0:
        fecha_vst = (fecha_periodo or date.today()).isoformat()
        vst_pesos = int(vst_valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        novedades_normal.append({
            "codigo": "VST",
            "fecha_desde": fecha_vst,
            "fecha_hasta": fecha_vst,
            "dias": None,
            "valor": vst_pesos,
        })
    
    # IBC línea NORMAL:
    # - Sin VST (vst_valor=0) y única línea 30 días: usar IBC del mes desde nómina (ind. 6/16/17).
    # - Con VST > 0: siempre salario proporcional (días/30) + importe VST (no se prorratea por días).
    if dias_normales >= 30 and not registros and vst_valor <= 0:
        ibc_normal = {
            "salud": str(ibc_actual["salud_pension"]),
            "pension": str(ibc_actual["salud_pension"]),
            "arl": str(ibc_actual["arl"]),
            "parafiscales": str(ibc_actual["caja"]),
        }
    else:
        factor = Decimal(dias_normales) / Decimal(30)
        salario_prop = (Decimal(str(salario_contrato or 0)) * factor).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        ibc_normal_valor = int((salario_prop + Decimal(int(vst_valor))))
        ibc_normal = {
            "salud": str(ibc_normal_valor),
            "pension": str(ibc_normal_valor),
            "arl": str(ibc_normal_valor),
            "parafiscales": str(ibc_normal_valor),
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