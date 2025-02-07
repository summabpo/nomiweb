from django.shortcuts import render,redirect
from apps.administrator.forms.companiesForm import CompaniesForm
from apps.common.models import  Empresa, Ciudades, Paises, Entidadessegsocial, Bancos
from django.http import JsonResponse


def createcompanies_admin(request):
    form = CompaniesForm()
    empresas = Empresa.objects.all().order_by('-idempresa')
    return render(request, './admin/companies.html',{
        'form': form ,
        'empresas':empresas
        
        })
    
    
def addcompanies_admin(request):
    if request.method == 'POST':
        form = CompaniesForm(request.POST, request.FILES)
        if form.is_valid():
            vstccf = form.cleaned_data.get('vstccf', '')
            vstsenaicbf = form.cleaned_data.get('vstsenaicbf', '')
            ige100 = form.cleaned_data.get('ige100', '')
            ajustarnovedad = form.cleaned_data.get('ajustarnovedad', '')
            
            print(request.POST)
            
            empresa = Empresa(
                nit=form.cleaned_data['nit'],
                nombreempresa=form.cleaned_data['nombreempresa'],
                dv=form.cleaned_data['dv'],
                tipodoc=form.cleaned_data['tipodoc'],
                replegal=form.cleaned_data['replegal'],
                direccionempresa=form.cleaned_data['direccionempresa'],
                telefono=form.cleaned_data['telefono'],
                email=form.cleaned_data['email'],
                codciudad=Ciudades.objects.get(idciudad=form.cleaned_data['codciudad']),
                pais=Paises.objects.get(idpais=form.cleaned_data['pais']),
                arl=Entidadessegsocial.objects.get(identidad=form.cleaned_data['arl']),
                contactonomina=form.cleaned_data['contactonomina'],
                emailnomina=form.cleaned_data['emailnomina'],
                contactorrhh=form.cleaned_data['contactorrhh'],
                emailrrhh=form.cleaned_data['emailrrhh'],
                contactocontab=form.cleaned_data['contactocontab'],
                emailcontab=form.cleaned_data['emailcontab'],
                cargocertificaciones=form.cleaned_data['cargocertificaciones'],
                firmacertificaciones=form.cleaned_data['firmacertificaciones'],
                website=form.cleaned_data['website'],
                logo=form.cleaned_data['logo'],
                metodoextras=form.cleaned_data['metodoextras'],
                realizarparafiscales=form.cleaned_data['realizarparafiscales'],
                vstccf=str(vstccf)[:2] if vstccf else '',
                vstsenaicbf=str(vstsenaicbf)[:2] if vstsenaicbf else '',
                ige100=str(ige100)[:2] if ige100 else '',
                slntarifapension=form.cleaned_data['slntarifapension'],
                banco=Bancos.objects.get(idbanco=form.cleaned_data['banco']) if form.cleaned_data['banco'] else None,
                numcuenta=form.cleaned_data['numcuenta'],
                tipocuenta=form.cleaned_data['tipocuenta'],
                codigosuc=form.cleaned_data['codigosuc'],
                nombresuc=form.cleaned_data['nombresuc'],
                claseaportante=form.cleaned_data['claseaportante'],
                tipoaportante=form.cleaned_data['tipoaportante'],
                ajustarnovedad=str(ajustarnovedad)[:2] if ajustarnovedad else '',	
            )
            empresa.save()
            return JsonResponse({'status': 'success', 'message': 'Empresa creada exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = CompaniesForm()
    return render(request, './admin/partials/companiesModal.html',{
        'form': form
        })