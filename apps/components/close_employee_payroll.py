from apps.common.models import Nomina , NominaComprobantes ,Crearnomina ,HistoricoNomina, Contratos ,Empresa
from django.db.models import Sum


# def close_employee_payroll(employee, idnomina):

#     try:
#         comp = NominaComprobantes.objects.get(idnomina_id=idnomina , idcontrato=employee )
#     except NominaComprobantes.DoesNotExist:
#         comp = NominaComprobantes.objects.create(
#             idcontrato=employee,
#             salario=employee.salario,
#             cargo=employee.cargo.nombrecargo,
#             idcosto_id=employee.idcosto.idcosto,
#             pension=employee.codafp.codigo,
#             salud=employee.codeps.codigo,
#             idnomina_id=idnomina,
#             envio_email=2
#         )

#     return comp

def close_employee_payroll(employee, idnomina):

    new_values = {
        "salario": employee.salario,
        "cargo": employee.cargo.nombrecargo,
        "idcosto_id": employee.idcosto.idcosto,
        "pension": employee.codafp.codigo,
        "salud": employee.codeps.codigo,
        "envio_email": 2,
    }

    comp = NominaComprobantes.objects.filter(
        idnomina_id=idnomina,
        idcontrato=employee
    ).first()


    if not comp:
        comp = NominaComprobantes.objects.create(
            idcontrato=employee,
            idnomina_id=idnomina,
            **new_values
        )
        return comp

    fields_to_update = []
    for field, value in new_values.items():
        if getattr(comp, field) != value:
            setattr(comp, field, value)
            fields_to_update.append(field)

    if fields_to_update:
        comp.save(update_fields=fields_to_update)
    return comp



def guardar_historico_nomina(comp): 

    ano_obj = comp.idnomina.anoacumular
    fecha_inicio = comp.idnomina.fechainicial
    fecha_fin = comp.idnomina.fechafinal

    historico, created = HistoricoNomina.objects.get_or_create(

        contrato=comp.idcontrato,
        ano=ano_obj,
        defaults={
            "historial": {},
            "total_anual": 0
        }
    )

    historial = historico.historial or {}
    key = f"{fecha_inicio.isoformat()}_{fecha_fin.isoformat()}_{comp.idnomina.idnomina}"

    nuevo_registro = {

            "idnomina": comp.idnomina_id,
            "nombre_nomina": comp.idnomina.nombrenomina,
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_final": fecha_fin.isoformat(),
            "salario": comp.idcontrato.salario,
            "cargo_id": comp.idcontrato.cargo.idcargo,
            "pension_id": comp.idcontrato.codafp.identidad,
            "salud_id": comp.idcontrato.codeps.identidad,
            "costo_id": comp.idcontrato.idcosto.idcosto,
        }
    
    registro_anterior = historial.get(key)

    if registro_anterior != nuevo_registro:
        historial[key] = nuevo_registro

        total = sum(
            item.get("salario", 0)
            for item in historial.values()
        )
        
        historico.historial = historial
        historico.total_anual = total

        historico.save(
                update_fields=[
                    "historial",
                    "total_anual",
                    "fecha_actualizacion"
                ]
            )

    return historico