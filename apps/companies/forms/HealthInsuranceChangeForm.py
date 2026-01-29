from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.core.exceptions import ValidationError
from datetime import timedelta , datetime
from apps.common.models  import Contratos,Entidadessegsocial
from django.urls import reverse
import os
from django.core.cache import cache
from django.db import models
from dateutil.relativedelta import relativedelta

class HealthInsuranceChangeForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()

        eps_old = cleaned_data.get('eps_oll')
        eps_new = cleaned_data.get('eps_new')

        # Validar que ambos estén seleccionados
        if eps_old and eps_new:
            if eps_old == eps_new:
                raise ValidationError({
                    'eps_new': 'El cargo nuevo no puede ser igual al cargo actual.'
                })

        return cleaned_data

    
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
        
        
        self.fields['eps_oll'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['identidad'], f"{item['entidad']}")
                for item in Entidadessegsocial.objects.filter(tipoentidad = 'EPS' )
                .order_by('entidad') 
                .values('entidad','identidad')
            ],
            required=False,
            label="Eps Anterior" , 
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Eps Anterior',
                'class': 'form-select'
                
            })
        )
        
        
        self.fields['eps_new'] = forms.ChoiceField(
            choices=[('', '----------')] + [
                (item['identidad'], f"{item['entidad']}")
                for item in Entidadessegsocial.objects.filter(tipoentidad = 'EPS' )
                .order_by('entidad') 
                .values('entidad','identidad')
            ],
            label="Eps Nuevo" , 
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'data-placeholder': 'Seleccione un nueva Eps',
                'class': 'form-select'
                
            })
        )

        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_eps'
        self.helper.enctype = 'multipart/form-data'
        
        
        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': reverse('companies:health_insurance_change_add'),
            'up-accept-location': reverse('companies:health_insurance_change_add'),
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
    
        
                
                
        self.helper.layout = Layout(
            Row(
                Column('contract', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('eps_oll', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('eps_new', css_class=' form-group col-md-12 mb-3'),
                css_class='row'
            ),
            
            
        )
    
    

