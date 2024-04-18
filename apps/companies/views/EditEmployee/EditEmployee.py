from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp




def EditEmployeeVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    
    tipo_documento = Tipodocumento.objects.using("lectaen").get(codigo=empleado.tipodocident) 
    
    ciudadex = Ciudades.objects.using("lectaen").get(idciudad=empleado.ciudadexpedicion) 
    ciudadna = Ciudades.objects.using("lectaen").get(idciudad=empleado.ciudadnacimiento) 
    
    
    
    DatoCruz = {
        'tipodocident': tipo_documento.documento,
        'ciudadexpedicion':ciudadex.ciudad + ' - ' + ciudadex.departamento,
        'ciudadnaci': ciudadna.ciudad + ' - ' + ciudadna.departamento,
        
    }
    
    #empleado_dict = list(empleado)
    return render(request, './companies/EditEmployeevisual.html',{'empleado':empleado , 'datocruz':DatoCruz})




def EditEmployeeSearch(request):
    empleados = Contratosemp.objects.using("lectaen").all()
    
    if request.method == 'POST':
        selected_option = request.POST['selected_option']
        #return redirect('main:costos', proyecto.codigo )
        return redirect('companies:editemployeevisual',selected_option)
    
    return render(request, './companies/EditEmployeesearch.html',{'empleados':empleados})
