from multiprocessing import Value
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from apps.common.models import Crearnomina , Contratos , Nomina , Salariominimoanual
from apps.components.decorators import  role_required

@login_required
@role_required('accountant')
def withholding_tax(request, idnomina):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    try:
        nomina = Crearnomina.objects.get(idnomina=idnomina)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"

    # , idcontrato_id = 8113
    empleados_raw = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=idnomina, estadonomina=1  ) \
        .values(
            'idcontrato__idempleado__docidentidad',
            'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__sapellido',
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__snombre',
            'idcontrato__salario',
            'idcontrato'
        ) \
        .order_by('idcontrato__idempleado__papellido') \
        .distinct()

    empleados = []
    for e in empleados_raw:
        doc = e.get('idcontrato__idempleado__docidentidad')
        if not doc or str(doc).strip().lower() == "no data":
            doc = ""

        nombres = [
            e.get('idcontrato__idempleado__pnombre'),
            e.get('idcontrato__idempleado__snombre'),
            e.get('idcontrato__idempleado__papellido'),
            e.get('idcontrato__idempleado__sapellido'),
        ]
        full_name = " ".join([
            n.strip() for n in nombres
            if n and n.strip().lower() != "no data"
        ])

        valor = calculate_withholding_tax(e.get('idcontrato'), idnomina)

        if valor > 0:
            empleados.append({
                'documento': doc,
                'nombre_completo': full_name,
                'salario': e.get('idcontrato__salario'),
                'idcontrato': e.get('idcontrato'),
                'valor': valor,
            })

    context = {
        'empleados': empleados,
        'nomina': nomina,
    }



    return render(request, './payroll/partials/withholding.html', context)




def calculate_withholding_tax(idcontrato, idnomina):

    #print('\n================ RETEFUENTE DEBUG ================')

    contrato = Contratos.objects.get(idcontrato=idcontrato)
    nomina = Crearnomina.objects.get(idnomina=idnomina)

    mes = nomina.mesacumular
    ano = nomina.anoacumular.ano

    uvt = Salariominimoanual.objects.get(ano=ano).uvt

    # 790 UVT anual → mensual
    limit_790 = (790 / 12) * uvt

    #print(f"\n📅 Periodo: {mes}/{ano}")
    #print(f"👤 Contrato: {idcontrato}")
    #print(f"💰 UVT: {uvt:,.2f}")
    #print(f"📊 Límite 790 UVT mensual: {limit_790:,.2f}")

    # -----------------------------
    # FUNCION AUXILIAR
    # -----------------------------
    def sum_nomina(campo):
        return filter_sum_nomina(mes, ano, idcontrato, campo)

    # -----------------------------
    # INGRESOS
    # -----------------------------
    ingresos_totales = sum_nomina('ingresotributario')

    #print(f"\n💵 Ingresos Totales: {ingresos_totales:,.2f}")

    tope_minimo = 129 * uvt
    #print(f"📊 Tope mínimo (129 UVT): {tope_minimo:,.2f}")

    if ingresos_totales <= tope_minimo:
        #print("❌ No aplica retefuente\n")
        return 0

    # -----------------------------
    # DEPURACIONES
    # -----------------------------
    ingresos_nr = sum_nomina('norenta')
    exentos = abs(sum_nomina('exentos'))
    pension = abs(sum_nomina('pension'))

    pension_limite = ingresos_totales * 0.3
    pension_original = pension
    pension = min(pension, pension_limite)

    #print("\n📉 DEPURACIÓN:")
    #print(f"   - Ingresos NO renta: {ingresos_nr:,.2f}")
    #print(f"   - Exentos: {exentos:,.2f}")
    #print(f"   - Pensión original: {pension_original:,.2f}")
    #print(f"   - Límite pensión (30%): {pension_limite:,.2f}")
    #print(f"   - Pensión aplicada: {pension:,.2f}")

    # -----------------------------
    # DEDUCCIONES
    # -----------------------------
    dependientes = 0
    if contrato.dependientes:
        dependientes = min(ingresos_totales * 0.1, 32 * uvt)

    medicina = min(contrato.valordeduciblemedicina or 0, 16 * uvt)
    vivienda = min(contrato.valordeduciblevivienda or 0, 100 * uvt)

    deducciones = dependientes + medicina + vivienda

    #print("\n📌 DEDUCCIONES:")
    #print(f"   - Dependientes: {dependientes:,.2f}")
    #print(f"   - Medicina: {medicina:,.2f}")
    #print(f"   - Vivienda: {vivienda:,.2f}")
    #print(f"   - Total deducciones: {deducciones:,.2f}")

    # -----------------------------
    # BASE INICIAL
    # -----------------------------
    ingreso_dep = (
        ingresos_totales
        - ingresos_nr
        - pension
        - exentos
        - deducciones
    )

    #print("\n🧮 DETALLE BASE:")
    #print(f"   Ingresos Totales: {ingresos_totales:,.2f}")
    #print(f" - Ingresos NO renta: {ingresos_nr:,.2f}")
    #print(f" - Pensión aplicada: {pension:,.2f}")
    #print(f" - Exentos: {exentos:,.2f}")
    #print(f" - Deducciones: {deducciones:,.2f}")
    #print(f" = Base depurada: {ingreso_dep:,.2f}")

    # -----------------------------
    # RENTA EXENTA 25%
    # -----------------------------
    renta_exenta = ingreso_dep * 0.25

    #print("\n📊 RENTA EXENTA:")
    #print(f"   - 25% calculado: {renta_exenta:,.2f}")
    #print(f"   - Límite 790 UVT: {limit_790:,.2f}")

    if renta_exenta > limit_790:
        #print("   ⚠️ Se aplica límite 790 UVT")
        renta_exenta = limit_790

    ingreso_dep_post25 = ingreso_dep - renta_exenta

    #print(f"   - Renta exenta aplicada: {renta_exenta:,.2f}")
    #print(f"   - Base después 25%: {ingreso_dep_post25:,.2f}")

    # -----------------------------
    # LIMITE 40%
    # -----------------------------
    limite_40 = ingresos_totales * 0.4
    ingreso_final = max(ingreso_dep_post25, limite_40)

    #print("\n⚠️ VALIDACIÓN 40%:")
    #print(f"   Base después 25%: {ingreso_dep_post25:,.2f}")
    #print(f"   Límite 40%: {limite_40:,.2f}")

    #if ingreso_dep_post25 < limite_40:
    #    print("   🔥 Se activa límite 40%")
    #else:
    #    print("   ✅ Se usa base real")

    #print(f"   👉 Base final usada: {ingreso_final:,.2f}")

    # -----------------------------
    # UVT
    # -----------------------------
    base_uvt = ingreso_final / uvt

    #print("\n🔢 BASE UVT:")
    #print(f"   Base en pesos: {ingreso_final:,.2f}")
    #print(f"   Base en UVT: {base_uvt:.2f}")

    # -----------------------------
    # TABLA DIAN
    # -----------------------------
    impuesto = 0
    rango = "No aplica"

    #print("\n🧾 CÁLCULO IMPUESTO:")

    if 95 < base_uvt <= 150:
        exceso = base_uvt - 95
        impuesto = exceso * uvt * 0.19
        rango = "95 - 150"
        #print(f"   ({exceso:.2f} × 0.19) × UVT")

    elif 150 < base_uvt <= 360:
        exceso = base_uvt - 150
        impuesto = (exceso * uvt * 0.28) + (10 * uvt)
        rango = "150 - 360"
        #print(f"   ({exceso:.2f} × 0.28 + 10) × UVT")

    elif 360 < base_uvt <= 640:
        exceso = base_uvt - 360
        impuesto = (exceso * uvt * 0.33) + (69 * uvt)
        rango = "360 - 640"

    elif 640 < base_uvt <= 945:
        exceso = base_uvt - 640
        impuesto = (exceso * uvt * 0.35) + (162 * uvt)
        rango = "640 - 945"

    elif 945 < base_uvt <= 2300:
        exceso = base_uvt - 945
        impuesto = (exceso * uvt * 0.37) + (268 * uvt)
        rango = "945 - 2300"

    elif base_uvt > 2300:
        exceso = base_uvt - 2300
        impuesto = (exceso * uvt * 0.39) + (770 * uvt)
        rango = "> 2300"

    #print(f"📊 Rango DIAN: {rango}")
    #print(f"💰 Impuesto antes redondeo: {impuesto:,.2f}")

    # -----------------------------
    # RESULTADO FINAL
    # -----------------------------
    impuesto_final = round(impuesto, -3)

    #print("\n🎯 DEBUG FINAL:")
    #print(f"   Impuesto sin redondeo: {impuesto:,.2f}")
    #print(f"   Impuesto redondeado: {round(impuesto, -3):,.0f}")

    #print(f"\n✅ RETEFUENTE FINAL: {impuesto_final:,.0f}")
    #print("================================================\n")

    return impuesto_final




def filter_sum_nomina(mes, ano, idcontrato,familia):
    total = 0
    #print(f" ----- familia: {familia} -----")
    data = Nomina.objects.filter(
        idnomina__mesacumular=mes,
        idnomina__anoacumular__ano=ano,
        idcontrato_id=int(idcontrato),
        idnomina__tiponomina__idtiponomina__in=[1, 2],
        idconcepto__indicador__nombre=familia,
    )

    #print('====================================================')
    #print(f" ----- familia: {familia} -----")
    for item in data:
        #print(f" valor {item.valor}  cantidad : {item.cantidad} concepto : {item.idconcepto.nombreconcepto}")
        total += abs(item.valor)
    
    #print('====================================================')
    return total