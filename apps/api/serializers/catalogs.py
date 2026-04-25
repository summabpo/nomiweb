from rest_framework import serializers
from apps.common.models import (
    Ciudades, Bancos, Tipodocumento, Entidadessegsocial,
    Tipocontrato, Tipodenomina, Tiposalario,
    Tiposdecotizantes, Subtipocotizantes, Tipoavacaus,
    Cargos, Costos, Sedes, Centrotrabajo,
)


class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudades
        fields = ['idciudad', 'ciudad', 'codciudad', 'departamento', 'coddepartamento']
        read_only_fields = fields


class BancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bancos
        fields = ['idbanco', 'nombanco', 'codbanco', 'codach', 'nitbanco']
        read_only_fields = fields


class TipodocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipodocumento
        fields = ['id_tipo_doc', 'documento', 'codigo', 'cod_dian']
        read_only_fields = fields


class EntidadSegSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entidadessegsocial
        fields = ['identidad', 'codigo', 'nit', 'entidad', 'tipoentidad', 'codsgp']
        read_only_fields = fields


class TipocontratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipocontrato
        fields = ['idtipocontrato', 'tipocontrato', 'cod_dian']
        read_only_fields = fields


class TipodenominaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipodenomina
        fields = ['idtiponomina', 'tipodenomina', 'cod_dian']
        read_only_fields = fields


class TiposalarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tiposalario
        fields = ['idtiposalario', 'tiposalario']
        read_only_fields = fields


class TiposdecotizantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tiposdecotizantes
        fields = ['tipocotizante', 'descripcioncot', 'codplanilla']
        read_only_fields = fields


class SubtipocotizantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtipocotizantes
        fields = ['subtipocotizante', 'descripcion', 'codplanilla']
        read_only_fields = fields


class TipoavacausSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipoavacaus
        fields = ['idvac', 'nombrevacaus']
        read_only_fields = fields


class CargosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargos
        fields = ['idcargo', 'nombrecargo', 'estado', 'id_empresa', 'nombrenivel']
        read_only_fields = fields


class CostosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Costos
        fields = ['idcosto', 'nomcosto', 'grupocontable', 'suficosto', 'id_empresa']
        read_only_fields = fields


class SedesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sedes
        fields = ['idsede', 'nombresede', 'cajacompensacion', 'codccf', 'id_empresa']
        read_only_fields = fields


class CentrotrabajoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centrotrabajo
        fields = [
            'centrotrabajo', 'nombrecentrotrabajo', 'tarifaarl',
            'actividad_economica_arl', 'codigo_operador', 'id_empresa',
        ]
        read_only_fields = fields
