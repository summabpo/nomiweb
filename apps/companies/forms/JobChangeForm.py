from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.core.exceptions import ValidationError
from datetime import timedelta , datetime
from apps.common.models  import Contratos,Cargos
from django.urls import reverse
import os
from django.core.cache import cache
from django.db import models
from dateutil.relativedelta import relativedelta

class JobChangeForm(forms.Form):
    
    
    def __init__(self, *args, **kwargs):
        # Obtener la variable externa pasada al formulario
        idempresa = kwargs.pop('idempresa', None)
        
        super().__init__(*args, **kwargs)


        
        self.fields['contract'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcontrato'], f"{item['idempleado__papellido']} {item['idempleado__pnombre']} - {item['cargo__nombrecargo']} - Contrato #{item['idcontrato']} ")
                for item in Contratos.objects.filter(estadocontrato=1 ,  id_empresa = idempresa ).exclude( tipocontrato__idtipocontrato__in = [5,6] )
                .order_by('idempleado__papellido') 
                .values('idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido', 'idcontrato','cargo__nombrecargo')
            ],
            label="Contrato" , 
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un Contrato',
                'class': 'form-select'
                
            })
        )
        
        
        self.fields['position_oll'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcargo'], f"{item['nombrecargo']}")
                for item in Cargos.objects.filter(id_empresa = idempresa )
                .order_by('nombrecargo') 
                .values('nombrecargo','idcargo')
            ],
            required=False,
            label="Cargo actual" , 
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Cargo Anterior',
                'class': 'form-select'
                
            })
        )
        
        
        self.fields['position_new'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['idcargo'], f"{item['nombrecargo']}")
                for item in Cargos.objects.filter(id_empresa = idempresa )
                .order_by('nombrecargo') 
                .values('nombrecargo','idcargo')
            ],
            label="Cargo Nuevo" , 
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un nuevo Cargo',
                'class': 'form-select'
                
            })
        )

        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_disablities'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('companies:disabilities_modal'),
            'up-accept-location': reverse('companies:disabilities'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
    
        
                
                
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('position_oll', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('position_new', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            
            
        )
    
    

