
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina ,Costos, Conceptosfijos , Salariominimoanual,Conceptosdenomina , Empresa , Anos , Nomina , Contratos


@login_required
@role_required('accountant')
def automatic_systems(request, type_payroll=0):
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

    return render(request, 'payroll/partials/payroll_automatic_systems.html', {'titulo': titulo, 'centros': centros, 'type_payroll': type_payroll})



