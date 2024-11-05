from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common.models import Contratos, Contratosemp
from apps.components.mail import send_template_email
from apps.common.models import User
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
        user = User.objects.create(
            username=email,
            first_name=pnombre,
            last_name=papellido,
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False,
            is_active=True
        )

        usuario = Usuario.objects.create(
            user=user,
            role='employees',
            company=empresa,
            permission='none',
            id_empleado=id_empleado
        )
        return True, user, usuario
    except Exception as e:
        return False, None, None

@login_required
@role_required('company')
def loginweb(request):
    db_name = request.session.get('usuario', {}).get('db')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids')
        if selected_ids:
            for selected in selected_ids:
                try:
                    usertempo = Contratosemp.objects.get(idempleado = selected)
                    usuario = Usuario.objects.get(id_empleado=usertempo.idempleado)
                except Contratosemp.DoesNotExist:
                    messages.error(request, "No se encontró el empleado con ID seleccionado.")
                    continue
                except Usuario.DoesNotExist:
                    usuario = None

                passwordoriginal = generate_random_password()
                password = make_password(passwordoriginal)

                if usuario:
                    usuario.user.password = password
                    usuario.user.save()
                else:
                    try:
                        empresa = Empresa.objects.get(db_name=db_name)
                        success, user, usuario = create_user_and_usuario(usertempo.email, usertempo.pnombre, usertempo.papellido, password, empresa, usertempo.idempleado)
                        if not success:
                            raise Exception("Error al crear el usuario.")
                    except Empresa.DoesNotExist:
                        messages.error(request, "No se encontró la empresa.")
                        return redirect('companies:loginweb')
                    except Exception as e:
                        messages.error(request, f"Error al crear el usuario: {e}")
                        continue

                email_type = 'loginweb'
                context = {
                    'nombre_usuario': usertempo.pnombre,
                    'usuario': usertempo.email,
                    'contrasena': passwordoriginal,
                }
                subject = 'Activacion de Usuario'
                #recipient_list = ['mikepruebas@yopmail.com'] ## cambiar el correo por el del usuario 
                recipient_list = [usertempo.email,'mikepruebas@yopmail.com']
                
                if send_template_email(email_type, context, subject, recipient_list):
                    pass
                else:
                    messages.error(request, 'Todo lo que podria salir mal, salio mal')

            messages.success(request, 'Los usuarios han sido enviados correctamente.')
            return redirect('companies:loginweb')

    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'cargo', 'idempleado__idempleado','idempleado__email',)

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'cargo': contrato['cargo'],
            'email': contrato['idempleado__email'],
            'idempleado': contrato['idempleado__idempleado']
        }
        empleados.append(contrato_data)

    return render(request, 'companies/loginweb.html', {'empleados': empleados})
