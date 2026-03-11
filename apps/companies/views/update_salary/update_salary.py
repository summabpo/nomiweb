from django.shortcuts import render
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.companies.forms.updatesalaryForm import updatesalaryForm
from django.http import JsonResponse , HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.dimensions import DimensionHolder
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.http import JsonResponse
from apps.common.models import NovSalarios, Contratos ,HistorialSalario
from decimal import Decimal

from django.db import transaction

error_messages = {
    '1': "Id contrato inválido o faltante",
    '3': "Contrato no encontrado",
    '4': "El contrato no está activo",
    '6': "El contrato no pertenece a la empresa actual",
    '7': "Fila vacía o incompleta",
    '8': "El nuevo salario debe ser mayor que cero",
    '13': "El contrato está cerrado o inactivo",
    '14': "El nuevo salario no puede ser negativo",
    '19': "El nuevo salario es igual al salario actual",
    '20': "Ya existe un ajuste salarial con la misma fecha",
    '21': "Ajuste salarial duplicado en el archivo",
    'general': "Error general: Error procesando el archivo"
}


@login_required
@role_required('company','accountant')
def update_salary(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    # Obtener fecha actual
    from datetime import date
    fecha_hoy = date.today()
    
    novsalarios = (
        NovSalarios.objects
        .select_related(
            'idcontrato',
            'idcontrato__idempleado'
        )
        .only(
            'idcambiosalario',
            'salarioactual',
            'nuevosalario',
            'fechanuevosalario',
            'idcontrato__idcontrato',
            'idcontrato__idempleado__docidentidad',
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__papellido',
        )
        .filter(
            idcontrato__id_empresa=idempresa
        )
        .order_by('idcambiosalario')
    )
    
    for i in novsalarios:
        contrato = Contratos.objects.get(idcontrato=i.idcontrato.idcontrato)
        
        if i.fechanuevosalario <= fecha_hoy and contrato.salario != i.nuevosalario:
            contrato.salario = i.nuevosalario
            contrato.save()
    
    return render(request, './companies/update_salary.html', {'novsalarios': novsalarios})




def actualizacion():


    return('ok')


@login_required
@role_required('company','accountant')
def update_salary_add(request):
    existe_historial = False
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    form = updatesalaryForm(idempresa = idempresa)
    if request.method == 'POST':
        
        form = updatesalaryForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            
            print(request.POST)

            contrato_id = form.cleaned_data['contract']
            nuevosalario = form.cleaned_data['Salario_nuevo']
            fecha_nuevo = form.cleaned_data['fecha_nuevo']
            salario_actual = form.cleaned_data['Salario_Actual']
            salario_nuevo = form.cleaned_data['Salario_nuevo']
            fecha_nuevo = form.cleaned_data['fecha_nuevo']
            tiposalario = form.cleaned_data['contractType']

            contrato = Contratos.objects.get(idcontrato = form.cleaned_data['contract'] )
            

            if nuevosalario > contrato.salario : 

                dataaux =  NovSalarios.objects.filter(nuevosalario = contrato.salario , idcontrato_id = form.cleaned_data['contract'] ).first()
                
                # validar existencia
                if dataaux : 
                    existe_historial = HistorialSalario.objects.filter(
                        contrato_id=contrato_id,
                        salario=salario_nuevo,
                        fecha_inicio=dataaux.fechanuevosalario,
                        fecha_fin=fecha_nuevo
                    ).exists()
                


                existe_novsalario = NovSalarios.objects.filter(
                    idcontrato_id=contrato_id,
                    salarioactual=salario_actual,
                    nuevosalario=salario_nuevo,
                    fechanuevosalario=fecha_nuevo,
                    tiposalario=tiposalario,
                ).exists()

                if not existe_novsalario:

                    with transaction.atomic():

                        novsalario = NovSalarios.objects.create(
                            idcontrato_id=contrato_id,
                            salarioactual=salario_actual,
                            nuevosalario=salario_nuevo,
                            fechanuevosalario=fecha_nuevo,
                            tiposalario=tiposalario,
                        )

                        if  not existe_historial  : 
                            historial = HistorialSalario.objects.create(
                                contrato_id=contrato_id,
                                salario=contrato.salario,
                                fecha_inicio=novsalario.fechanuevosalario,
                                es_actual=True,
                            )
                        else:
                            historial = HistorialSalario.objects.create(
                                contrato_id=contrato_id,
                                salario=contrato.salario,
                                fecha_inicio=dataaux.fechanuevosalario,
                                fecha_fin=fecha_nuevo,
                                es_actual=True,
                            )
                            

                        response = HttpResponse()
                        response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
                        response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
                        response['X-Up-message'] = 'Nuevo salario guardada exitosamente'    
                        response['X-Up-Location'] = reverse('companies:update_salary')           
                        return response
                else:
                    
                    response = HttpResponse()
                    response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
                    response['X-Up-icon'] = 'warning'  # URL para recargar la página principal   
                    response['X-Up-message'] = 'ups , parece que esa data ya la tenemos'    
                    response['X-Up-Location'] = reverse('companies:update_salary')           
                    return response
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")   
    return render (request, './companies/partials/update_salary_add.html',{'form':form})


@login_required
@role_required('company', 'accountant')
def update_salary_add_masive(request):

    usuario = request.session.get('usuario', {})
    idempresa = int(usuario['idempresa'])

    errores = []
    pending_rows = []   # datos válidos en memoria
    has_errors = False  # flag global

    if request.method == 'POST':
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"errors": ["Archivo no proporcionado"]}, status=400)

        # Leer archivo
        try:

            file.seek(0)

            if file.name.endswith('.csv'):
                df = pd.read_csv(file)

            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file, engine='openpyxl')

            else:

                return JsonResponse(
                    {"errors": ["Formato no soportado"]},
                    status=400
                )

        except Exception as e:
            print("ERROR REAL:", e)
            return JsonResponse(
                {"errors": [str(e)]},
                status=400
            )
        
        cargados = set()  # detectar duplicados en archivo

        # =========================
        # 1️VALIDAR TODO
        # =========================
        for index, row in df.iterrows():
            row_errors = []  # se reinicia por fila
            try:
                id_contrato = int(row.get('ID Contrato'))
                nuevo_salario = float(row.get('Nuevo Salario'))
                fecha = row.get('Fecha')
            except Exception:
                row_errors.append('7')

            contrato = None
            if not row_errors:
                contrato = Contratos.objects.filter(
                    idcontrato=id_contrato,
                    id_empresa_id=idempresa
                ).first()

                if not contrato:
                    row_errors.append('3')
                elif contrato.estadocontrato != 1:
                    row_errors.append('4')

                if nuevo_salario <= 0:
                    row_errors.append('8')

                if contrato and nuevo_salario == float(contrato.salario):
                    row_errors.append('19')

                if contrato and NovSalarios.objects.filter(
                    idcontrato=contrato,
                    fechanuevosalario=fecha
                ).exists():
                    row_errors.append('20')

                key = (id_contrato, fecha)
                if key in cargados:
                    row_errors.append('21')
                else:
                    cargados.add(key)

            # Si hay errores → marcar flag global
            if row_errors:
                has_errors = True
                for err in row_errors:
                    print('------------------')
                    print(error_messages[err])

                    errores.append({
                        "fila": index + 1,
                        "id_contrato": id_contrato,
                        "error": error_messages[err]
                    })
            else:
                pending_rows.append({
                    "contrato": contrato,
                    "nuevo_salario": nuevo_salario,
                    "fecha": fecha
                })

        # Si hubo cualquier error → NO guardar
        if has_errors:
                        
            return render(
                request,
                './companies/partials/update_salary_add_masive_error.html',
                {"errores": errores,
                "message": "No se guardó ningún registro"}
            )

        # =========================
        # 2GUARDAR (SIN ERRORES)
        # =========================
        # =========================
        # GUARDAR
        # =========================
        try:
            with transaction.atomic():
                for r in pending_rows:
                    NovSalarios.objects.create(
                        idcontrato=r["contrato"],
                        salarioactual=r["contrato"].salario,
                        nuevosalario=r["nuevo_salario"],
                        fechanuevosalario=r["fecha"],
                        tiposalario=r["contrato"].tiposalario.idtiposalario
                    )

        except Exception as e:

            return render(
                request,
                './companies/partials/update_salary_add_masive_error.html',
                {
                    "errores": [{"error": str(e)}],
                    "message": "Ocurrió un error al guardar."
                }
            )

        # =========================
        # SUCCESS
        # =========================
        return render(
            request,
            './companies/partials/update_salary_add_masive_success.html',
            {
                "total": len(pending_rows),
                "message": f"Se guardaron {len(pending_rows)} registros correctamente."
            }
        )


    return render(
        request,
        './companies/partials/update_salary_add_masive.html',
        {}
    )


@login_required
@role_required('company', 'accountant')
def update_salary_add_masive_doc(request):
    # Crear el libro de Excel
    wb = Workbook()

    # Hoja principal
    ws = wb.active
    ws.title = "Datos"

    # Columnas fijas
    columns = ["ID Contrato", "Documento", "Nombre", "Nuevo Salario",'Fecha']

    # Escribir encabezados
    for col_num, col_name in enumerate(columns, start=1):
        ws.cell(row=1, column=col_num, value=col_name)
        ws.cell(row=1, column=col_num).alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # Fijar fila de encabezado
    ws.freeze_panes = "A2"

    # Ajustar ancho de columnas
    dim_holder = DimensionHolder(worksheet=ws)
    for col in range(1, len(columns) + 1):
        column_letter = get_column_letter(col)
        dim_holder[column_letter] = ws.column_dimensions[column_letter]
        dim_holder[column_letter].width = 20
    ws.column_dimensions = dim_holder

    # Preparar respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=ajuste_salarial_masivo.xlsx'

    wb.save(response)
    return response




@login_required
@role_required('company','accountant')
def get_contract_salary(request):
    """
    Endpoint para obtener el salario de un contrato específico
    """
    if request.method == 'GET':
        
        contract_id = request.GET.get('contract_id')
        if not contract_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de contrato requerido'
            })
        
        try:
            contract = Contratos.objects.get(
                idcontrato=contract_id,
                estadocontrato=1  # Solo contratos activos
            )
            return JsonResponse({
                'success': True,
                'salary': contract.salario or 0
            })
        except Contratos.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Contrato no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })