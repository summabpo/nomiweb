from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Contratos , Contratosemp , Ciudades
from apps.components.decorators import custom_login_required ,custom_permission
from django.db.models import OuterRef, Exists, Subquery
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.companies.forms.ReactivationForm import ReactivationForm
from django.http import HttpResponse
from django.urls import reverse

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