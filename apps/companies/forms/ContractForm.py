# Django
from django import forms
from django.urls import reverse

# Models 784512325698
from apps.common.models import (
    Cargos,
    Centrotrabajo,
    Tipodenomina,
    Ciudades,
    Tipocontrato,
    ModelosContratos,
    Tiposalario,
    Bancos,
    Costos,
    Subcostos,
    Entidadessegsocial,
    Sedes,
    Tiposdecotizantes,
    Subtipocotizantes,
    Contratosemp
)

# Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML




ModalidadSalario = (
    ('', '----------'),
    ('1', 'Variable'),
    ('2', 'Fijo'),
    ('3', 'Mixto'),
)

FormaPago = (
    ('', '----------'),
    ('1', 'Abono a cuenta'),
    ('2', 'Cheque'),
    ('3', 'Efectivo'),
    ('4', 'Transferencia electrónica'),
)


Cercania = (
    ('', '----------'),
    (True, 'Si'),
    (False, 'No'),
)

TipoCcuenta = [
    ('', '----------'),
    ('ahorros', 'Ahorros'),
    ('corriente', 'Corriente'),
]

#forms.ChoiceField(choices=[('', '----------')] + [(documento.codigo, documento.documento) for documento in Tipodocumento.objects.all()], label='Tipo de documento de identidad ')


class ContractForm(forms.Form):
    
    
    def clean(self):
        cleaned_data = super().clean()
        payrollAccount = cleaned_data.get('payrollAccount')
        if payrollAccount:
            try:
                float(payrollAccount)
            except ValueError:
                self.add_error('payrollAccount', 'El salario debe ser un número válido (entero o flotante).')
        return cleaned_data
    
                
                
    def __init__(self, *args, **kwargs):
        idempresa = kwargs.pop('idempresa', None)
        empleado_actual = kwargs.pop('empleado_actual', None)
        super(ContractForm, self).__init__(*args, **kwargs)   
        
        
        self.fields['name'] = forms.ChoiceField(
            choices=[('', '----------')] + [(employee.idempleado, f" {employee.pnombre} {employee.papellido} " ) for employee in Contratosemp.objects.filter(estadocontrato=4 , id_empresa__idempresa = idempresa )], 
            label='Empleado' ,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
                'data-dropdown-parent':"#contractModal",
            }), 
            required=False )
        
        if empleado_actual:
            self.fields['name'].initial = empleado_actual
            
            
        self.fields['endDate'] = forms.DateField(label='Fecha de Terminación', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
        
        self.fields['payrollType'] = forms.ChoiceField(
            choices=[('', '----------')] + [(nomina.idtiponomina, nomina.tipodenomina) for nomina in Tipodenomina.objects.all().exclude(idtiponomina=13).order_by('idtiponomina') ], 
            label='Tipo de Nómina' ,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-tags': 'true',
                'class': 'form-select',
                'data-hide-search': 'true',
                'data-dropdown-parent':"#contractModal",
            }), 
            required=False )
        
        self.fields['position'] = forms.ChoiceField(
            choices=[('', '----------')] + [(cargo.idcargo, cargo.nombrecargo) for cargo in Cargos.objects.filter(id_empresa__idempresa =  idempresa ).exclude(idcargo=93).order_by('nombrecargo') ], 
            label='Cargo', required=True ,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }), 
            )
        
        self.fields['contributor'] = forms.ChoiceField(
            choices=[('', '----------')] + [(cotizante.tipocotizante,f"{cotizante.tipocotizante} - {cotizante.descripcioncot}"   ) for cotizante in Tiposdecotizantes.objects.all().exclude(tipocotizante=52).order_by('tipocotizante')], 
            label='Tipo de Cotizante' , 
            required=True ,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            )
        
        self.fields['subContributor'] = forms.ChoiceField(
            choices=[('', '----------')] + [(subtipo.subtipocotizante, f"{subtipo.subtipocotizante} - {subtipo.descripcion}"   ) for subtipo in Subtipocotizantes.objects.all().order_by('descripcion')], 
            label='Subtipo de Cotizante' , 
            required=True ,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            )
        
        
        self.fields['workLocation'] = forms.ChoiceField(
            choices=[('', '----------')] + [(ciudad.idciudad,  f"{ciudad.ciudad} - {ciudad.departamento}" ) for ciudad in Ciudades.objects.all().exclude(idciudad=1122).order_by('ciudad')], 
            label='Lugar de trabajo' , 
            required = True ,
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }),
            )
        
        self.fields['contractStartDate'] = forms.DateField(label='Fecha de inicio de contrato', required=True, widget=forms.DateInput(attrs={'type': 'date'})) 
        
        self.fields['contractType'] = forms.ChoiceField(
            choices=[('', '----------')] + [(contrato.idtipocontrato, contrato.tipocontrato) for contrato in Tipocontrato.objects.all().exclude(idtipocontrato=7).order_by('-tipocontrato')], 
            label='Tipo de Contrato',
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=True)
        self.fields['contractModel'] = forms.ChoiceField(
            choices=[('', '----------')] + [(modelo.idmodelo, modelo.nombremodelo) for modelo in ModelosContratos.objects.all().exclude(idmodelo = 3).order_by('nombremodelo')], 
            label='Modelo de Contrato',
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }))
        self.fields['salary'] = forms.CharField(label='Salario', max_length=100, required=True)   
        self.fields['salaryType'] = forms.ChoiceField(
            choices=[('', '----------')] + [(salario.idtiposalario, salario.tiposalario) for salario in Tiposalario.objects.all().order_by('tiposalario')], 
            label='Tipo Salario', 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=True ) 
        self.fields['salaryMode'] = forms.ChoiceField(
            label='Modalidad Salario', 
            choices=ModalidadSalario, 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=True)
        self.fields['livingPlace'] = forms.ChoiceField(
            label='Vive en el lugar de trabajo', 
            choices=Cercania, 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }))
        
        self.fields['paymentMethod'] = forms.ChoiceField(
            label='Forma de pago', 
            choices=FormaPago, 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=False)
        self.fields['bankAccount'] = forms.ChoiceField(
            choices=[('', '----------')] + [(banco.idbanco, banco.nombanco) for banco in Bancos.objects.all().exclude(idbanco=27).order_by('nombanco')], 
            label='Banco de la Cuenta', 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }), )
        self.fields['accountType'] = forms.ChoiceField(
            label='Tipo de Cuenta', 
            choices=TipoCcuenta, 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=False)                                     
        self.fields['payrollAccount'] = forms.CharField(label='Cuenta de Nómina', max_length=100, required=False)    
        self.fields['costCenter'] = forms.ChoiceField(
            choices=[('', '----------')] + [(costo.idcosto, costo.nomcosto) for costo in Costos.objects.filter(id_empresa__idempresa =  idempresa ).exclude(grupocontable ='0').order_by('nomcosto')], 
            label='Centro de Costos', 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=True)
        self.fields['subCostCenter'] = forms.ChoiceField(
            choices=[('', '----------')] + [(subcosto.idsubcosto, subcosto.nomsubcosto) for subcosto in Subcostos.objects.filter(id_empresa__idempresa =  idempresa ).exclude(sufisubcosto='0').order_by('nomsubcosto')], 
            label='Sub centro de Costos', 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=False)
        self.fields['eps'] = forms.ChoiceField(
            choices=[('', '----------')] + [(entidad.identidad, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='EPS').order_by('entidad')],
            label='Eps',
            required=True , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }),) 
        self.fields['pensionFund'] = forms.ChoiceField(
            choices=[('', '----------')] + [(entidad.identidad, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='AFP').order_by('entidad')], 
            label='Pension', required=True , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }),) 
        self.fields['CesanFund'] = forms.ChoiceField(
            choices=[('', '----------')] + [(entidad.identidad, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='AFP').order_by('entidad')], 
            label='Fondo Cesantias', 
            required=True , 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-dropdown-parent':"#contractModal",
                }),) 
        self.fields['workPlace'] = forms.ChoiceField(
            choices=[('', '----------')] + [(sede.idsede, sede.nombresede) for sede in Sedes.objects.filter(id_empresa__idempresa =  idempresa ).exclude(codccf='0').order_by('nombresede')], 
            label='Sede de Trabajo',
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }), 
            required=True)
        self.fields['arlWorkCenter'] = forms.ChoiceField(
            choices=[('', '----------')] + [(centro.centrotrabajo, centro.nombrecentrotrabajo) for centro in Centrotrabajo.objects.filter(id_empresa__idempresa =  idempresa ).exclude(centrotrabajo=11 ).order_by('nombrecentrotrabajo')], 
            label='Centro de Trabajo ARL', 
            widget=forms.Select(attrs={
                    'data-control': 'select2',
                    'data-tags': 'true',
                    'class': 'form-select',
                    'data-hide-search': 'true',
                    'data-dropdown-parent':"#contractModal",
                }),
            required=True)
        
        
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'container'
        self.helper.form_id = 'form_Contract'
        self.helper.enctype = 'multipart/form-data'
        #self.helper.form_action = reverse('companies:hiring_contract' , kwargs={'idempleado': empleado_actual})
        #url = reverse('companies:hiring_contract', kwargs={'contract_id': empleado_id})

        
        self.helper.attrs.update({
            'hx-post': reverse('companies:hiring_contract' , kwargs={'idempleado': empleado_actual}),  # Usa el nombre de la vista en urls.py
            'hx-target': '#modal-container',  # El elemento donde se actualizará el contenido
            'hx-swap': 'innerHTML',  # Cómo se actualizará el contenido del objetivo
        })
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col' ),
                css_class='row'
            ),
            HTML('<h3>Contrato</h3>'),
            Div(
                Div('contractType', css_class='col' ),
                Div('payrollType', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('position', css_class='col'),
                Div('workLocation', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('contractStartDate', css_class='col'),
                Div('endDate', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('contractModel', css_class='col'),
                css_class='row'
            ),

            HTML('<h3>Compensación</h3>'),
            # compenasion 
            Div(
                Div('salary', css_class='col'),
                Div('salaryType', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('salaryMode', css_class='col'),
                Div('livingPlace', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('paymentMethod', css_class='col'),
                Div('bankAccount', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('accountType', css_class='col'),
                Div('payrollAccount', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('costCenter', css_class='col'),
                Div('subCostCenter', css_class='col'),
                css_class='row'
            ),
            
            HTML('<h3>Seguridad Social</h3>'),
            
            Div(
                Div('eps', css_class='col'),
                Div('pensionFund', css_class='col'),
                css_class='row'
            ),
            
            
            Div(
                Div('CesanFund', css_class='col'),
                Div('arlWorkCenter', css_class='col'),
                css_class='row'
            ),
            
            Div(
                Div('workPlace', css_class='col'),
                #Div('arlWorkCenter', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('contributor', css_class='col'),
                #Div('arlWorkCenter', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('subContributor', css_class='col'),
                #Div('arlWorkCenter', css_class='col'),
                css_class='row'
            ),
        )
        
        
        