from rest_framework import serializers
from apps.common.models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    ciudad_detail = serializers.SerializerMethodField()
    arl_detail = serializers.SerializerMethodField()

    class Meta:
        model = Empresa
        fields = [
            'idempresa', 'nit', 'dv', 'nombreempresa',
            'tipodoc', 'replegal',
            'tipo_persona', 'naturaleza_juridica',
            'tipo_identificacion_rep_legal', 'numero_identificacion_rep_legal',
            'papellido_rep_legal', 'sapellido_rep_legal',
            'pnombre_rep_legal', 'snombre_rep_legal',
            'direccionempresa', 'telefono', 'email',
            'idciudad', 'ciudad_detail',
            'contactonomina', 'emailnomina',
            'contactorrhh', 'emailrrhh',
            'contactocontab', 'emailcontab',
            'cargocertificaciones',
            'website', 'logo',
            'realizarparafiscales', 'vstccf', 'vstsenaicbf',
            'ige100', 'slntarifapension', 'empresa_exonerada',
            'banco', 'numcuenta', 'tipocuenta',
            'codigosuc', 'nombresuc',
            'codigo_sucursal', 'nombre_sucursal',
            'claseaportante', 'tipoaportante',
            'ajustarnovedad', 'tipo_presentacion_planilla',
            'arl', 'arl_detail',
        ]
        read_only_fields = fields

    def get_ciudad_detail(self, obj):
        if obj.idciudad:
            return {
                'id': obj.idciudad.pk,
                'ciudad': obj.idciudad.ciudad,
                'codciudad': obj.idciudad.codciudad,
                'departamento': obj.idciudad.departamento,
            }
        return None

    def get_arl_detail(self, obj):
        if obj.arl:
            return {
                'id': obj.arl.pk,
                'entidad': obj.arl.entidad,
                'codigo': obj.arl.codigo,
                'tipoentidad': obj.arl.tipoentidad,
            }
        return None
