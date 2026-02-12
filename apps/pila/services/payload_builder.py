# nomiweb/apps/pila/services/payload_builder.py

from datetime import date
import calendar
from decimal import Decimal
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

    # Empresa: datos reales (ORM solo lectura, managed=False ok)
    empresa = Empresa.objects.only(
        "empresa_exonerada",
        "nit",
        "dv",
        "nombreempresa",
        "tipodoc",
        "tipoaportante",
        "claseaportante"
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

    # 3) IBC por contrato (indicadores 6/16/17)
    ibc_map = _get_ibc_por_contrato_mes(
        empresa_id=empresa_id_interno,
        mesacumular=mesacumular,
        ano=ano,
        ids_contrato=ids_contrato
    )

    # 4) Armar empleados reales
    empleados = []
    for row in rows:
        idcontrato = int(row["idcontrato"])

        tipo_cot = str(row["tipo_cotizante"]).zfill(2)
        subtipo_cot = str(row["subtipo_cotizante"]).zfill(2)
        flags_tc = _get_flags_tipo_cotizante(tipo_cot)

        # --- Días base (mes comercial) + ausencias para ARL ---
        dias_base = _dias_base_contrato_mes(
            fechainicio=row["fechainiciocontrato"],
            fechafin=row["fechafincontrato"],
            mesacumular=mesacumular,
            ano=ano
        )

        vac_tipo = _dias_vacaciones_en_mes_por_tipo(
            empresa_id=empresa_id_interno,
            idcontrato=idcontrato,
            mesacumular=mesacumular,
            ano=ano
        )

        dias_arl = _dias_arl_mes(dias_base, vac_tipo)
        dias = _build_dias_por_subsistema(dias_base, dias_arl)
        
        novedades = []
        novedades += _novedades_ing_ret_mes(
            row["fechainiciocontrato"],
            row["fechafincontrato"],
            mesacumular,
            ano
        )
        novedades += _novedades_vacaciones_mes(
            empresa_id=empresa_id_interno,
            idcontrato=idcontrato,
            mesacumular=mesacumular,
            ano=ano
        )
        novedades += _novedades_incapacidades_mes(
            empresa_id=empresa_id_interno,
            idcontrato=idcontrato,
            mesacumular=mesacumular,
            ano=ano
        )
        # --- IBC por contrato ---
        ibc = ibc_map.get(idcontrato, {"salud_pension": Decimal("0"), "arl": Decimal("0"), "caja": Decimal("0")})

        empleados.append({
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
                "salario_integral": (row["tiposalario_id"] == 2),
            },

            "dias": {
                "salud": dias["salud"],
                "pension": dias["pension"],
                "arl": dias["arl"],
                "caja": dias["caja"],
            },

            "ibc": {
                "salud": str(ibc["salud_pension"]),
                "pension": str(ibc["salud_pension"]),
                "arl": str(ibc["arl"]),
                "parafiscales": str(ibc["caja"]),
            },

            "tarifas": {
                "arl": str(row["tarifa_arl"]) if row["tarifa_arl"] else None
            },
            "novedades": novedades,
        })

    payload = {
        "empresa": {
            "id_interno": empresa_id_interno,
            "nit": f"{empresa.nit}{empresa.dv or ''}",  # NIT + dígito verificación
            "razon_social": empresa.nombreempresa or "",
            "sucursal": "",  # En blanco: tipo presentación única
            "tipo_documento_aportante": empresa.tipodoc or "NI",
            "tipo_aportante": str(empresa.tipoaportante or "1").zfill(2),  # 01=Empleador
            "clase_aportante": empresa.claseaportante or "A",
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
        "parametros": _get_parametros_pila(periodo),
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

    return {
        "smmlv": smmlv,
        "tope_ibc_smmlv": tope_ibc_smmlv,
        "dias_base": 30,
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

      ciu.coddepartamento            AS cod_departamento,
      ciu.codciudad                  AS cod_municipio,

      c.salario::numeric             AS salario_basico,
      c.tiposalario_id               AS tiposalario_id,

      tc.tipocotizante               AS tipo_cotizante,
      st.subtipocotizante            AS subtipo_cotizante,

      eps.codigo                     AS eps_codigo,
      afp.codigo                     AS afp_codigo,
      ccf.codigo                     AS ccf_codigo,
      arl.codigo                     AS arl_codigo,

      ct.tarifaarl::numeric          AS tarifa_arl

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
    JOIN public.entidadessegsocial afp
      ON afp.identidad = c.codafp_id
    JOIN public.entidadessegsocial ccf
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