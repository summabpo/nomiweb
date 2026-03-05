from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Contratos , Contratosemp , Ciudades , Cargos , Entidadessegsocial ,Costos
from apps.components.decorators import custom_login_required ,custom_permission
from django.db.models import OuterRef, Exists, Subquery
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.companies.forms.ReactivationForm import ReactivationForm
from django.http import HttpResponse
from django.urls import reverse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment

@login_required
@role_required('company', 'accountant')
def reactivation(request):  
    
    # --- Función auxiliar de limpieza ---
    def clean_value(value):
        """
        Limpia valores tipo texto que indiquen falta de datos.
        Ejemplo: 'no data', 'sin dato', 'n/a', 'none', 'ninguno'
        """
        if isinstance(value, str):
            if value.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"]:
                return ""
        return value

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    # Contratos activos
    contratos_activos = Contratos.objects.filter(
        idempleado=OuterRef('pk'),
        estadocontrato=1,
        id_empresa_id=idempresa
    )

    # Cualquier contrato (histórico)
    contratos_historicos = Contratos.objects.filter(
        idempleado=OuterRef('pk'),
        id_empresa_id=idempresa
    )

    # Último contrato
    ultimo_contrato = contratos_historicos.order_by('-idcontrato')

    empleados = Contratosemp.objects.filter(
        id_empresa_id=idempresa
    ).annotate(
        tiene_contrato_activo=Exists(contratos_activos),
        tiene_contrato=Exists(contratos_historicos),  # 👈 NUEVO
        fechainiciocontrato=Subquery(ultimo_contrato.values('fechainiciocontrato')[:1]),
        fechafincontrato=Subquery(ultimo_contrato.values('fechafincontrato')[:1]),
        salario=Subquery(ultimo_contrato.values('salario')[:1]),
        cargo=Subquery(ultimo_contrato.values('cargo__nombrecargo')[:1]),
        tipocontrato=Subquery(ultimo_contrato.values('tipocontrato__tipocontrato')[:1]),
        centrocostos=Subquery(ultimo_contrato.values('idcosto__nomcosto')[:1]),
        idcontrato=Subquery(ultimo_contrato.values('idcontrato')[:1]),
    ).filter(
        tiene_contrato_activo=False,   # No activo
        tiene_contrato=True            # Pero sí tuvo contrato
    )

    # Nombre completo
    for e in empleados:
        e.nombre = clean_value(
            f"{e.pnombre or ''} {e.snombre or ''} {e.papellido or ''} {e.sapellido or ''}".strip()
        )
        e.cargo = clean_value(e.cargo)
        e.tipocontrato = clean_value(e.tipocontrato)
        e.centrocostos = clean_value(e.centrocostos)


    return render(request, './companies/reactivation.html', { 'empleados': empleados, 'user': request.user })



@login_required
@role_required('company', 'accountant')
def reactivation_modal(request,id):
    contrato = Contratos.objects.get(idcontrato = id)
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    idc = contrato.idcontrato
    data = {
        'name': contrato.idempleado.idempleado,
        'payrollType': contrato.tiponomina.idtiponomina if contrato.tiponomina else '',
        'position': contrato.cargo.idcargo if contrato.cargo else '',
        'workLocation': contrato.ciudadcontratacion.idciudad if contrato.ciudadcontratacion else '',
        'contractType': contrato.tipocontrato.idtipocontrato if contrato.tipocontrato else '',
        'contractModel': contrato.idmodelo.idmodelo if contrato.idmodelo else '',
        'salary': "{:,.0f}".format(contrato.salario).replace(',', '.') if contrato.salario else '',
        'salaryType': contrato.tiposalario.idtiposalario if contrato.tiposalario else '',
        'paymentMethod': contrato.formapago or '',
        'salaryMode': contrato.salariovariable or '',
        'bankAccount': contrato.bancocuenta.idbanco if contrato.bancocuenta else '',
        'accountType': contrato.tipocuentanomina or '',
        'payrollAccount': contrato.cuentanomina or '',
        'costCenter': contrato.idcosto.idcosto if contrato.idcosto else '',
        'subCostCenter': contrato.idsubcosto.idsubcosto if contrato.idsubcosto else '',
        'eps': contrato.codeps.identidad if contrato.codeps else '',
        'pensionFund': contrato.codafp.identidad if contrato.codafp else '',
        'CesanFund': contrato.codccf.identidad if contrato.codccf else '',
        'livingPlace': contrato.auxiliotransporte ,
        'arlWorkCenter': contrato.centrotrabajo.centrotrabajo if contrato.centrotrabajo else '',
        'workPlace': contrato.idsede.idsede if contrato.idsede else '',
        'contributor': contrato.tipocotizante.tipocotizante if contrato.tipocotizante else '',
        'subContributor': contrato.subtipocotizante.subtipocotizante if contrato.subtipocotizante else '',
    }


    # ✅ Limpieza de valores tipo "no data", "sin dato", "n/a", etc.
    data = {
        k: ("" if isinstance(v, str) and v.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"] else v)
        for k, v in data.items()
    }
    if request.method == 'POST':
        form = ReactivationForm(request.POST,idempresa=idempresa,empleado_actual = True , idcontrato = id)

        if form.is_valid():
            print('-------------')
            print(request.POST)
            print('-------------')
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-Message'] = 'La reactivación del empleado se realizó correctamente.' 
            response['X-Up-Location'] = reverse('companies:reactivation')           
            return response
        
        else: 
            for field, errors in form.errors.items():
                for error in errors:
                    response = HttpResponse()
                    response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
                    response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
                    response['X-Up-message'] = f"Error en el campo '{field}': {error}"    
                    response['X-Up-Location'] = reverse('companies:reactivation')           
                    return response
                
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = "Todo lo que podía fallar, falló."    
            response['X-Up-Location'] = reverse('companies:reactivation')           
            return response
    else:
        form = ReactivationForm(idempresa=idempresa , initial=data , empleado_actual = True , idcontrato = id)
    return render(request, './companies/partials/reactivation_modal.html',{'form':form , 'idc':idc})




def estilo_header(ws):
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")


def ajustar_columnas(ws):
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)

        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        adjusted_width = max_length + 2
        ws.column_dimensions[column_letter].width = adjusted_width

@login_required
@role_required('company', 'accountant')
def reactivation_doc(request):
    def clean_value(value):
        if isinstance(value, str):
            if value.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"]:
                return ""
        return value

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    contratos_activos = Contratos.objects.filter(
        idempleado=OuterRef('pk'),
        estadocontrato=1,
        id_empresa_id=idempresa
    )

    contratos_historicos = Contratos.objects.filter(
        idempleado=OuterRef('pk'),
        id_empresa_id=idempresa
    )

    ultimo_contrato = contratos_historicos.order_by('-idcontrato')

    empleados = Contratosemp.objects.filter(
        id_empresa_id=idempresa
    ).annotate(
        tiene_contrato_activo=Exists(contratos_activos),
        tiene_contrato=Exists(contratos_historicos),
        salario=Subquery(ultimo_contrato.values('salario')[:1]),
    ).filter(
        tiene_contrato_activo=False,
        tiene_contrato=True
    )

    for e in empleados:
        e.nombre = clean_value(
            f"{e.pnombre or ''} {e.snombre or ''} {e.papellido or ''} {e.sapellido or ''}".strip()
        )

    # ------------------------
    # CREAR EXCEL
    # ------------------------

    wb = Workbook()

    # HOJA 1 (plantilla)
    ws1 = wb.active
    ws1.title = "Plantilla"

    headers = [
        
        "Documento",
        "Tipo de documento",
        "Nombre",
        "Fecha de ingreso",
        "Fecha de retiro",
        "Salario",
        'Tipo Salario - ID',
        "Modalidad Salario - ID",
        "Cargo - ID",
        "Tipo de Contrato - ID",
        "Tipo de Nómina - ID",
        "Modelo de Contrato - ID",
        "Lugar de trabajo - ID",
        "Forma de pago - ID",
        "Banco de la Cuenta - ID",
        "Tipo de Cuenta - ID",
        "Cuenta de Nómina",
        "Eps - ID",
        "Pension - ID",
        "Fondo Cesantias - ID",
        "Sede de Trabajo - ID",
        "Tipo de Cotizante - ID",
        "Subtipo de Cotizante - ID",

    ]

    ws1.append(headers)

    # HOJA 2 (listado empleados)
    ws2 = wb.create_sheet(title="Empleados")

    ws2.append(["Documento", "Nombre","Salario anterior"])

    for e in empleados:
        ws2.append([
            e.docidentidad,
            e.nombre,
            e.salario
        ])

    # HOJA 3 (Cargos)
    cargos = Cargos.objects.filter(id_empresa__idempresa=usuario['idempresa']).exclude(idcargo=241).order_by('idcargo')

    ws3 = wb.create_sheet(title="Cargos")


    ws3.append(["ID", "Nombre"])

    for c in cargos:
        ws3.append([
            c.idcargo,
            c.nombrecargo,
        ])

    # HOJA 4 (Entidades)
   
    entidades = Entidadessegsocial.objects.all().exclude(
        codigo__in=['000', '9999', '9988', '9998']
    ).exclude(
        nit=''
    ).exclude(
        nit__isnull=True
    ).order_by('entidad')

    ws4 = wb.create_sheet(title="Entidades")
    ws4.append(["ID","Codigo", "Nombre","Tipo"])

    for e in entidades:
        ws4.append([
            e.identidad,
            e.codigo,
            e.entidad,
            e.tipoentidad
        ])

    # HOJA 5 (Cargos)
    costos = Costos.objects.filter(id_empresa__idempresa=usuario['idempresa'] ).exclude(grupocontable= 0 ,suficosto = 0 ).order_by('idcosto')
    ws5 = wb.create_sheet(title="Centros de Costos")

    ws5.append(["ID", "Nombre","Grupo"])

    for c in costos:
        ws5.append([
            c.idcosto,
            c.nomcosto,
            c.grupocontable
        ])

    ## ajuste 
    ajustar_columnas(ws1)
    ajustar_columnas(ws2)
    ajustar_columnas(ws3)
    ajustar_columnas(ws4)
    ajustar_columnas(ws5)

    ## estilos 
    estilo_header(ws1)
    estilo_header(ws2)
    estilo_header(ws3)
    estilo_header(ws4)
    estilo_header(ws5)

    # ------------------------
    # RESPUESTA HTTP
    # ------------------------



    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response['Content-Disposition'] = 'attachment; filename="reactivacion_empleados.xlsx"'

    wb.save(response)

    return response




@login_required
@role_required('company', 'accountant')
def reactivation_data(request):


    return render(request, './companies/partials/reactivation_data.html')



