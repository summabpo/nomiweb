from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.components.decorators import role_required
from apps.common.models import Crearnomina , Tipodenomina ,Subcostos,Costos,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
from apps.components.humani import format_value
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ConceptoForm(forms.Form):
    Concepto = forms.ChoiceField(
        label='Conceptos',
        choices=[],  # Se define dinámicamente en el método `__init__`
        required=False
    )
    cantidad = forms.CharField(
        label='Cantidad',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': ''
        })
    )
    valor = forms.IntegerField(
        label='Valor',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': ''
        })
    )
    
    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)  # Obtener `idempresa` del contexto si se pasa
        super().__init__(*args, **kwargs)
        
        # Configurar dinámicamente las opciones del campo 'Concepto'
        self.fields['Concepto'].choices = [('', '----------')] + [
            (concept.idconcepto, f"{concept.codigo} - {concept.nombreconcepto}")
            for concept in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo')
        ]
        
        
        self.fields['Concepto'] = forms.ChoiceField(
            choices=[('', '----------')] + [
            (concept.idconcepto, f"{concept.codigo} - {concept.nombreconcepto}")
            for concept in Conceptosdenomina.objects.filter(id_empresa_id=idempresa).order_by('codigo')], 
            
            label='Conceptos' ,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
                'data-hide-search': 'true',
                'data-dropdown-parent': "#kt_modal_concept",
            }), 
            required=False )
        
        
        # Configuración de Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'

        # Diseño del formulario con Crispy Forms
        self.helper.layout = Layout(
            Row(
                Column('Concepto', css_class='form-group col-md-6 mb-3'),
                Column('cantidad', css_class='form-group col-md-3 mb-3'),
                Column('valor', css_class='form-group col-md-3 mb-3'),
                css_class='row'
            ),
        )
    

@login_required
@role_required('accountant')
def pruebas(request,id,idnomina):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    # Optimizar consulta del contrato
    forms = []
    data = {}

    #try:
    contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)
    empleado = contrato.idempleado
    nombre_completo = " ".join(filter(None, [empleado.papellido, empleado.sapellido, empleado.pnombre, empleado.snombre]))
            # Optimizar consultas con select_related
    conceptos = Nomina.objects.filter(
        idnomina__idnomina=idnomina,
        idcontrato__idcontrato=id
    ).select_related('idcontrato')

    # Verificar si hay conceptos encontrados
    if not conceptos.exists():
        return JsonResponse({"error": "No se encontraron conceptos para este empleado y nómina"}, status=404)

    forms = [ConceptoForm(idempresa = idempresa), ConceptoForm(idempresa = idempresa), ConceptoForm(idempresa = idempresa)]
    # Optimizar consulta del contrato
    contrato = Contratos.objects.select_related('idempleado').get(idcontrato=id)

    # Estructurar los datos para la respuesta
    conceptos_data = [
        {   
            "codigo": concepto.idregistronom ,
            "id": concepto.idconcepto.idconcepto,
            "amount": concepto.cantidad,
            "value": concepto.valor ,
        }
        
        # Crear un formulario para cada concept
        for concepto in conceptos
    ]

    
    # Construir el nombre completo
    empleado = contrato.idempleado
    nombre_completo = " ".join(filter(None, [empleado.papellido, empleado.sapellido, empleado.pnombre, empleado.snombre]))

    # Respuesta estructurada
    data = {
        
        "nombre": nombre_completo,
        "salario": f"${format_value(contrato.salario)}",
        "conceptos": conceptos_data,
    }
    return render(request, 'payroll/partials/payrollmodal.html', {'data': data,'forms': forms})

    # except Exception as e:
    #     return render(request, 'payroll/partials/payrollmodal.html', {'data': data})