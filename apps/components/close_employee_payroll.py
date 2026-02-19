from apps.common.models import Nomina , NominaComprobantes ,Crearnomina , Contratos ,Empresa



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