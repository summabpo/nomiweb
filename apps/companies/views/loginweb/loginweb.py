from django.shortcuts import render, redirect
from apps.companies.models import Contratos ,Contratosemp
from apps.components.mail import send_template_email
from django.contrib import messages


def loginweb(request):
    
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids')
        if selected_ids:
            for selected in selected_ids:
                usertempo = Contratosemp.objects.get(idempleado = selected )


                email_type = 'loginweb' 
                name = 'nada'  
                context = {
                            'nombre_usuario': usertempo.pnombre,
                            'usuario': usertempo.email,
                            'contrasena': 'contrasena',
                            
                            }  
                
                subject = 'Asunto del correo'  
                recipient_list = ['mikepruebas@yopmail.com']
                
                if send_template_email(email_type, context, subject, recipient_list):
                    pass
                else:
                    messages.error(request, 'Todo lo que podria salir mal , salio mal ')
                
            messages.success(request, 'Los usuarios han sido enviados correctamente.')
            return redirect('companies:loginweb')  
    
    
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'cargo' , 'idempleado__idempleado' ,
                'tipocontrato__tipocontrato')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"

        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'cargo': contrato['cargo'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'idempleado': contrato['idempleado__idempleado']
        }

        empleados.append(contrato_data)
        
    return render(request, 'companies/loginweb.html' , {'empleados': empleados} )
