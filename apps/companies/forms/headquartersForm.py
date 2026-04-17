from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.common.models  import Entidadessegsocial
from django.urls import reverse



class headquartersForm(forms.Form):
    nombresede = forms.CharField(label='Nombre de la Sede' , required=True ,widget=forms.TextInput(attrs={'placeholder': 'Nombre de la Sede'}))
    
    def __init__(self, *args, **kwargs):
        modo = kwargs.pop('modo', 0)
        idsede = kwargs.pop('idsede', None)
        super().__init__(*args, **kwargs)
        
        self.fields['cajacompensacion'] = forms.ChoiceField(choices=[('', '----------')] + [(entidad.codigo, entidad.entidad) for entidad in Entidadessegsocial.objects.filter(tipoentidad='CCF').order_by('entidad')], label='Caja de Compensación Familiar' , required=True , widget=forms.Select(attrs={'data-control': 'select2'}) )
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_headquarters'
        self.helper.enctype = 'multipart/form-data'
        
        if modo == 1 :
            submit_url = reverse('companies:headquarters_modal_edit', args=[idsede])
        else:
            submit_url = reverse('companies:headquarters_modal')

        
        # Configurar la apariencia del campo nivelcargo
        self.fields['cajacompensacion'].widget.attrs.update({
            'data-control': 'select2',
            'data-placeholder': 'Seleccione una caja de compensación familiar',
            'data-allow-clear': "true",
        })
        

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_sede'
        self.helper.enctype = 'multipart/form-data'

        self.helper.attrs.update({
            'up-target': '#modal-content',
            'up-mode': 'replace',
            'up-layer': 'current',  # Clave para resolver el error
            'up-submit': submit_url,
            'up-accept-location': submit_url,
            'up-on-accepted': 'up.modal.close()',  # Cierra el modal al aceptar
        })
        
        self.helper.layout = Layout(
            Row(
                Column('nombresede', css_class='form-group mb-0'),
                Column('cajacompensacion', css_class='form-group mb-0'),
                css_class='row'
            ),
        )
    