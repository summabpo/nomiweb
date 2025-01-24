from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.components.decorators import role_required
from apps.common.models import Crearnomina , Tipodenomina ,Subcostos,Costos,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
from apps.components.humani import format_value
from django import forms

class ConceptoForm(forms.Form):
    cantidad = forms.IntegerField()
    valor = forms.IntegerField()

@login_required
@role_required('accountant')
def pruebas(request,id,idnomina):
    # Optimizar consulta del contrato
    forms = []

    try:
        contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)
        empleado = contrato.idempleado
        nombre_completo = " ".join(filter(None, [empleado.papellido, empleado.sapellido, empleado.pnombre, empleado.snombre]))
                # Optimizar consultas con select_related
        conceptos = Nomina.objects.filter(
            idnomina__idnomina=idnomina,
            idcontrato__idcontrato=id
        ).select_related('idcontrato')

        # Verificar si hay conceptos encontrados
        if not conceptos.exists():
            return JsonResponse({"error": "No se encontraron conceptos para este empleado y nómina"}, status=404)

        forms = [ConceptoForm(), ConceptoForm(), ConceptoForm()]
        # Optimizar consulta del contrato
        contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)

        # Estructurar los datos para la respuesta
        conceptos_data = [
            {   
                "codigo": concepto.idregistronom ,
                "id": concepto.idconcepto.idconcepto,
                "amount": concepto.cantidad,
                "value": concepto.valor ,
            }
            
            # Crear un formulario para cada concept
            for concepto in conceptos
        ]

        
        # Construir el nombre completo
        empleado = contrato.idempleado
        nombre_completo = " ".join(filter(None, [empleado.papellido, empleado.sapellido, empleado.pnombre, empleado.snombre]))

        # Respuesta estructurada
        data = {
            
            "nombre": nombre_completo,
            "salario": f"${format_value(contrato.salario)}",
            "conceptos": conceptos_data,
        }
        return render(request, 'payroll/partials/payrollmodal.html', {'data': data,'forms': forms})

    except Exception as e:
        return render(request, 'payroll/partials/payrollmodal.html', {'data': data})