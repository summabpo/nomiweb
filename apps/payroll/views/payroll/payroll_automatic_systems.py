
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Contratos ,Costos, Crearnomina , Salariominimoanual,Conceptosdenomina , Empresa , Vacaciones , Nomina , Contratos
from django.contrib import messages

@login_required
@role_required('accountant')
def automatic_systems(request, type_payroll=0,idnomina=0):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    titles = {
        0: 'Nómina Básica',
        1: 'Incapacidades',
        2: 'Aportes',
        3: 'Transporte',
        4: 'Reinicio de Nómina'
    }

    titulo = titles.get(type_payroll, 'Sistemas Automáticos')
    centros = Costos.objects.filter(id_empresa_id=idempresa)
    if request.method == 'POST':
        need_comment = request.POST.get('need_comment', False)  # Devuelve 'on' si está marcado, None si no
        no_cost_center = request.POST.get('no-cost-center', False)
        costo = request.POST.get('costos', False)
        # Convertirlo a True/False
        need_comment = need_comment == 'on'
        no_cost_center = no_cost_center == 'on'

        if need_comment:
            
            if procesar_nomina(idnomina, costo, idempresa):
                messages.success(request, "Nómina procesada correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
        else:
            if procesar_nomina(idnomina, 0,idempresa) :
                messages.success(request, "Nómina procesada correctamente")
                return redirect('payroll:payrollview', id=idnomina)
            else :
                messages.error(request, "Error al procesar la nómina")
                return redirect('payroll:payrollview', id=idnomina)
    
    return render(request, 'payroll/partials/payroll_automatic_systems.html', {'titulo': titulo, 'centros': centros, 'type_payroll': type_payroll , 'idnomina':idnomina})


# Lógica de consulta en Django ORM
def procesar_nomina(idn, parte_nomina,idempresa):
    if not parte_nomina:
        parte_nomina = 0

    contratos = Contratos.objects.filter(estadoliquidacion=3, id_empresa =  idempresa)
    if parte_nomina != 0:
        contratos = contratos.filter(idcosto=parte_nomina)

    try:
        nomina = Crearnomina.objects.get(idnomina=idn)
    except Crearnomina.DoesNotExist:
        return "Error de creación de nómina"

    fechainicial = nomina.fechainicial
    fechafinal = nomina.fechafinal
    mesacumular = nomina.mesacumular
    anoacumular = nomina.anoacumular.ano

    try:
        salario_min = Salariominimoanual.objects.get(ano=anoacumular)
        salmin = salario_min.salariominimo
        auxtra = salario_min.auxtransporte
    except Salariominimoanual.DoesNotExist:
        return "Error: Año no encontrado en salario mínimo anual"

    for contrato in contratos:
        diasnomina = nomina.diasnomina

        if contrato.fechainiciocontrato > fechainicial:
            diasnomina = (fechafinal - contrato.fechainiciocontrato).days + 1

        if contrato.fechafincontrato and fechainicial <= contrato.fechafincontrato <= fechafinal:
            diasnomina -= (fechafinal - contrato.fechafincontrato).days

        vacaciones = Vacaciones.objects.filter(idcontrato=contrato)
        for vac in vacaciones:
            if vac.fechainicialvac <= fechafinal and vac.ultimodiavac >= fechainicial:
                inicio = max(vac.fechainicialvac, fechainicial)
                fin = min(vac.ultimodiavac, fechafinal)
                dias_vacaciones = (fin - inicio).days + 1
                diasnomina -= dias_vacaciones
        concepto = Conceptosdenomina.objects.get(codigo=1, id_empresa_id = idempresa)
        if diasnomina > 0:
            valorsalario = (contrato.salario / 30) * diasnomina
            
            
            Nomina.objects.create(
                idconcepto = concepto ,#*
                cantidad=diasnomina ,#*
                valor=valorsalario , #*
                idcontrato_id=contrato.idcontrato ,
                idnomina_id = idn ,
            )
    return True





