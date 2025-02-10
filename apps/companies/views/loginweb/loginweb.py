from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common.models import Contratos, Contratosemp
from apps.components.mail import send_template_email
from apps.common.models import User, Empresa
from django.contrib.auth.hashers import make_password
import random
import string
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


def create_user_and_usuario(email, pnombre, papellido, password, empresa, id_empleado):
    try:
        empresa = Empresa.objects.get( idempresa = empresa )
        
        empleado = Contratosemp.objects.get(idempleado = id_empleado) 
        
        user = User.objects.create(
            first_name=pnombre,
            last_name=papellido,
            email=email,
            tipo_user = 'employee',
            id_empresa = empresa ,
            rol = Role.objects.get(id = 1),
            password=password,
            id_empleado = empleado,
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        user.save()
        print(user)
        return True, user
    except Exception as e:
        print(e)
        return False, None 

@login_required
@role_required('company')
def loginweb(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    if request.method == 'POST':
        
        selected_ids = request.POST.getlist('selected_ids')
        
        if selected_ids:
            for selected in selected_ids:
                try:
                    usertempo = Contratosemp.objects.get(idempleado = int(selected))
                    usuario = User.objects.get(id_empleado = int(selected))
                    
                except Contratosemp.DoesNotExist:
                    messages.error(request, "No se encontró el empleado con ID seleccionado.")
                    return redirect('companies:loginweb')
                except User.DoesNotExist:
                    usuario = None
                passwordoriginal = generate_random_password()
                password = make_password(passwordoriginal)
                
                if usuario:
                    usuario.password = password
                    usuario.save()
                    
                else:
                    try:
                        empresa = Empresa.objects.get( idempresa = usertempo.id_empresa.idempresa )
                        success, user  = create_user_and_usuario(usertempo.email, usertempo.pnombre, usertempo.papellido, password, empresa.idempresa, usertempo.idempleado)
                        if not success:
                            messages.error(request,"Error al crear el usuario.")
                    except Empresa.DoesNotExist:
                        messages.error(request, "No se encontró la empresa.")
                        return redirect('companies:loginweb')
                    except Exception as e:
                        messages.error(request, f"Error al crear el usuario: {e}")
                        return redirect('companies:loginweb')

                email_type = 'loginweb'
                context = {
                    'nombre_usuario': usertempo.pnombre,
                    'usuario': usertempo.email,
                    'contrasena': passwordoriginal,
                }
                subject = '¡Bienvenido a Nomiweb! Tu nueva plataforma de nóminas... ¡y tu mejor amigo!'
                recipient_list = ['mikepruebas@yopmail.com','manuel.david.13.b@gmail.com']
                #recipient_list = [usertempo.email,'manuel.david.13.b@gmail.com']

                if send_template_email(email_type, context, subject, recipient_list):
                    messages.success(request, 'Los usuarios han sido enviados correctamente.')
                else:
                    messages.error(request, 'Todo lo que podria salir mal, salio mal')
                    return redirect('companies:loginweb')
                
        messages.success(request, 'Los usuarios han sido enviados correctamente.')
        return redirect('companies:loginweb')
                
    
    empleados = []
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1,id_empresa_id =  idempresa) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'cargo__nombrecargo', 'idempleado__idempleado','idempleado__email',)

    for contrato in contratos_empleados:
        nombre_empleado = ' '.join(filter(None, [
            contrato['idempleado__papellido'],
            contrato.get('idempleado__sapellido', ''),  # Evita KeyError si no existe
            contrato['idempleado__pnombre'],
            contrato.get('idempleado__snombre', '')  # También protege este campo
        ]))

        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'cargo': contrato['cargo__nombrecargo'],
            'email': contrato['idempleado__email'],
            'idempleado': contrato['idempleado__idempleado']
        }
        empleados.append(contrato_data)

    return render(request, 'companies/loginweb.html', {'empleados': empleados})
