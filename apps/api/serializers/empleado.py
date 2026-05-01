from rest_framework import serializers
from apps.common.models import Contratosemp


class ContratosempSerializer(serializers.ModelSerializer):
    tipodocident_codigo = serializers.SerializerMethodField()
    ciudadnacimiento_cod = serializers.SerializerMethodField()
    ciudadresidencia_cod = serializers.SerializerMethodField()
    ciudadexpedicion_cod = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Contratosemp
        fields = [
            'idempleado',
            'docidentidad', 'tipodocident', 'tipodocident_codigo',
            'pnombre', 'snombre', 'papellido', 'sapellido',
            'email', 'telefonoempleado', 'celular', 'direccionempleado',
            'sexo', 'fechanac', 'estadocivil',
            'ciudadnacimiento', 'ciudadnacimiento_cod',
            'paisnacimiento',
            'ciudadresidencia', 'ciudadresidencia_cod',
            'paisresidencia',
            'profesion', 'niveleducativo',
            'estatura', 'peso', 'gruposanguineo',
            'fechaexpedicion',
            'ciudadexpedicion', 'ciudadexpedicion_cod',
            'formatohv',
            'dotpantalon', 'dotcamisa', 'dotzapatos',
            'estadocontrato', 'estrato', 'numlibretamil',
            'fotografiaempleado',
            'id_empresa', 'empresa_nombre',
            'contact_name', 'contact_cell_phone', 'contact_relationship',
        ]

    def get_tipodocident_codigo(self, obj):
        if obj.tipodocident:
            return obj.tipodocident.codigo
        return None

    def get_ciudadnacimiento_cod(self, obj):
        if obj.ciudadnacimiento:
            return obj.ciudadnacimiento.codciudad
        return None

    def get_ciudadresidencia_cod(self, obj):
        if obj.ciudadresidencia:
            return obj.ciudadresidencia.codciudad
        return None

    def get_ciudadexpedicion_cod(self, obj):
        if obj.ciudadexpedicion:
            return obj.ciudadexpedicion.codciudad
        return None

    def get_empresa_nombre(self, obj):
        if obj.id_empresa:
            return obj.id_empresa.nombreempresa
        return None
