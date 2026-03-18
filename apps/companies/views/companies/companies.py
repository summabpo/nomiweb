
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models import  Empresa, Ciudades, Paises, Entidadessegsocial, Bancos , Conceptosdenomina ,Familia
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.chargesForm import ChargesForm
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.companies.forms.CompanyForm import CompanyForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from apps.components.history import register_history



@login_required
@role_required('company','accountant')
def company(request): 
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')
    if not idempresa:
        return redirect('login:login')
    data = get_object_or_404(Empresa, idempresa=int(idempresa))
    return render(request, './companies/company.html', {'data': data})




@login_required
@role_required('company','accountant')
def company_edit(request,type = 1 ): 

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    empresa = Empresa.objects.get( idempresa = idempresa ) 

    data = {

            ## Información General
            'nit':empresa.nit ,
            'nombreempresa':empresa.nombreempresa ,
            'dv':empresa.dv ,
            'tipodoc':empresa.tipodoc ,
            'arl':empresa.arl.identidad if empresa.arl else None ,
            'replegal':empresa.replegal ,


            ## Información General - 2 
            'tipo_identificacion_rep_legal':empresa.tipo_identificacion_rep_legal ,
            'naturaleza_juridica':empresa.naturaleza_juridica ,
            'numero_identificacion_rep_legal':empresa.numero_identificacion_rep_legal ,
            'papellido_rep_legal':empresa.papellido_rep_legal ,
            'sapellido_rep_legal':empresa.sapellido_rep_legal ,
            'pnombre_rep_legal':empresa.pnombre_rep_legal ,
            'snombre_rep_legal':empresa.snombre_rep_legal ,


            ## Información Bancaria
            'bankAccount':empresa.banco.idbanco  if empresa.banco else None,
            'accountType':empresa.tipocuenta ,
            'payrollAccount':empresa.numcuenta ,

            ## Ubicación y Contacto 
            'direccionempresa':empresa.direccionempresa ,
            'city':empresa.idciudad.idciudad if empresa.idciudad else None,
            'country':empresa.pais.idpais if empresa.pais else None,
            'telefono':empresa.telefono ,
            'email':empresa.email ,
            'website':empresa.website ,

            ## Contactos por Área 
            'contactonomina':empresa.contactonomina ,
            'contactocontab':empresa.contactocontab ,
            'contactorrhh':empresa.contactorrhh ,
            'emailnomina':empresa.emailnomina ,
            'emailcontab':empresa.emailcontab ,
            'emailrrhh':empresa.emailrrhh ,

            ## Configuración Aportes y Parafiscales
            'claseaportante':empresa.claseaportante ,
            'tipoaportante':empresa.tipoaportante ,
            'tipo_presentacion_planilla':empresa.tipo_presentacion_planilla ,
            'codigo_sucursal':empresa.codigo_sucursal ,
            'nombre_sucursal':empresa.nombre_sucursal ,
            'vstccf':  True if  empresa.vstccf == 'SI' else False,
            'vstsenaicbf':True if  empresa.vstsenaicbf == 'SI' else False,
            'ige100':True if  empresa.ige100 == 'SI' else False,
            'slntarifapension':True if  empresa.slntarifapension == 'SI' else False,
            'ajustarnovedad':True if  empresa.ajustarnovedad == 'SI' else False,
            'metodoextras':True if  empresa.metodoextras == 'SI' else False,
            'realizarparafiscales':True if  empresa.realizarparafiscales == 'SI' else False,
            'empresa_exonerada': empresa.empresa_exonerada  ,

        }
        
    form = CompanyForm(initial = data ,edit = type ) 

    if request.method == 'POST':
        form = CompanyForm(request.POST, edit = type)
        if form.is_valid():
            cleaned = form.cleaned_data


            # =========================
            # BLOQUE 1 → Información General - 2
            # =========================
            if str(type) == '1':
                changes = {}

                # Campos de Información General - 2
                fields = [
                    'tipo_identificacion_rep_legal',
                    'naturaleza_juridica',
                    'numero_identificacion_rep_legal',
                    'papellido_rep_legal',
                    'sapellido_rep_legal',
                    'pnombre_rep_legal',
                    'snombre_rep_legal'
                ]

                for field in fields:
                    old_value = getattr(empresa, field)
                    new_value = cleaned.get(field)
                    if old_value != new_value:
                        changes[field] = (old_value, new_value)
                        setattr(empresa, field, new_value)

                # Guardamos solo los campos que cambiamos
                empresa.save(update_fields=fields)

                register_history(
                    instance=empresa,
                    user=request.user,
                    changed_fields=changes
                )



            # =========================
            # BLOQUE 2 → Información Bancaria
            # =========================
            if type == '2':
                changes = {}

                # Banco
                old_banco = empresa.banco_id
                new_banco = cleaned.get('bankAccount') or 0
                if old_banco != new_banco:
                    changes['banco'] = (old_banco, new_banco)
                    empresa.banco_id = new_banco

                # Tipo cuenta
                old_tipo = empresa.tipocuenta
                new_tipo = cleaned.get('accountType') or ''
                if old_tipo != new_tipo:
                    changes['tipocuenta'] = (old_tipo, new_tipo)
                    empresa.tipocuenta = new_tipo

                # Número cuenta
                old_num = empresa.numcuenta
                new_num = cleaned.get('payrollAccount') or ''
                if old_num != new_num:
                    changes['numcuenta'] = (old_num, new_num)
                    empresa.numcuenta = new_num

                empresa.save(update_fields=list(changes.keys()))
                register_history(instance=empresa, user=request.user, changed_fields=changes)

            # =========================
            # BLOQUE 3 → Ubicación
            # =========================
            elif str(type) == '3':
                changes = {}
                fields = ['direccionempresa', 'telefono', 'email', 'website']

                for field in fields:
                    old = getattr(empresa, field)
                    new = cleaned.get(field) or ''
                    if old != new:
                        changes[field] = (old, new)
                        setattr(empresa, field, new)

                # Ciudad
                old = empresa.idciudad_id
                new = cleaned.get('city') or 0
                if old != new:
                    changes['idciudad'] = (old, new)
                    empresa.idciudad_id = new

                # País
                old = empresa.pais_id
                new = cleaned.get('country') or 0
                if old != new:
                    changes['pais'] = (old, new)
                    empresa.pais_id = new

                empresa.save(update_fields=list(changes.keys()))
                register_history(empresa, request.user, changes)


            # =========================
            # BLOQUE 4 → Contactos
            # =========================
            elif str(type) == '4':
                changes = {}
                fields = [
                    'contactonomina', 'emailnomina',
                    'contactorrhh', 'emailrrhh',
                    'contactocontab', 'emailcontab'
                ]

                for field in fields:
                    old = getattr(empresa, field)
                    new = cleaned.get(field) or ''
                    if old != new:
                        changes[field] = (old, new)
                        setattr(empresa, field, new)

                empresa.save(update_fields=list(changes.keys()))
                register_history(empresa, request.user, changes)



            # =========================
            # BLOQUE 5 → Parafiscales
            # =========================
            if str(type) == '5':
                changes = {}

                boolean_fields = [
                    'metodoextras', 'realizarparafiscales',
                    'vstccf', 'vstsenaicbf',
                    'ige100', 'slntarifapension',
                    'ajustarnovedad',
                ]

                for field in boolean_fields:
                    old = getattr(empresa, field)
                    new = "SI" if cleaned.get(field) else "NO"
                    if old != new:
                        changes[field] = (old, new)
                        setattr(empresa, field, new)

                # Campos obligatorios, reemplazar None por valores por defecto
                required_fields_defaults = {
                    'claseaportante': cleaned.get('claseaportante') or '',
                    'tipoaportante': cleaned.get('tipoaportante') or '',
                    'codigo_sucursal': cleaned.get('codigo_sucursal') or '',
                    'nombre_sucursal': cleaned.get('nombre_sucursal') or '',
                    'tipo_presentacion_planilla': cleaned.get('tipo_presentacion_planilla') or ''
                }

                for field, value in required_fields_defaults.items():
                    old = getattr(empresa, field)
                    if old != value:
                        changes[field] = (old, value)
                        setattr(empresa, field, value)

                empresa.save(update_fields=list(changes.keys()))
                register_history(empresa, request.user, changes)

                
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'La Actualizacion fue registrada correctamente'    
            response['X-Up-Location'] = reverse('companies:company')           
            return response
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")

    return render(request, './companies/partials/company_edit.html',{'form':form})